
# Anilist api call

import requests

url = 'https://graphql.anilist.co'
query = '''
query ($id: Int) {
   Media (id: $id) {
       id
       title {
           romaji
           english
           native
       }
       description
       coverImage
{
   large
medium
color
}
   }
}
'''
variables = {'id': 1535} # tähän vois vaikka randomilla ottaa ID:n

response = requests.post(url, json={'query': query, 'variables': variables})
print(response.json())