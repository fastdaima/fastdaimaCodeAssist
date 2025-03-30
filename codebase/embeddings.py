# go through ragas implementation and langchain embeddings implementation to create
# base classes


from abc import ABC, abstractmethod
from typing_extensions import TypedDict
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, List, Optional, TypeVar, Union, cast
from itertools import islice 
import numpy as np
from llama_cpp import Llama

from codebase.utils import weak_lru



# use https://huggingface.co/nvidia/NV-Embed-v2 model for creating embeddings


class EmbeddingModel(ABC):
    """
    Embeddings model base class, embed a batch of strings or bytes, which returns a list of floats 
    """
    model_id: str
    model_path: str 
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
    def __init__(self, model_path, model_id=None): 
        self.model_id = model_id 
        self.model_path = model_path 
        self._model = self._get_model()
    
    def embed_batch(self, texts):
        results = self._model.create_embedding(texts)
        return [result['embedding'] for result in results['data']]

    @weak_lru(maxsize=1)
    def _get_model(self):
        return Llama(
            model_path = self.model_path, embedding=True, verbose=False 
        )