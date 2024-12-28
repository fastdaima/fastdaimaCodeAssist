import unittest 
# from codebase.embeddings import GGUFEmbeddings
from codebase.embeddings import GGufEmbeddings

class TestGGufEmbeddings(unittest.TestCase):

    def test_embed(self):
        gguf = GGufEmbeddings( 'mxbau-embed-xsmall','/home/srk/Desktop/projects/fastdaimaCodeAssist/models/mxbai-embed-xsmall-v1-q8_0.gguf' )

        embeddings = gguf.embed('Hello World')
        print(len(embeddings))
        assert len(embeddings) == 384


if __name__ == '__main__':
    unittest.main()     
