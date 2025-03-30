import lancedb
import pandas as pd

from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
model_name = '/home/srk/Desktop/projects/fastdaimaCodeAssist/models/bge-micro-v2'

from lancedb.embeddings import TransformersEmbeddingFunction

EMBEDDING_DIM = 384
MAX_TOKENS = 1000

model = TransformersEmbeddingFunction(name=model_name, _ndims=EMBEDDING_DIM)

class Method(LanceModel):
    code: str = model.SourceField()
    method_embeddings: Vector(EMBEDDING_DIM) = model.VectorField()
    file_path: str
    class_name: str
    name: str
    doc_comment: str
    source_code: str
    references: str

class Class(LanceModel):
    source_code: str = model.SourceField()
    class_embeddings: Vector(EMBEDDING_DIM) = model.VectorField()
    file_path: str
    class_name: str
    constructor_declaration: str
    method_declarations: str
    references: str

import tiktoken

def clip_text_to_max_tokens(text, max_tokens, encoding_name='cl100k_base'):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    original_token_count = len(tokens)

    print(f"\nOriginal text ({original_token_count} tokens):")
    print("=" * 50)
    print(text[:200] + "..." if len(text) > 200 else text)  # Print first 200 chars for preview

    if original_token_count > max_tokens:
        tokens = tokens[:max_tokens]
        clipped_text = encoding.decode(tokens)
        print(f"\nClipped text ({len(tokens)} tokens):")
        print("=" * 50)
        print(clipped_text[:200] + "..." if len(clipped_text) > 200 else clipped_text)
        return clipped_text

    return text

model = TransformersEmbeddingFunction(name=model_name, _ndims=EMBEDDING_DIM)

method_data  = pd.read_csv('/home/srk/Desktop/projects/fastdaimaCodeAssist/output/mypy/methods.csv')

table_name = 'mypy'
uri = 'database'
db = lancedb.connect(uri)

table = db.create_table(table_name+"_method", schema=Method, mode='overwrite', on_bad_vectors='drop')


#
# embs = model.compute_source_embeddings(
#     ['Hi how are you', 'Hi I am fine']
# )
#
method_data['code'] = method_data['source_code']
null_rows = method_data.isnull().any(axis=1)

if null_rows.any():
    print("Null values found in method_data. Replacing with 'empty'.")
    method_data = method_data.fillna('empty')
else:
    print("No null values found in method_data.")

method_data['source_code'] = method_data.apply(lambda row: clip_text_to_max_tokens(row['source_code'], MAX_TOKENS) + "\n\n", axis=1)



# Add the concatenated data to the table
print("Adding method data to table")
table.add(method_data)
breakpoint()
print(embs)