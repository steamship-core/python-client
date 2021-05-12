# NLUDB Python Client Library

NLUDB is a cloud-hosted database that helps developers get work done with natural language content.

**NLUDB is currently in a closed beta.** If you are interested in joining, please sign up at https://www.nludb.com

## Installing

```
pip install nludb
```
## Using

### Initialization

Sign up for an account at https://www.nludb.com to get your API key. Then use it to initialize your client library:

```python
from nludb import NLUDB, EmbeddingModels
nludb = NLUDB(api_key)
```

### Embedding Indices

An Embedding Index is a persistent, read-optimized index over an embedded space. Once an index is created, you can search for similar items within that embedding space.

```python
index = nludb.create_index(
  "Question Answering Index", 
  EmbeddingModels.DEFAULT_QA
)

index.insert("Armadillo shells are bulletproof.")
results = index.search("What is something interesting about Armadillos?")    
```
