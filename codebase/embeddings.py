# go through ragas implementation and langchain embeddings implementation to create
# base classes

from abc import ABC, abstractmethod
from typing_extensions import TypedDict
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union, cast
import uuid


import logging
import typing as t
from dataclasses import dataclass

import numpy as np

@dataclass
class RunConfig:
    """
    Configuration for a timeouts, retries and seed for Ragas operations.

    Parameters
    ----------
    timeout : int, optional
        Maximum time (in seconds) to wait for a single operation, by default 60.
    max_retries : int, optional
        Maximum number of retry attempts, by default 10.
    max_wait : int, optional
        Maximum wait time (in seconds) between retries, by default 60.
    max_workers : int, optional
        Maximum number of concurrent workers, by default 16.
    exception_types : Union[Type[BaseException], Tuple[Type[BaseException], ...]], optional
        Exception types to catch and retry on, by default (Exception,).
    log_tenacity : bool, optional
        Whether to log retry attempts using tenacity, by default False.
    seed : int, optional
        Random seed for reproducibility, by default 42.

    Attributes
    ----------
    rng : numpy.random.Generator
        Random number generator initialized with the specified seed.

    Notes
    -----
    The `__post_init__` method initializes the `rng` attribute as a numpy random
    number generator using the specified seed.
    """

    timeout: int = 180
    max_retries: int = 10
    max_wait: int = 60
    max_workers: int = 16
    exception_types: t.Union[
        t.Type[BaseException],
        t.Tuple[t.Type[BaseException], ...],
    ] = (Exception,)
    log_tenacity: bool = False
    seed: int = 42

    def __post_init__(self):
        self.rng = np.random.default_rng(seed=self.seed)


class Embeddings(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        pass

    async def aembed_query(self, text: str) -> list[float]:
        """Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        pass



class EmbeddingsBase(Embeddings, ABC):
    """
    Abstract base class for codebase embeddings

    """
    def __init__(self):
        pass


class HuggingFaceEmbeddings(EmbeddingsBase):
    pass

class OpenAIEmbeddings(EmbeddingsBase):
    pass


