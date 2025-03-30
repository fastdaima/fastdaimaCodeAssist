from dotenv import load_dotenv 
load_dotenv('.env', override=True)

import unittest 
from codebase.vectorstore.lance_db import make_vectorstore, return_db_objects



class TestMakeVectorStore(unittest.TestCase):    
    def test_make_vectorstore(self):
        uri = make_vectorstore('gguf-embeddings', '/home/srk/Desktop/projects/fastdaimaCodeAssist/models/mxbai-embed-xsmall-v1-q8_0.gguf' , 'mypy', 200)
        table_objects = return_db_objects('mypy')
        assert 2 == len(table_objects)


if __name__ == '__main__':
    unittest.main()
