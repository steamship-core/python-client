import os
from typing import List
from nludb import EmbeddingModels
from nludb import NLUDB 

# Note: Numpy and SKLearn isn't in requirements.txt since it is only
#       used in this example!
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity 

class NludbAnomalyDetector:
  def __init__(self, api_key: str, model: str):
    self.nludb = NLUDB(api_key)
    self.model = model
    self.datapoints = []
    self.embeddings = []

  def add_datapoints(self, values: List[str]):
    res = self.nludb.embed(values, self.model)
    for value, embedding in zip(values, res.embeddings):
      self.datapoints.append(value)
      self.embeddings.append(np.array(embedding))
  
  def compute_mean(self) -> List[float]:
    return np.mean(self.embeddings, axis=0)

  def find_furthest(self) -> str:
    mean = self.compute_mean()
    sim = cosine_similarity(self.embeddings, [mean])
    # distances = self.embeddings - mean
    # norms = np.linalg.norm(distances, axis=1)    
    # print(norms)
    print(sim)
    furthest = np.argmin(sim)
    return self.datapoints[furthest]
    
def main():
  nludb_key = os.environ['NLUDB_KEY']
  if nludb_key is None:
    print("Please set the NLUDB_KEY environment variable")
    return

  def new_detector() -> NludbAnomalyDetector:
    return NludbAnomalyDetector(api_key=nludb_key, model=EmbeddingModels.SIMILARITY)

  detector = new_detector()
  print('''NLUDB Anomaly Detection Demonstration
  
Enter a list of items to consider, pressing enter after each.
Enter a blank line to find the one most unlike the others.
  ''')
  while True:
    message = input("> ")   # Python 3
    if len(message) == 0:
      print("Finding which one doesn't belong..")
      print("My guess: {}".format(detector.find_furthest()))
      detector = new_detector()
      print("")
    else:
      detector.add_datapoints([message])

if __name__ == "__main__":
  main()