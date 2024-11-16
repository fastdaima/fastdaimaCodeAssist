# /usr/bin/python
import os
import sys
from tree_sitter import Node
from collections import defaultdict
import subprocess
import csv
from typing import List, Dict
from tree_sitter import Node
from tree_sitter_languages import get_language, get_parser


INPUT_DIR = os.environ.get('INPUT_DIR', '/home/srk/Desktop/projects/fastdaimaCodeAssist/input')


BLACKLIST_DIR = [
    "__pycache__",
    ".pytest_cache",
    ".venv",
    ".git",
    ".idea",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".vscode",
    ".github",
    ".gitlab",
    ".angular",
    "cdk.out",
    ".aws-sam",
    ".terraform"
]
WHITELIST_FILES = [".py"]
BLACKLIST_FILES = ["docker-compose.yml"]

NODE_TYPES = {
    'python': {
        'class': 'class_definition',
        'method': 'function_definition'
    }
}

REFERENCE_IDENTIFIERS = {
    'python': {
        'class': 'identifier',
        'method': 'call',
        'child_field_name': 'function'
    }
}


def download_codebase(git_url, username, token):
    if username and token:
        base= git_url.split('https://')[-1]
        url = ['https://', username, ':', token, '@', base]
        url = ''.join(url)
    else: url = git_url

    subprocess.run(
        f'cd {INPUT_DIR}; git clone {url}', shell=True
    )

    repo_name = url.split('.git')[0].split('/')[-1]
    return f'{INPUT_DIR}/{repo_name}'


def get_files(codebase_path):
    pass


def parse_code_files(files):
    pass


def find_reference(files, class_names, method_names):
    pass


def map_references(references, class_data_map, method_data_map):
    pass


def save_data_to_file(class_data, method_data):
    pass


def return_db_data(git_url):

    files = get_files(codebase_path)
    class_data, method_data, class_names, method_names = parse_code_files(files)
    references = find_reference(files, class_names, method_names)
    class_data_map = {o['class_name']: o for o in class_data}
    method_data_map ={(o['class_name'], o['name']):o for o in method_data}
    class_data, method_data = map_references(references, class_data_map, method_data_map)
    data_file_paths = save_data_to_file(class_data, method_data)
    return data_file_paths



if __name__ == '__main__':

    git_url = 'https://github.com/python/mypy.git'
    username = None
    token = None
    '''
    git_url = input('Enter git url')
    username = input('Enter git username')
    token = input('Enter git token')
    '''
    # codebase_path = download_codebase(url, username, token)

    codebase_path = f'{INPUT_DIR}/mypy'



