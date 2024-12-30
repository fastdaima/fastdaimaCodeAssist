import functools
import weakref 
import tiktoken

def weak_lru(maxsize=128):
    def wrapper(func):
        @functools.lru_cache(maxsize)
        def _func(_self, *args, **kwargs):
            return func(_self(), *args, **kwargs)

        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            return _func(weakref.ref(self), *args, **kwargs)

        return inner
    return wrapper


def clip_text_to_max_tokens(text, max_tokens, encoding_name='cl100k_base'):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    original_token_count = len(tokens)
    if original_token_count > max_tokens:
        tokens = tokens[:max_tokens]
        clipped_text = encoding.decode(tokens)
        return clipped_text

    return text