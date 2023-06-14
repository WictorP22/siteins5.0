from googleapiclient.discovery import build
from datetime import datetime

Key = "AIzaSyDJMPIX2CuoHD1U6XSHUEzxXTcUd0dBdrU"  # Replace with your API key.

BlogID = "5826046378587679340"  # Replace with your BlogId here.

Roles = ["CSGO", "Garry's Mod", "GTA 5"]  # Add your server roles here.

blog = build("blogger", "v3", developerKey=Key)

def anuncios_blogger():
    posts = blog.posts().list(blogId=BlogID).execute()
    retorno = []
    for post in posts['items']:
        if ((post['labels'][0] == 'anuncio') or (post['labels'][0] == 'rápido') or (post['labels'][0] == 'ata')):
            publicado = post['updated'][0:19]
            data = datetime.strptime(publicado, '%Y-%m-%dT%H:%M:%S')
            retorno.append ({
                "Id": post['id'],
                "Title": post['title'],
                "Atualização": data,
                "Corpo": post['content'],
                "Tipo": post['labels'][0]
            })
    return retorno

def busca_anuncio(id):
    posts = blog.posts().list(blogId=BlogID).execute()
    for post in posts['items']:
        if post['id'] == id:
            publicado = post['updated'][0:19]
            data = datetime.strptime(publicado, '%Y-%m-%dT%H:%M:%S')
            return {
                "Id": post['id'],
                "Title": post['title'],
                "Atualização": data,
                "Corpo": post['content'],
                "Tipo": post['labels'][0]
            }
    return retorno

def busca_scripts():
    posts = blog.posts().list(blogId=BlogID).execute()
    retorno = []
    for post in posts['items']:
        if 'script' in post['labels']:
            if 'primary' in post['labels']:
                cor = 'primary'
            elif 'warning' in post['labels']:
                cor = 'warning'
            elif 'danger' in post['labels']:
                cor = 'danger'
            elif 'info' in post['labels']:
                cor = 'info'
            else:
                cor = 'light'
            if len(post['labels']) == 2:
                publicado = post['updated'][0:19]
                data = datetime.strptime(publicado, '%Y-%m-%dT%H:%M:%S')
                retorno.append({
                    "Id": post['id'],
                    "Title": post['title'],
                    "Atualização": post['updated'],
                    "Corpo": post['content'],
                    "Tipo": post['labels'][0],
                    "Cor": cor
                })
            else:
                print(post['labels'])
    return retorno

def busca_script(id):
    posts = blog.posts().list(blogId=BlogID).execute()
    for post in posts['items']:
        if post['id'] == id:
            if 'primary' in post['labels']:
                cor = 'primary'
            elif 'warning' in post['labels']:
                cor = 'warning'
            elif 'danger' in post['labels']:
                cor = 'danger'
            elif 'info' in post['labels']:
                cor = 'info'
            else:
                cor = 'light'
            publicado = post['updated'][0:19]
            return {
                "Id": post['id'],
                "Title": post['title'],
                "Atualização": post['updated'],
                "Corpo": post['content'],
                "Tipo": post['labels'][0],
                "Cor": cor
            }