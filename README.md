# NLUDB Python Client Library

NLUDB is a cloud-hosted database that helps developers get work done with natural language content.

**NLUDB is currently in a closed beta.** If you are interested in joining, please sign up at https://www.nludb.com

## Installing

```
pip install nludb
```

## Examples

These examples illustrate simple ways to apply NLUDB in your project. To run these samples, make sure your API key is present in the `NLUDB_KEY` environment variable.

* **Question Answering Bot**

  A simple chat bot that can learn facts and answer questions. View the source at [src/nludb/examples/chatbot.py](src/nludb/examples/chatbot.py) or run with: 

  ```bash
  python -m nludb.examples.chatbot
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
  EmbeddingModels.QA
)

index.insert("Armadillo shells are bulletproof.")
index.insert("Dolphins sleep with one eye open.")
index.insert("Alfred Hitchcock was frightened of eggs.")
index.insert("Jonathan can help you with new employee onboarding")
index.insert("The code for the New York office is 1234")

results = index.search("Who should I talk to about new employee setup?")    
```

### Classifiers

An Classifier encapsulates a ZeroShot or Pre-Trained classifier over some set of labels. Once a classifier is created, you can call it without providing that parameterization a second time.

```python
index = nludb.create_classifier(
  "Email Intents", 
  ClassifierModels.HF_ZERO_SHOT_LBART,
  save=False, # Use it transiently
  labels=["Account Opening", "Technical Support", "Complaint"]
)

classifier.classify(docs=[
  "I was wondering if you could help me with a problem I've been having"
])
```
