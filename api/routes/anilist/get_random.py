import random
import requests
import time
from typing import List, Dict


# def get_random_anime_table():
#     # Hakee 3 satunnaista animea ja palauttaa ne listana sanakirjoja.
#     url = 'https://graphql.anilist.co'
#
#     # Arvotaan sivu väliltä 1-500 (suosituimmat sarjat)
#     random_page = random.randint(1, 500)
#
#     query = '''
#     query ($page: Int, $perPage: Int) {
#       Page (page: $page, perPage: $perPage) {
#         media (type: ANIME, sort: POPULARITY_DESC) {
#           title {
#             english
#             romaji
#           }
#           description
#           averageScore
#           coverImage {
#             medium
#           }
#         }
#       }
#     }
#     '''
#
#     variables = {
#         'page': random_page,
#         'perPage': 3
#     }
#
#     try:
#         response = requests.post(url, json={'query': query, 'variables': variables})
#         response.raise_for_status()  # Nostaa virheen jos statuskoodi on huono
#
#         data = response.json()['data']['Page']['media']
#         anime_list = []
#
#         for anime in data:
#             # Luodaan sanakirja jokaisesta animesta
#             entry = {
#                 "title": anime['title']['english'] or anime['title']['romaji'],
#                 "score": anime['averageScore'] if anime['averageScore'] is not None else "N/A",
#                 "description": anime['description'] or "No description available.",
#                 "image": anime['coverImage']['medium']
#             }
#             anime_list.append(entry)
#
#         return anime_list
#
#     except Exception as e:
#         print(f"Virhe haettaessa tietoja: {e}")
#         return []


import random
import requests
from typing import List, Dict


def get_random_anime(n: int = 3) -> List[Dict]:
    """
    Gets n truly random anime with a single API request.
    Fetches a batch from a random page and samples n items from it.

    Args:
        n: Number of random anime to fetch (default: 3)

    Returns:
        List of anime dictionaries with id, title, score, description, image
    """
    url = 'https://graphql.anilist.co'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Fetch a larger batch to ensure we have enough items to sample from
    per_page = 50
    random_page = random.randint(1, 100)

    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        media (type: ANIME, sort: POPULARITY_DESC) {
          id
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

    try:
        # Add small delay to avoid rate limiting
        time.sleep(0.2)
        
        response = requests.post(
            url,
            json={'query': query, 'variables': {'page': random_page, 'perPage': per_page}},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        all_anime = response.json()['data']['Page']['media']

        if not all_anime:
            return []

        # Select n truly random anime from the fetched batch
        selected = random.sample(all_anime, min(n, len(all_anime)))

        anime_list = []
        for anime in selected:
            entry = {
                "id": anime.get('id'),
                "title": anime['title']['english'] or anime['title']['romaji'],
                "score": anime['averageScore'] if anime['averageScore'] is not None else "N/A",
                "description": anime['description'] or "No description available.",
                "image": anime['coverImage']['medium']
            }
            anime_list.append(entry)

        return anime_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching random anime: {e}")
        return []


# --- TESTAUSLOHKO ---
# Tämä suoritetaan vain, kun tiedosto ajetaan suoraan.
from flask import Blueprint, jsonify
from .get_random import get_random_anime

bp = Blueprint('anilist', __name__, url_prefix='/api/anilist')


@bp.route('/random-series', methods=['GET'])
def random_series():
    """
    Get 3 random anime series from AniList.
    Returns a list of 3 series with id, title, score, description, and image.
    """
    try:
        anime_list = get_random_anime(n=3)

        if not anime_list:
            return jsonify({'error': 'Failed to fetch random series'}), 500

        return jsonify({
            'success': True,
            'series': anime_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    print("Suoritetaan testi: Haetaan 3 satunnaista animea...\n")

    tulokset = get_random_anime()

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

