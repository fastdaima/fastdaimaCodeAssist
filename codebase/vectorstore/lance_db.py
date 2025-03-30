import lancedb
from lancedb.embeddings import TextEmbeddingFunction, EmbeddingFunctionRegistry
from ..embeddings import GGufEmbeddings
from lancedb.pydantic import LanceModel, Vector
import os 
import pandas as pd
from ..utils import clip_text_to_max_tokens
from lancedb.embeddings.registry import register


@register('gguf-embeddings')
class GGUFEmbeddingFunction(TextEmbeddingFunction):
    name: str = 'model-path'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ndims = None

    @property
    def embedding_model(self):
        return self.get_embedding_model()
        
    def ndims(self):
        if not self._ndims: self._ndims = len(self.embedding_model.embed('foo'))
        return self._ndims    
    
    def generate_embeddings(self, texts):
        return self.embedding_model.embed_batch(texts)

    def get_embedding_model(self):
        return GGufEmbeddings(self.name)._model



def return_model(model_type='gguf-embeddings', model_name=None):
    registry = EmbeddingFunctionRegistry.get_instance()
    model = registry.get(model_type).create(name=model_name)
    return model 


def return_pydantic_classes(model_type, model_name):
    model = return_model(model_type, model_name)
    class Method(LanceModel):
        code: str = model.SourceField()
        method_embeddings: Vector(model.ndims()) = model.VectorField()
        file_path: str
        class_name: str
        name: str
        doc_comment: str
        source_code: str
        references: str

    class Class(LanceModel):
        source_code: str = model.SourceField()
        class_embeddings: Vector(model.ndims()) = model.VectorField()
        file_path: str
        class_name: str
        constructor_declaration: str
        method_declarations: str
        references: str

    return Method, Class


def make_vectorstore(model_type, model_name, project_name, MAX_TOKENS=1000):
    methods, classes = return_pydantic_classes(model_type, model_name)
    method_data = pd.read_csv(f'{os.environ["OUTPUT_DIR"]}/{project_name}/methods.csv')
    class_data = pd.read_csv(f'{os.environ["OUTPUT_DIR"]}/{project_name}/classes.csv')

    table_name = project_name
    uri = os.environ['LANCEDB_DATABASE_URI']
    db = lancedb.connect(uri)

    method_table = db.create_table(table_name+'_method', schema=methods, mode='overwrite', on_bad_vectors='drop')
    class_table = db.create_table(table_name+'_class', schema=classes, mode='overwrite', on_bad_vectors='drop')


    method_data['code'] = method_data['source_code']
    null_rows = method_data.isnull().any(axis=1)

    if null_rows.any():
        print("Null values found in method_data. Replacing with 'empty'.")
        method_data = method_data.fillna('empty')
    else:
        print("No null values found in method_data.")

    # Add the concatenated data to the table
    print("Adding method data to table")
    
    method_table.add(method_data)

    class_table = db.create_table(
        table_name + "_class", 
        schema=classes, 
        mode="overwrite",
        on_bad_vectors='drop'
    )
    null_rows = class_data.isnull().any(axis=1)
    if null_rows.any():
        print("Null values found in class_data. Replacing with 'empty'.")
        class_data = class_data.fillna('')
    else:
        print("No null values found in class_data.")

    class_data['source_code'] = class_data.apply(lambda row: "File: " + row['file_path'] + "\n\n" +
                                                    "Class: " + row['class_name'] + "\n\n" +
                                                    "Source Code:\n" + 
                                                    clip_text_to_max_tokens(row['source_code'], MAX_TOKENS) + "\n\n", axis=1)

    if len(class_data) == 0:
        columns = ['source_code', 'file_path', 'class_name', 'constructor_declaration', 'method_declarations', 'references']
        empty_data = {col: ["empty"] for col in columns}

        class_data = pd.DataFrame(empty_data)
        
    print("Adding class data to table")
    class_table.add(class_data)

    print("Embedded method data successfully")
    print("Embedded class data successfully")

    return uri  

def return_db_objects(table_name):
    uri = os.environ['LANCEDB_DATABASE_URI']
    db = lancedb.connect(uri)
    method_table = db.open_table(table_name+'_method')
    class_table = db.open_table(table_name+'_class')
    return method_table, class_table

def search_table(table, query, top_k=10):
    return table.search(query, top_k=top_k).to_pandas()

