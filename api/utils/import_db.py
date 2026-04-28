from pathlib import Path
import re
from sqlalchemy import text
from sqlalchemy.orm import Session
from api.database.db import engine
from api.database.models.airport import Airport
from api.database.models.country import Country


def parse_insert_statement(insert_statement: str) -> dict:
    """
    Parse MySQL INSERT statement and extract values.
    
    Example:
    INSERT INTO `airport` VALUES (1,'00A','heliport','Total Rf Heliport',...)
    """
    # Extract the VALUES part
    values_match = re.search(r'VALUES\s*\((.*)\)', insert_statement, re.IGNORECASE | re.DOTALL)
    if not values_match:
        return None
    
    values_str = values_match.group(1)
    
    # Parse individual rows (each enclosed in parentheses)
    rows = []
    current_row = []
    in_quotes = False
    current_value = ""
    
    for char in values_str:
        if char == "'" and (not current_value or current_value[-1] != "\\"):
            in_quotes = not in_quotes
            current_value += char
        elif char == "," and not in_quotes:
            current_row.append(current_value.strip())
            current_value = ""
        elif char == ")" and not in_quotes:
            if current_value.strip():
                current_row.append(current_value.strip())
            if current_row:
                rows.append(current_row)
            current_row = []
            current_value = ""
        else:
            current_value += char
    
    return rows


def parse_sql_value(value: str):
    """Convert SQL value string to Python value."""
    value = value.strip()
    if value == "NULL" or value == "":
        return None
    if value.startswith("'") and value.endswith("'"):
        # Remove quotes and unescape
        return value[1:-1].replace("\\'", "'").replace('""', '"')
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            # Return None for non-numeric strings instead of the string itself
            return None


def import_sql_file_direct(sql_file_path: str) -> None:
    """
    Parse SQL dump and insert data directly using SQLAlchemy ORM.
    
    Args:
        sql_file_path: Path to the SQL file to import
    """
    sql_file = Path(sql_file_path)
    
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
    
    # Read the SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    session = Session(engine)
    
    try:
        # Find all INSERT statements for airport table
        airport_inserts = re.findall(
            r"INSERT INTO `airport`\s+VALUES\s+\((.*?)\);",
            sql_content,
            re.IGNORECASE | re.DOTALL
        )
        
        print(f"Found {len(airport_inserts)} airport INSERT statements")
        
        # Track unique countries
        countries_to_add = {}
        airports_to_add = []
        
        for insert_group in airport_inserts:
            # Parse multiple value groups in one INSERT
            # Each row is like: (id, ident, type, name, ...)
            rows = parse_insert_statement(f"INSERT INTO airport VALUES ({insert_group});")
            
            if not rows:
                continue
            
            for row in rows:
                if len(row) < 11:  # Ensure we have at least the fields we need
                    continue
                
                try:
                    # Map columns from the SQL dump to our needs
                    id_val = parse_sql_value(row[0])
                    ident = parse_sql_value(row[1])
                    type_val = parse_sql_value(row[2])
                    name = parse_sql_value(row[3])
                    latitude = parse_sql_value(row[4])
                    longitude = parse_sql_value(row[5])
                    elevation = parse_sql_value(row[6])
                    continent = parse_sql_value(row[7])
                    iso_country = parse_sql_value(row[8])
                    iso_region = parse_sql_value(row[9])
                    municipality = parse_sql_value(row[10])
                    
                    # Normalize values
                    iso_country = str(iso_country or "XX").strip()[:10]
                    continent = str(continent or "XX").strip()[:2]
                    iso_region = str(iso_region or "XX").strip()[:10]
                    
                    # Track countries
                    if iso_country not in countries_to_add:
                        countries_to_add[iso_country] = {
                            'iso_country': iso_country,
                            'name': iso_country,  # Default to code if no separate data
                            'continent': continent
                        }
                    
                    # Add airport
                    airport = {
                        'id': id_val or 0,
                        'ident': (ident or "UNKNOWN").strip()[:40],
                        'type': (type_val or "unknown").strip()[:40],
                        'name': (name or "Unknown").strip()[:256],
                        'latitude_deg': float(latitude) if latitude is not None else 0.0,
                        'longitude_deg': float(longitude) if longitude is not None else 0.0,
                        'elevation_ft': elevation if elevation is not None else 0,
                        'continent': continent,
                        'iso_region': iso_region,
                        'municipality': (municipality or "Unknown").strip()[:100],
                        'iso_country': iso_country
                    }
                    airports_to_add.append(airport)
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠ Warning parsing row: {str(e)[:50]}")
                    continue
        
        print(f"✓ Parsed {len(countries_to_add)} countries and {len(airports_to_add)} airports")
        
        # Insert countries first
        print("Inserting countries...")
        for country_data in countries_to_add.values():
            existing = session.query(Country).filter_by(iso_country=country_data['iso_country']).first()
            if not existing:
                country = Country(**country_data)
                session.add(country)
        session.commit()
        print(f"✓ Inserted {len(countries_to_add)} countries")
        
        # Insert airports
        print("Inserting airports...")
        for i, airport_data in enumerate(airports_to_add):
            existing = session.query(Airport).filter_by(ident=airport_data['ident']).first()
            if not existing:
                airport = Airport(**airport_data)
                session.add(airport)
            
            # Batch commit every 500 records
            if (i + 1) % 500 == 0:
                session.commit()
                print(f"  Progress: {i + 1}/{len(airports_to_add)} airports inserted...")
        
        session.commit()
        print(f"✓ Inserted {len(airports_to_add)} airports total")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error during import: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


