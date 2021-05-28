import re
import os
from nludb import EmbeddingModels
from nludb import NLUDB 

FACT_TRIGGERS = [
  "fact", "rem", "remember", "learn", "true story"
]

FACT_PUNCT = [
  ":", " -- ", " that ", " - ", "--", "-", " "
]

class NludbChatbotBase:
  def __init__(
    self, 
    api_key: str, 
    index_name: str, 
    min_confidence: float = 0.4):
    self.nludb = NLUDB(api_key)
    self.index_name = index_name
    self.min_confidence = min_confidence
    self.index = self.nludb.create_index(
        index_name, 
        EmbeddingModels.QA, 
        upsert=True
    )

  def learn_fact(self, fact: str, externalId: str = None, externalType: str = None, metadata: dict = None):
    if fact is None:
      return None
    return self.index.insert(
      fact,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata
    )

  def search_facts(self, query:  str) -> str:
    res = self.index.search(query)
    if res is None or res.hits is None or len(res.hits) == 0:
      return None
    hit = res.hits[0]
    if hit.score is None or hit.score < self.min_confidence:
      return None
    return hit.value 

  def extract_fact(self, input: str) -> str:
    lower = re.sub("\s\s+" , " ", input.lower())
    triggered = False
    for trigger in FACT_TRIGGERS:
      if lower.find(trigger) == 0:
        input = input[len(trigger):]
        triggered = True
        break
    if not triggered:
      return None
    
    # Now we strip the punctuation
    for punct in FACT_PUNCT:
      if input.find(punct) == 0:
        input = input[len(punct):]
        return input
    return input
  
  def dispatch(self, message: str, externalId: str = None, externalType: str = None, metadata: dict = None) -> str:
    maybe_fact = self.extract_fact(message)
    if maybe_fact is not None:
      self.learn_fact(maybe_fact, externalId=externalId, externalType=externalType, metadata=metadata)
      return "{}... OK, I got it!".format(maybe_fact)
    
    # Assume it's a question
    return self.search_facts(message)


def main():
  nludb_key = os.environ['NLUDB_KEY']
  if nludb_key is None:
    print("Please set the NLUDB_KEY environment variable")
    return

  index_name = os.environ.get('NLUDB_INDEX', "NludbChatbotBase Demo")
  bot = NludbChatbotBase(api_key=nludb_key, index_name=index_name)

  print('''NLUDB QA Bot Demonstration
  
Type "fact: <some fact>" to learn something new.
Type a question to retrieve knowledge.
  ''')
  while True:
    message = input("> ")   # Python 3
    response = bot.dispatch(message)
    if response:
      print(response)
    else:
      print("Unsure how to respond..")
    print("")

if __name__ == "__main__":
  main()