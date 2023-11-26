import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def get_game_description(game_url):
    try:
        response = requests.get(game_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extrage descrierea jocului
            description = soup.find('div', class_='game_description_snippet')
            return description.text.strip() if description else 'Nicio descriere disponibilă'
    except Exception as e:
        return 'Eroare la extragerea descrierii: ' + str(e)

def get_game_image_url(game_url):
    try:
        response = requests.get(game_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            image = soup.find('img', class_='game_header_image_full')
            if image:
                # Elimină parametrii de query de după '.jpg'
                image_url = image['src']
                jpg_end_index = image_url.find('.jpg') + 4  # '+ 4' pentru a include '.jpg'
                return image_url[:jpg_end_index] if jpg_end_index > 4 else None
            else:
                return None
    except Exception as e:
        return None

def scrape_steam_new_releases(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    new_releases = soup.find_all('a', class_='tab_item')

    games_data = []
    for game in new_releases:
        title = game.find('div', class_='tab_item_name').text
        game_url = game['href']
        description = get_game_description(game_url)
        image_url = get_game_image_url(game_url)
        games_data.append((title, game_url, description, image_url))

    return games_data

def generate_rss_feed(games_data):
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')

    rss = ET.Element('rss', xmlns_atom="http://www.w3.org/2005/Atom", xmlns_content="http://purl.org/rss/1.0/modules/content/", version="2.0")
    channel = ET.SubElement(rss, 'channel')

    # Adăugarea elementelor suplimentare (titlu, link, etc.) dacă este necesar

    for game_title, game_link, game_description, game_image in games_data:
        item = ET.SubElement(channel, 'item')
        title_element = ET.SubElement(item, 'title')
        title_element.text = game_title
        link_element = ET.SubElement(item, 'link')
        link_element.text = game_link
        description_element = ET.SubElement(item, 'description')
        description_with_image = f'<![CDATA[<img src="{game_image}" /><br/>{game_description}]]>' if game_image else f'<![CDATA[{game_description}]]'
        description_element.text = description_with_image

    tree = ET.ElementTree(rss)
    tree.write('docs/index.xml', encoding='UTF-8', xml_declaration=True)

# URL-ul paginii cu noile lansări Steam
url = 'https://store.steampowered.com/explore/new/'

# Execută scraping-ul și generează feed-ul RSS
games_data = scrape_steam_new_releases(url)
if games_data:
    generate_rss_feed(games_data)
else:
    print("Nu s-au putut extrage datele de pe Steam.")
