# /usr/bin/python
import os
import json
from pprint import pprint
import sys
from collections import defaultdict
import subprocess
import csv
from typing import List, Dict
from treesitter import Treesitter, LanguageEnum
from tree_sitter_languages import get_language, get_parser



INPUT_DIR = os.environ.get('INPUT_DIR', '/home/srk/Desktop/projects/fastdaimaCodeAssist/input')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/home/srk/Desktop/projects/fastdaimaCodeAssist/output')

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

FILE_EXTENSION_LANGUAGE_MAP = {
    # ".java": LanguageEnum.JAVA,
    ".py": LanguageEnum.PYTHON,
    # ".js": LanguageEnum.JAVASCRIPT,
    # ".rs": LanguageEnum.RUST,
    # Add other extensions and languages as needed
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
    return f'{INPUT_DIR}/{repo_name}', repo_name


def get_language_from_extension(file_ext):
    return FILE_EXTENSION_LANGUAGE_MAP.get(file_ext)


def get_files(fp):
    files_list = []
    for root, dirs, files in os.walk(fp):
        dirs[:] = [d for d in dirs if d not in BLACKLIST_DIR]
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext in WHITELIST_FILES:
                if file not in BLACKLIST_FILES:
                    file_path = os.path.join(root, file)
                    lang = get_language_from_extension(file_ext)
                    if lang: files_list.append((file_path, lang))
                    else: print(f'Unsupported file extension {file_ext} in file {file_path}')
    return files_list


def parse_code_files(file_list):
    cls_data = []
    method_data = []
    class_names = set()
    method_names = set()

    files_by_lang = defaultdict(list)
    for fp, lang in file_list:
        files_by_lang[lang].append(fp)

    for lang, files in files_by_lang.items():
        parser = Treesitter.create_treesitter(lang)
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                code = f.read()
                file_bytes = code.encode()
                class_nodes, method_nodes = parser.parse(file_bytes)

                for cls_node in class_nodes:
                    cls_name = cls_node.name
                    class_names.add(cls_name)
                    cls_data.append(
                        dict(
                            file_path=fp,
                            class_name=cls_name,
                            method_declarations='\n------\n'.join(cls_node.method_declarations) if cls_node.method_declarations else '',
                            source_code=cls_node.source_code,
                            references=[]
                        )
                    )

                for method_node in method_nodes:
                    method_name = method_node.name
                    method_names.add(method_name)
                    method_data.append(
                        dict(
                            file_path=fp,
                            class_name=method_node.class_name if method_node.class_name else '',
                            name=method_name,
                            doc_comment=method_node.doc_comment,
                            source_code=method_node.method_source_code,
                            references=[]
                        )
                    )

    return cls_data, method_data, class_names, method_names




def find_references(files, class_names, method_names):
    references = {
        'class': defaultdict(list),
        'method': defaultdict(list)
    }

    files_by_language = defaultdict(list)

    # for faster lookup
    class_names = set(class_names)
    method_names = set(method_names)

    for fp, lang in files_by_language.items(): files_by_language[lang].append(fp)

    for lang, file in files_by_language.items():
        parser = Treesitter.create_treesitter(lang)
        for fp in file:
            with open(fp, 'r', encoding='utf-8') as f:
                code = f.read()
                file_bytes = code.encode()
                tree = parser.parse(file_bytes)
                stack = [(tree.root_node, None)]
                while stack:
                    node, parent = stack.pop()
                    if node.type == 'identifier':
                        name = node.text.decode()

                        # for checking class reference
                        if name in class_names and parent and parent.type in ['type', 'class_type', 'object_creation_expression']:
                            references['class'][name].append(
                               dict(
                                   file=fp,
                                   line=node.start_point[0]+1,
                                   column=node.start_point[1]+1,
                                   text=parent.text.decode()
                               )
                            )

                        # for checking method reference
                        if name in method_names and parent and parent.type in ['call_expression', 'method_invocation']:
                            references['method'][name].append(
                                dict(
                                    file=fp,
                                    line=node.start_point[0]+1,
                                    column=node.start_point[1]+1,
                                    text=parent.text.decode()
                                )
                            )
                    stack.extend((child, node) for child in node.children)

    return references




def map_references(references, class_data_map, method_data_map):
    for cls_name, refs in references['class'].items():
        if cls_name in class_data_map:
            class_data_map[cls_name]['references'] = refs
    for method_name, refs in references['method'].items():
        for key in method_data_map:
            if key[1] == method_name:
                method_data_map[key]['references'] = refs

    return class_data_map, method_data_map



def save_data_to_file(repo_name, class_map, method_map):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f'{OUTPUT_DIR}/{repo_name}', exist_ok=True)
    output_fp = f'{OUTPUT_DIR}/{repo_name}/data.json'
    data = {
        'class': list(class_map.values()),
        'method': list(method_map.values())
    }

    with open(output_fp, 'w+') as f:
        f.dump(data, f)
    return output_fp

    # [TODO]
    method_fp = f'{OUTPUT_DIR}/{repo_name}/methods.csv'
    class_fp = f'{OUTPUT_DIR}/{repo_name}/classes.csv'

    # [TODO] rewrite write to csv in polars
    def write_class_data_to_csv():
        field_names = ['file_path', 'class_name', 'constructor_declaration', 'method_declarations', 'source_code', 'references']
        with open(class_fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            for row in class_map:
                refs = row.get('references', [])
                row['references'] = '; '.join(
                    [f"{ref['file']}:{ref['line']}:{ref['column']}" for ref in refs]
                )
                writer.writerow(row)
        return class_fp

    def write_method_data_to_csv():
        field_names = ['file_path', 'class_name', 'name', 'doc_comment', 'source_code', 'references']
        with open(method_fp, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            for row in method_map:
                refs = row.get('references', [])
                row['references'] = "; ".join(
                    [f"{ref['file']}: {ref['line']}: {ref['column']}" for ref in refs]
                )
                writer.writerow(row)
        return method_fp

    return [write_class_data_to_csv(), write_method_data_to_csv()]



def return_db_data(url, username, token):
    # codebase_path, repo_name = download_codebase(url, username, token)

    codebase_path, repo_name = f'{INPUT_DIR}/mypy', 'mypy'
    files = get_files(codebase_path)
    cls_data, method_data, cls_names, method_names = parse_code_files(files)
    references = find_references(files, cls_names, method_names)
    class_data_map = {o['class_name']: o for o in cls_data}
    method_data_map = {(o['class_name'], o['name']): o for o in method_data}
    print(len(references), len(class_data_map), len(method_data_map))
    data_file_paths = save_data_to_file(repo_name, class_data_map.values(), method_data_map.values())
    print(data_file_paths)



def index_codebase(git_url, username, token):
    git_url = 'https://github.com/python/mypy.git'
    username = None
    token = None
    '''
    git_url = input('Enter git url')
    username = input('Enter git username')
    token = input('Enter git token')
    '''
    db_paths = return_db_data(git_url, username, token)

    db_paths = ['/home/srk/Desktop/projects/fastdaimaCodeAssist/output/mypy/classes.csv', '/home/srk/Desktop/projects/fastdaimaCodeAssist/output/mypy/methods.csv']


    
