import re
import aiohttp
from bs4 import BeautifulSoup

from conf.settings import Settings

settings = Settings()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    return links

def search_tag(data: str, pattern: str) -> int:
    """
    Search the specific tag from file
    :param data: str
    :param pattern: str
    :return: String with matching tags
    """
    count_word = 0
    compiled = re.compile(pattern)

    for match in compiled.findall(data):
        if compiled.match(match):
            count_word += 1

    return count_word

async def return_results(url):
    """
    Return Tags from url
    :param url:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)

        return search_tag(html, settings.pattern)