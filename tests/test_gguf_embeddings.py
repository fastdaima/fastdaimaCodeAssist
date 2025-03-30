import unittest 
from codebase.embeddings import GGufEmbeddings

class TestGGufEmbeddings(unittest.TestCase):

    def test_embed(self):
        gguf = GGufEmbeddings( 'mxbau-embed-xsmall','/home/srk/Desktop/projects/fastdaimaCodeAssist/models/mxbai-embed-xsmall-v1-q8_0.gguf' )

        embeddings = gguf.embed('Hello World')
        print(len(embeddings))
        assert len(embeddings) == 384

    def test_embed_batch(self):
        gguf = GGufEmbeddings( 'mxbau-embed-xsmall','/home/srk/Desktop/projects/fastdaimaCodeAssist/models/mxbai-embed-xsmall-v1-q8_0.gguf' )
        embeddings = gguf.embed_batch(['Hello fastdaima', 'I am glad to be in your service'])

        for emb in embeddings:
            assert len(emb) == 384

if __name__ == '__main__':
    unittest.main()     
