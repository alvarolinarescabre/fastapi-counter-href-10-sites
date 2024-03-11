import os
import re
import shutil
import requests


def save_file(tmp_dir: str, filename: str, data: str, format: str) -> None:
    """
    Save the data to a file
    :param tmp_dir:
    :param filename:
    :param data:
    :param format:
    :return:
    """
    with open(f"{tmp_dir}/{filename}.txt", format) as file:
        file.write(data)
        print(f"Saved {filename}.txt")


def read_file(filename: str) -> str:
    """
    Read a file
    :param filename:
    :return: Content File
    """
    with open(filename, 'r') as file:
        content = file.read()
        return content


def create_dir(dir_name: str) -> None:
    """
    Create a directory
    :param dir_name:
    :return:
    """
    os.makedirs(dir_name, exist_ok=True)
    print(f"Created {dir_name}")


def delete_dir(dir_name: str) -> None:
    """
    Delete the directory
    :param temp_dir:
    :return:
    """
    shutil.rmtree(dir_name)
    print(f"Deleted {dir_name}")


def download_file(dir_name: str, url: str) -> str:
    """
    Download the file from URL
    :param url:
    :return:
    """
    response = requests.get(url)
    filename = url.split('/')
    filename = f"pre.{filename[len(filename) - 1]}"

    save_file(dir_name, filename, response.content, "wb")

    return f"{dir_name}{filename}.txt"


def search_tag(dir_name: str, filename: str, tag: str) -> str:
    """
    Search the specific tag from file
    :param filename:
    :param tag:
    :return: String with matching tags
    """
    count_word = 0

    for match in re.findall(tag, read_file(filename)):
        if match == tag:
            count_word += 1

    filename = filename.split('/')
    filename = f"post.{filename[len(filename) - 1].strip('.pre.').strip('.txt')}"
    data = f"The site: {filename.strip('.post.')} haves total of '{tag}' tags: {count_word}"
    save_file(dir_name, filename, data, "w")

    return data
