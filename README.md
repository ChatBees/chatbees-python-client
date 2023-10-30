# nautilusdb-python-client
A python client for NautilusDB

## Quick start

You can try out NautilusDB in just a few lines of code! We have 
prepared a special public collection ```openai-web``` that can answer 
questions about contents of ```www.openai.com``` 
``` python
import nautilusdb as ndb

answer, _ = ndb.collection('openai-web').ask('what is red team?')
print(answer)
"""
Sample answer:

Red teaming is a process of adversarial testing and evaluation of
possibly harmful capabilities in new systems, performed by a cohort
of external experts in collaboration with OpenAI.
"""

```
You can also create your own collections, upload files, then get answers 
specific to your data assets. The following example walks you through the 
process of creating a Collection and indexing [the original transformer paper](https://arxiv.org/abs/1706.03762) into that collection.

``` python
import nautilusdb as ndb

# Create an API key
my_api_key = ndb.create_api_key()

# Configure ndb to use the newly minted API key
ndb.init(api_key=my_api_key)

# Create a new collection with preconfigured dimension
llm_research = ndb.CollectionBuilder.question_answer(name="llm_research")
ndb.create_collection(llm_research)

# Index the original Transformer paper into this collection.
llm_research.upload_document("https://arxiv.org/pdf/1706.03762.pdf")

# Get answers from this paper
llm_research.ask("what is a transformer?")

```



## Installation

Install a released NautilusDB python client from pip.

python3 version >= 3.10 is required

``` shell
pip3 install nautilusdb
```

## Creating an API key
You can create an API key. This API key can be configured 

## Creating a Collection

## Uploading a document

## Asking a question
