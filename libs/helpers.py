import re
import aiohttp
from conf.settings import Settings

settings = Settings()


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


def search_tag(data: str, pattern: str) -> int:
    """
    Search the specific tag from file
    :param data: str
    :param pattern: str
    :return: String with matching tags
    """
    count_word = 0

    for match in re.findall(pattern, data):
        if match:
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