def migrate_data_to_models() -> None:
    """
    Migrate data from imported tables to SQLAlchemy model tables.
    This ensures only the fields defined in your models are kept.
    """
    session = Session(engine)
    
    try:
        # Check if raw airport table has data
        count = session.execute(text("SELECT COUNT(*) FROM airport")).scalar()
        print(f"Found {count} airports in raw data")
        
        if count == 0:
            print("⚠ No data found in airport table. Check if SQL dump was imported correctly.")
            return
        
        # First, migrate countries (derive from airport data)
        print("\nMigrating countries...")
        raw_countries = session.execute(
            text("""
                SELECT DISTINCT iso_country, continent
                FROM airport 
                WHERE iso_country 
                    IS NOT NULL AND iso_country != ''
                ORDER BY iso_country
            """)
        ).fetchall()
        
        country_count = 0
        for iso_country, continent in raw_countries:
            existing = session.query(Country).filter_by(iso_country=iso_country).first()
            if not existing:
                country = Country(
                    iso_country=iso_country.strip() if iso_country else "XX",
                    name=iso_country if iso_country else "Unknown",  # Use country code as name if unavailable
                    continent=continent.strip() if continent else "XX"
                )
                session.add(country)
                country_count += 1
        
        session.commit()
        print(f"✓ Migrated {country_count} countries")
        
        # Then, migrate airports (only the fields in your model)
        print("\nMigrating airports...")
        raw_airports = session.execute(
            text("""
                SELECT id, ident, type, name, latitude_deg, longitude_deg,
                       elevation_ft, continent, iso_region, municipality, iso_country
                FROM airport
                ORDER BY ident
            """)
        ).fetchall()
        
        airport_count = 0
        for row in raw_airports:
            existing = session.query(Airport).filter_by(ident=row.ident).first()
            if not existing:
                airport = Airport(
                    id=row.id,
                    ident=row.ident.strip() if row.ident else "UNKNOWN",
                    type=row.type.strip() if row.type else "unknown",
                    name=row.name.strip() if row.name else "Unknown Airport",
                    latitude_deg=float(row.latitude_deg) if row.latitude_deg else 0.0,
                    longitude_deg=float(row.longitude_deg) if row.longitude_deg else 0.0,
                    elevation_ft=row.elevation_ft,
                    continent=row.continent.strip() if row.continent else "XX",
                    iso_region=row.iso_region.strip() if row.iso_region else "XX",
                    municipality=row.municipality.strip() if row.municipality else "Unknown",
                    iso_country=row.iso_country.strip() if row.iso_country else "XX"
                )
                session.add(airport)
                airport_count += 1
                
                # Commit in batches to avoid memory issues
                if airport_count % 1000 == 0:
                    session.commit()
                    print(f"  Progress: {airport_count} airports migrated...")
        
        session.commit()
        print(f"✓ Migrated {airport_count} airports total")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()