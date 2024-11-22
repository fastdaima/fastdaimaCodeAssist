from abc import ABC
from enum import Enum

from tree_sitter import Language, Parser
from tree_sitter_languages.core import get_language, get_parser
from typing import List
import logging

class LanguageEnum(Enum):
    PYTHON = 'python'


LANGUAGE_QUERIES = {
    LanguageEnum.PYTHON: {
        'class_query': """
            (class_definition
                name: (identifier) @class.name)
        """,
        'method_query': """
            (function_definition
                name: (identifier) @function.name)
        """,
        'doc_query': """
            (expression_statement
                (string) @comment)
        """
    }
}

class MethodNode:
    def __init__(self, name: str, doc_comment: str, method_source_code: str, node, class_name: str= None):
        self.name = name
        self.doc_comment = doc_comment
        self.method_source_code = method_source_code
        self.node = node
        self.class_name = class_name

class ClassNode:
    def __init__(self, name: str, method_declarations: List, node):
        self.name = name
        self.source_code = node.text.decode()
        self.node = node
        self.method_declarations = method_declarations


class Treesitter(ABC):
    def __init__(self, language: LanguageEnum):
        self.language_enum = language
        self.parser = get_parser(language.value)
        self.language_obj = get_language(language.value)
        self.query_config = LANGUAGE_QUERIES.get(language)
        if not self.query_config:
            raise ValueError(f'Unsupported language: {language}')
        self.class_query = self.language_obj.query(
            self.query_config['class_query'],
        )
        self.method_query = self.language_obj.query(
            self.query_config['method_query'],
        )
        self.doc_query = self.language_obj.query(
            self.query_config['doc_query'],
        )

    @staticmethod
    def create_treesitter(language: LanguageEnum):
        return Treesitter(language)

    def parse(self, file_bytes: bytes):
        tree = self.parser.parse(file_bytes)
        root = tree.root_node
        class_results = []
        method_results = []

        class_name_by_node = {}
        class_captures = self.class_query.captures(root)
        class_nodes = []

        for node, capture_name in class_captures:
            if capture_name == 'class.name':
                class_name = node.text.decode()
                class_node = node.parent
                class_name_by_node[class_node.id]= class_name
                methods_in_class = self._extract_methods_in_class(class_node)
                class_results.append(
                    ClassNode(
                        class_name,
                        methods_in_class,
                        class_node
                    )
                )

        method_captures = self.method_query.captures(root)

        for node, capture_name in method_captures:
            if capture_name == 'function.name':
                method_name = node.text.decode()
                method_node = node.parent
                method_source_code = method_node.text.decode()
                doc_comment = self._extract_doc_comment(method_node)
                parent_class_name = None
                for class_node in class_nodes:
                    if self._is_descendant_of(method_node, class_node):
                        parent_class_name = class_name_by_node[class_node.id]
                        break
                method_results.append(
                    MethodNode(
                        name=method_name,
                        doc_comment=doc_comment,
                        method_source_code=method_source_code,
                        node=method_node,
                        class_name=parent_class_name
                    )
                )
        return class_results, method_results

    def _extract_methods_in_class(self, class_node):
        method_declarations = []
        method_captures = self.method_query.captures(class_node)
        for node, capture_name in method_captures:
            if capture_name == 'function.name':
                method_declaration = node.parent.text.decode()
                method_declarations.append(method_declaration)
        return method_declarations

    def _extract_doc_comment(self, node):
        doc_comment = ''
        cur_node = node.prev_sibling
        while cur_node:
            captures = self.doc_query.captures(cur_node)
            if captures:
                for cap_node, cap_name in captures:
                    if cap_name == 'comment':
                        doc_comment = cap_node.text.decode() + '\n' + doc_comment
            elif cur_node.type not in ['comment']:
                break
            cur_node = cur_node.prev_sibling
        return doc_comment.strip()

    def _is_descendant_of(self, method_node, class_node):
        """checks if method node is an descendant of class_node"""
        current = method_node.parent
        while current:
            if current == class_node: return True
            method_node = method_node.parent
        return False



