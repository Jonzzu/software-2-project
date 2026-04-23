import requests
import random


def get_random_anime_table():
    # Hakee 3 satunnaista animea ja palauttaa ne listana sanakirjoja.
    url = 'https://graphql.anilist.co'

    # Arvotaan sivu väliltä 1-500 (suosituimmat sarjat)
    random_page = random.randint(1, 500)

    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        media (type: ANIME, sort: POPULARITY_DESC) {
          title {
            english
            romaji
          }
          description
          averageScore
          coverImage {
            medium
          }
        }
      }
    }
    '''

    variables = {
        'page': random_page,
        'perPage': 3
    }

    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        response.raise_for_status()  # Nostaa virheen jos statuskoodi on huono

        data = response.json()['data']['Page']['media']
        anime_list = []

        for anime in data:
            # Luodaan sanakirja jokaisesta animesta
            entry = {
                "title": anime['title']['english'] or anime['title']['romaji'],
                "score": anime['averageScore'] if anime['averageScore'] is not None else "N/A",
                "description": anime['description'] or "No description available.",
                "image": anime['coverImage']['medium']
            }
            anime_list.append(entry)

        return anime_list

    except Exception as e:
        print(f"Virhe haettaessa tietoja: {e}")
        return []


# --- TESTAUSLOHKO ---
# Tämä suoritetaan vain, kun tiedosto ajetaan suoraan.
if __name__ == "__main__":
    print("Suoritetaan testi: Haetaan 3 satunnaista animea...\n")

    tulokset = get_random_anime_table()

    if tulokset:
        for i, anime in enumerate(tulokset, 1):
            print(f"{i}. {anime['title'].upper()}")
            print(f"   Pisteet: {anime['score']}")
            print(f"   Kuva:    {anime['image']}")
            # Lyhennetään kuvaus konsoliin, ettei se täyty tekstistä
            lyhyt_kuvaus = anime['description'][:100].replace('<br>', '')
            print(f"   Kuvaus:  {lyhyt_kuvaus}...\n")
            print("-" * 50)
    else:
        print("Tuloksia ei voitu hakea.")

