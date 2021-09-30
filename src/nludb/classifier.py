import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase, AsyncTask, NludbResponse
from nludb.types.classifier import ClassifierCreateRequest, ClassifierCreateResponse, ClassifyRequest, ClassifyResponse
from nludb.types.embedding_index import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class Classifier:
  """A persistent, read-optimized index over embeddings.
  """

  def __init__(self, nludb: ApiBase, id: str = None, name: str = None, model: str = None, labels: List[str] = None):
    if id is None and model is None:
      raise Exception("Either an ID or a model must be provided")

    self.nludb = nludb
    self.name = name
    self.id = id
    self.model = model
    self.labels = labels

  @staticmethod
  def create(
    nludb: ApiBase,
    model: str,
    name: str = None,
    upsert: bool = True,
    save: bool = None,
    labels: List[str] = None
  ) -> "Classifier":
    if save == False:
      return Classifier(nludb, id=None, model=model, name=name, labels=labels)
    else:
      raise Exception("Persistent classifiers not yet supported.")
      req = ClassifierCreateRequest(
        model=model,
        name=name,
        upsert=upsert,
        save=save,
        labels=labels
      )
      res = nludb.post('classifier/create', req)
      return ClassifierCreateResponse(
        nludb=nludb,
        name=req.name,
        id=res.data.get("classifierId", None)
      )

  def classify(
    self, 
    docs: List[str],
    model: str = None,
    labels: List[str] = None,
    k: int = None
  ) -> NludbResponse[ClassifyResponse]:
    if self.id is None and self.model is None:
      raise Exception("Neither an ID nor a model was found on the classifier object. Please reinitialize with one or the other.")

    if self.id is None and (labels is None or len(labels) == 0) and (self.labels is None or len(self.labels) == 0):
      raise Exception('Since you are calling a stateless classifier, please include output labels in your classify request.')
    
    if self.id is not None and labels is not None and len(labels) > 0:
      raise Exception("Since you are calling a stateful classifier, you can not include in-line labels in your classify request. Please add them first.")
    
    req = ClassifyRequest(
      docs=docs,
      classifierId=self.id,
      model=model if model is not None else self.model,
      labels=labels if (labels is not None and len(labels) > 0) else self.labels,
      k=k
    )
    return self.nludb.post(
      'classifier/classify',
      req,
      expect=ClassifyResponse
    )