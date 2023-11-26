import requests
from bs4 import BeautifulSoup
from lxml import etree

def get_game_description(game_url):
    try:
        response = requests.get(game_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
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
                image_url = image['src']
                jpg_end_index = image_url.find('.jpg') + 4
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
    rss = etree.Element('rss', version="2.0", nsmap={'atom': "http://www.w3.org/2005/Atom", 'content': "http://purl.org/rss/1.0/modules/content/"})
    channel = etree.SubElement(rss, 'channel')

    for game_title, game_link, game_description, game_image in games_data:
        item = etree.SubElement(channel, 'item')
        title_element = etree.SubElement(item, 'title')
        title_element.text = game_title
        link_element = etree.SubElement(item, 'link')
        link_element.text = game_link
        description_element = etree.SubElement(item, 'description')
        
        if game_image:
            description_with_html = f'<img src="{game_image}" /><br/>{game_description}'
        else:
            description_with_html = game_description
        
        description_element.text = etree.CDATA(description_with_html)

    with open('docs/index.xml', 'wb') as f:
        f.write(etree.tostring(rss, pretty_print=True, xml_declaration=True, encoding='UTF-8'))



url = 'https://store.steampowered.com/explore/new/'
games_data = scrape_steam_new_releases(url)
if games_data:
    generate_rss_feed(games_data)
else:
    print("Nu s-au putut extrage datele de pe Steam.")
