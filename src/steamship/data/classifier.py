from dataclasses import dataclass
from typing import List

from steamship.base import Client, Response, Request
from steamship.data.search import Hit


@dataclass
class ClassifierCreateRequest(Request):
    plugin: str
    name: str = None
    upsert: bool = True
    save: bool = True
    labels: List[str] = None


@dataclass
class ClassifierCreateResponse:
    classifierId: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClassifierCreateResponse":
        return ClassifierCreateResponse(
            classifierId=d.get('classifierId', None),
        )


@dataclass
class ClassifyRequest(Request):
    docs: List[str]
    classifierId: str = None
    plugin: str = None
    labels: List[str] = None
    k: int = None


@dataclass
class ClassifyResponse:
    classifierId: str = None
    plugin: str = None
    hits: List[List[Hit]] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClassifyResponse":
        hits = [[Hit.from_dict(h) for h in innerList] for innerList in (d.get("hits", []) or [])]
        return ClassifyResponse(
            classifierId=d.get('classifierId', None),
            plugin=d.get('plugin', None),
            hits=hits
        )


@dataclass
class LabelInsertRequest(Request):
    value: str
    externalId: str = None
    externalType: str = None
    metadata: str = None


@dataclass
class LabelInsertResponse:
    labelId: str
    value: str
    externalId: str = None
    externalType: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "LabelInsertResponse":
        return LabelInsertResponse(
            labelId=d.get('labelId', None),
            value=d.get('value', None),
            externalId=d.get('externalId', None),
            externalType=d.get('externalType', None),
            metadata=d.get('metadata', None),
        )


class Classifier:
    """A persistent, read-optimized index over embeddings.
    """

    def __init__(self, client: Client, id: str = None, name: str = None, plugin: str = None, labels: List[str] = None):
        if id is None and model is None:
            raise Exception("Either an ID or a model must be provided")

        self.client = client
        self.name = name
        self.id = id
        self.model = model
        self.labels = labels

    @staticmethod
    def create(
            client: Client,
            plugin: str,
            name: str = None,
            upsert: bool = True,
            save: bool = None,
            labels: List[str] = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> "Response[Classifier]":
        if save == False:
            return Response(
                data=Classifier(client, id=None, plugin=plugin, name=name, labels=labels)
            )
        else:
            raise Exception("Persistent classifiers not yet supported.")
            req = ClassifierCreateRequest(
                plugin=plugin,
                name=name,
                upsert=upsert,
                save=save,
                labels=labels
            )
            res = client.post(
                'classifier/create',
                req,
                spaceId=spaceId,
                spaceHandle=spaceHandle
            )
            return ClassifierCreateResponse(
                client=client,
                name=req.name,
                id=res.data.get("classifierId", None)
            )

    def classify(
            self,
            docs: List[str],
            plugin: str = None,
            labels: List[str] = None,
            k: int = None,
            pd: bool = False,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ClassifyResponse]:
        if self.id is None and self.model is None:
            raise Exception(
                "Neither an ID nor a model was found on the classifier object. Please reinitialize with one or the other.")

        if self.id is None and (labels is None or len(labels) == 0) and (self.labels is None or len(self.labels) == 0):
            raise Exception(
                'Since you are calling a stateless classifier, please include output labels in your classify request.')

        if self.id is not None and labels is not None and len(labels) > 0:
            raise Exception(
                "Since you are calling a stateful classifier, you can not include in-line labels in your classify request. Please add them first.")

        req = ClassifyRequest(
            docs=docs,
            classifierId=self.id,
            plugin=plugin if model is not None else self.model,
            labels=labels if (labels is not None and len(labels) > 0) else self.labels,
            k=k
        )
        ret = self.client.post(
            'classifier/classify',
            req,
            expect=ClassifyResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )
        if pd is False:
            return ret

        import pandas as pd  # type: ignore
        return pd.DataFrame([(hit.score, hit.value) for hit in ret.data.hits[0]], columns=['Score', 'Value'])
