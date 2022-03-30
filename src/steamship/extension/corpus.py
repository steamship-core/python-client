from steamship import Corpus
from steamship.plugin.corpus_importer import CorpusImportResponse, CorpusImportRequest


def doImport(
        self,
        value: str = None,
        url: str = None,
        pluginInstance: str = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None,
        fileImporterPluginInstance: str = None
) -> "Response[CorpusImportResponse]":
    req = CorpusImportRequest(
        type="corpus",
        id=self.id,
        value=value,
        url=url,
        pluginInstance=pluginInstance,
        fileImporterPluginInstance=fileImporterPluginInstance
    )
    return self.client.post(
        'plugin/instance/importCorpus',
        req,
        expect=CorpusImportResponse,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


Corpus.doImport = doImport
