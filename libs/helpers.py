import re
import aiohttp
import requests
from bs4 import BeautifulSoup

from conf.settings import Settings

settings = Settings()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all(href=True)

    return links

def search_tag(data: str, pattern: str) -> int:
    """
    Search the specific tag from file
    :param data: str
    :param pattern: str
    :return: String with matching tags
    """
    count_word = 0

    for tag in data:
        if tag:
         count_word += 1

    return count_word

async def results(url):
    """
    Return Tags from url
    :param url:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        links = parse(html)

        return search_tag(links, settings.pattern)