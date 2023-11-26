import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def get_game_description(game_url):
    try:
        response = requests.get(game_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extrage descrierea jocului - aceasta va varia în funcție de structura paginii
            description = soup.find('div', class_='game_description_snippet')
            return description.text.strip() if description else 'Nicio descriere disponibilă'
    except Exception as e:
        return 'Eroare la extragerea descrierii: ' + str(e)

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
        games_data.append((title, game_url, description))

    return games_data

def generate_rss_feed(games_data):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    title = ET.SubElement(channel, 'title')
    title.text = 'Steam New Releases'
    description = ET.SubElement(channel, 'description')
    description.text = 'Latest game releases on Steam'

    for game_title, game_link, game_description in games_data:
        item = ET.SubElement(channel, 'item')
        title_element = ET.SubElement(item, 'title')
        title_element.text = game_title
        link_element = ET.SubElement(item, 'link')
        link_element.text = game_link
        description_element = ET.SubElement(item, 'description')
        description_element.text = game_description

    tree = ET.ElementTree(rss)
    tree.write('docs/index.xml', encoding='utf-8', xml_declaration=True)

# URL-ul paginii cu noile lansări Steam
url = 'https://store.steampowered.com/explore/new/'

# Execută scraping-ul și generează feed-ul RSS
games_data = scrape_steam_new_releases(url)
if games_data:
    generate_rss_feed(games_data)
else:
    print("Nu s-au putut extrage datele de pe Steam.")
