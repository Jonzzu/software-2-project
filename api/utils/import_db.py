from pathlib import Path
from sqlalchemy.orm import Session
from api.database.db import engine
from api.database.models.airport import Airport
from api.database.models.country import Country


def import_sql_file_direct(sql_file_path: str) -> None:
    """
    Parse SQL dump and insert data directly using SQLAlchemy ORM.
    Simple, reliable approach without complex parsing.
    """
    sql_file = Path(sql_file_path)

    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    session = Session(engine)

    try:
        # ===== IMPORT COUNTRIES FIRST =====
        print("=" * 60)
        print("Importing countries...")

        # Split by INSERT statements
        insert_statements = sql_content.split("INSERT INTO `country`")

        countries_imported = 0
        countries_skipped = 0

        for statement_part in insert_statements[1:]:  # Skip the part before first INSERT
            # Extract just the VALUES(...) section
            if "VALUES" not in statement_part:
                continue

            values_start = statement_part.find("VALUES")
            values_section = statement_part[values_start:]

            # Find the actual data rows (between parentheses after VALUES)
            start_idx = values_section.find("(")
            end_idx = values_section.rfind(";")

            if start_idx == -1 or end_idx == -1:
                continue

            rows_str = values_section[start_idx+1:end_idx-1]  # Remove outer parens and semicolon

            # Split rows by ),(
            rows = rows_str.split("),(")

            print(f"Found {len(rows)} country rows")

            for row_str in rows:
                try:
                    # Clean up the row
                    row_str = row_str.strip()
                    if row_str.startswith("("):
                        row_str = row_str[1:]
                    if row_str.endswith(")"):
                        row_str = row_str[:-1]

                    # Parse values manually
                    values = parse_row_values(row_str)

                    # Expect: iso_country, name, continent, wikipedia_link, keywords
                    if len(values) < 3:
                        countries_skipped += 1
                        continue

                    iso_country = values[0]
                    name = values[1]
                    continent = values[2] if len(values) > 2 else "XX"

                    if not iso_country or not name:
                        countries_skipped += 1
                        continue

                    # Normalize
                    iso_country = str(iso_country).strip()[:10]
                    name = str(name).strip()[:256]
                    continent = str(continent or "XX").strip()[:2]

                    # Check if exists
                    if session.query(Country).filter_by(iso_country=iso_country).first():
                        countries_skipped += 1
                        continue

                    # Create and add
                    country = Country(
                        iso_country=iso_country,
                        name=name,
                        continent=continent
                    )
                    session.add(country)
                    countries_imported += 1

                except Exception as e:
                    countries_skipped += 1
                    continue

            session.commit()

        print(f"✓ Imported {countries_imported} countries ({countries_skipped} skipped)")

        # ===== IMPORT AIRPORTS =====
        print("\nImporting airports...")

        insert_statements = sql_content.split("INSERT INTO `airport`")

        airports_imported = 0
        airports_skipped = 0

        for statement_part in insert_statements[1:]:  # Skip the part before first INSERT
            if "VALUES" not in statement_part:
                continue

            values_start = statement_part.find("VALUES")
            values_section = statement_part[values_start:]

            start_idx = values_section.find("(")
            end_idx = values_section.rfind(";")

            if start_idx == -1 or end_idx == -1:
                continue

            rows_str = values_section[start_idx+1:end_idx-1]
            rows = rows_str.split("),(")

            print(f"Found {len(rows)} airport rows")

            for row_str in rows:
                try:
                    # Clean up
                    row_str = row_str.strip()
                    if row_str.startswith("("):
                        row_str = row_str[1:]
                    if row_str.endswith(")"):
                        row_str = row_str[:-1]

                    # Parse values
                    values = parse_row_values(row_str)

                    # Expected order from SQL: id, ident, type, name, latitude_deg, longitude_deg,
                    # elevation_ft, continent, iso_country, iso_region, municipality, ...
                    if len(values) < 11:
                        airports_skipped += 1
                        continue

                    id_val = values[0]
                    ident = values[1]
                    type_val = values[2]
                    name = values[3]
                    latitude = values[4]
                    longitude = values[5]
                    elevation = values[6]
                    continent = values[7]
                    iso_country = values[8]
                    iso_region = values[9]
                    municipality = values[10]

                    if not ident or not iso_country:
                        airports_skipped += 1
                        continue

                    # Type/name validation
                    if not type_val or type_val == "":
                        type_val = "unknown"
                    if not name or name == "":
                        name = "Unknown Airport"

                    # Numeric conversion
                    try:
                        id_val = int(id_val) if id_val else 0
                        latitude = float(latitude) if latitude else 0.0
                        longitude = float(longitude) if longitude else 0.0
                        elevation = int(elevation) if elevation else 0
                    except (ValueError, TypeError):
                        airports_skipped += 1
                        continue

                    # Normalize strings
                    ident = str(ident).strip()[:40]
                    name = str(name).strip()[:256]
                    type_val = str(type_val).strip()[:40]
                    iso_country = str(iso_country).strip()[:10]
                    continent = str(continent or "XX").strip()[:2]
                    iso_region = str(iso_region or "XX").strip()[:10]
                    municipality = str(municipality or "Unknown").strip()[:100]

                    # Check if exists
                    if session.query(Airport).filter_by(ident=ident).first():
                        airports_skipped += 1
                        continue

                    # Create and add
                    airport = Airport(
                        id=id_val,
                        ident=ident,
                        type=type_val,
                        name=name,
                        latitude_deg=latitude,
                        longitude_deg=longitude,
                        elevation_ft=elevation,
                        continent=continent,
                        iso_region=iso_region,
                        municipality=municipality,
                        iso_country=iso_country
                    )
                    session.add(airport)
                    airports_imported += 1

                    if airports_imported % 500 == 0:
                        session.commit()
                        print(f"  Progress: {airports_imported} airports imported...")

                except Exception as e:
                    airports_skipped += 1
                    continue

            session.commit()

        print(f"✓ Imported {airports_imported} airports ({airports_skipped} skipped)")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"✗ Error during import: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


def parse_row_values(row_str: str) -> list:
    """
    Parse a single SQL row into individual values.
    Handles quoted strings and commas inside them.
    """
    values = []
    current_value = ""
    in_quotes = False
    i = 0

    while i < len(row_str):
        char = row_str[i]

        # Toggle quote state
        if char == "'" and (i == 0 or row_str[i-1] != "\\"):
            in_quotes = not in_quotes
            current_value += char
        # Comma separator (only outside quotes)
        elif char == "," and not in_quotes:
            values.append(current_value.strip())
            current_value = ""
        else:
            current_value += char

        i += 1

    # Add last value
    if current_value.strip():
        values.append(current_value.strip())

    # Clean up values (remove quotes if present)
    cleaned = []
    for val in values:
        if val.startswith("'") and val.endswith("'"):
            cleaned.append(val[1:-1])
        elif val.upper() == "NULL" or val == "":
            cleaned.append(None)
        else:
            cleaned.append(val)

    return cleaned