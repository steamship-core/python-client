from steamship import Corpus
from steamship.plugin.corpus_importer import CorpusImportResponse, CorpusImportRequest


def do_import(
    self,
    value: str = None,
    url: str = None,
    plugin_instance: str = None,
    space_id: str = None,
    space_handle: str = None,
    space: any = None,
    file_importer_plugin_instance: str = None,
) -> "Response[CorpusImportResponse]":
    # TODO (enias): Why not part of Corpus?
    req = CorpusImportRequest(
        type="corpus",
        id=self.id,
        value=value,
        url=url,
        pluginInstance=plugin_instance,
        fileImporterPluginInstance=file_importer_plugin_instance,
    )
    return self.client.post(
        "plugin/instance/importCorpus",
        req,
        expect=CorpusImportResponse,
        space_id=space_id,
        space_handle=space_handle,
        space=space,
    )


Corpus.do_import = do_import
