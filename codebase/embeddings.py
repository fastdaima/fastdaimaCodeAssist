# go through ragas implementation and langchain embeddings implementation to create
# base classes


from abc import ABC, abstractmethod
from typing_extensions import TypedDict
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, List, Optional, TypeVar, Union, cast
import uuid
from dataclasses import dataclass, field 

import logging
import typing as t
from dataclasses import dataclass
from itertools import islice 
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


# use https://huggingface.co/nvidia/NV-Embed-v2 model for creating embeddings


from llama_cpp import Llama

# taken from awesome simon willison llm and llm_gguf projects 

class EmbeddingModel(ABC):
    """
    Embeddings model base class, embed a batch of strings or bytes, which returns a list of floats 
    """
    model_id: str 
    key: Optional[str] = None 
    needs_key: Optional[str] = None 
    key_env_var: Optional[str] = None 
    supports_text: bool = True 
    supports_binary: bool = False 
    batch_size: Optional[int] = None


    def _check(self, item: Union[str, bytes]):
        if not self.supports_binary and isinstance(item, bytes): raise ValueError('This model does not support binary data, please try strings')
        if not self.supports_text and isinstance(item, bytes): raise ValueError('This model does not support strings, please try bytes')

    def embed(self, item: Union[str, bytes]) -> List[float]:
        self._check(item)
        return next(iter(self.embed_batch([item])))
    
    def embed_multi(self, items: Iterable[Union[str, bytes]], batch_size: Optional[int]=None) -> Iterator[List[float]]:
        iter_items = iter(items)
        batch_size = self.batch_size if batch_size is None else batch_size
        if (not self.supports_text) or (not self.supports_binary):
            def checking_iter(items):
                for item in items: 
                    self._check(item)
                    yield item 
            iter_items = checking_iter(items)
        if batch_size is None: 
            yield from self.embed_batch(iter_items) 
            return 
        while True:
            batch_items = list(islice(iter_items, batch_size))
            if not batch_items: break 
            yield from self.embed_batch(batch_items)

    @abstractmethod
    def embed_batch(self, items: Iterable[Union[str, bytes]]) -> Iterator[List[float]]:
        pass


class GGufEmbeddings(EmbeddingModel):
    def __init__(self, model_id, model_path): 
        self.model_id = model_id 
        self.model_path = model_path 
        self._model = None 
    
    def embed_batch(self, texts):
        if self._model is None: 
            self._model = Llama(
                model_path = self.model_path, embedding=True, verbose=False 
            )
        results = self._model.create_embedding(texts)
        return [result['embedding'] for result in results['data']]