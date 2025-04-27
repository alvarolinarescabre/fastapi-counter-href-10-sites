import re
from conf.settings import Settings

settings = Settings()

def search_tag(filename: str, tag: str) -> str:
    """
    Search the specific tag from file
    :param tag:
    :return: String with matching tags
    """
    count_word = 0

    for match in re.findall(tag, filename):
        if match == tag:
            count_word += 1
            
    return count_word
