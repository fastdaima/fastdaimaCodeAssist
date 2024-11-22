# fastdaimaCodeAssist
## what is this?
- A question answering system which helps user on the codebase wide queries by retrieving relevant snippets, file names and references
- whenever user says @fca {query}, our system will return relevant information
- sample questions from lancedb blog 
```
	- "What is this git repository about?"
	- "How does a particular method work?" → where you may not mention the exact name of method
	- "Which methods do xyz things?" → it is supposed to identify the relevant method/class names from your query
	- They can be more complex, e.g. "What is the connection between EncoderClass and DecoderClass?" → The system is supposed to answer by gathering context from multiple sources (multi-hop question answering) 
```


## Feature set

- [] repository map generation 
- [] tree map parser implementation for chunking
- [] generating overall file structure in an md / text file
- [] initial language support for python language
- [] indexing codebases into sqlite-vec along with metadata
- [] 


# Heavy References: 
- https://blog.lancedb.com/rag-codebase-1/
- https://github.com/Aider-AI/aider
- https://github.com/mufeedvh/code2prompt
- [what is a treesitter?](https://www.youtube.com/watch?v=09-9LltqWLY)
