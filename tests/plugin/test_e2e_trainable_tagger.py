from steamship.data.plugin import TrainingPlatform
from steamship.data.plugin_instance import PluginInstance
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import (
    TrainingParameterPluginInput,
)
from .. import APPS_PATH

__copyright__ = "Steamship"
__license__ = "MIT"

#
# def test_e2e_trainable_tagger_lambda_training():
#     client = get_steamship_client()
#     versionConfigTemplate = dict(
#         textColumn=dict(type="string"),
#         tagColumns=dict(type="string"),
#         tagKind=dict(type="string")
#     )
#     instanceConfig = dict(
#         textColumn="Message",
#         tagColumns="Category",
#         tagKind="Intent"
#     )
#
#     # Make a blockifier which will generate our training corpus
#     with deploy_plugin("csv_blockifier.py", "blockifier", versionConfigTemplate=versionConfigTemplate, instanceConfig=instanceConfig, trainingPlatform=TrainingPlatform.custom) as (plugin, version, instance):
#         with upload_file("utterances.csv") as file:
#             assert (len(file.refresh().data.blocks) == 0)
#             # Use the plugin we just registered
#             file.blockify(pluginInstance=instance.handle).wait()
#             assert (len(file.refresh().data.blocks) == 5)
#
#             # Now make a trainable tagger to train on those tags
#             with deploy_plugin("plugin_trainable_tagger.py", "tagger", trainingPlatform=TrainingPlatform.custom) as (tagger, taggerVersion, taggerInstance):
#
#                 # Now train the plugippcn
#                 trainingRequest = TrainingParameterPluginInput(
#                     pluginInstance=taggerInstance.handle,
#                     exportPluginInput=ExportPluginInput(
#                         type="corpus",
#                         handle="default"
#                     )
#                 )
#
#                 trainResult = taggerInstance.train(trainingRequest)
#
#                 trainResult.wait()
from ..utils.client import get_steamship_client
from ..utils.file import upload_file
from ..utils.deployables import deploy_plugin

EXPORTER_HANDLE = "signed-url-exporter"


def test_e2e_trainable_tagger_ecs_training():
    client = get_steamship_client()

    version_config_template = dict(
        text_column=dict(type="string"),
        tag_columns=dict(type="string"),
        tag_kind=dict(type="string"),
    )
    instance_config = dict(
        text_column="Message", tag_columns="Category", tag_kind="Intent"
    )

    exporter_plugin_r = PluginInstance.create(
        client=client,
        handle=EXPORTER_HANDLE,
        plugin_handle=EXPORTER_HANDLE,
        upsert=True,
    )
    assert exporter_plugin_r.data is not None
    exporter_plugin = exporter_plugin_r.data
    assert exporter_plugin.handle is not None

    csv_blockifier_path = APPS_PATH / "plugins" / "blockifiers" / "csv_blockifier.py"
    trainable_tagger_path = APPS_PATH / "plugins" / "taggers" / "plugin_trainable_tagger.py"

    # Make a blockifier which will generate our training corpus
    with deploy_plugin(
            client,
            csv_blockifier_path,
            "blockifier",
            version_config_template=version_config_template,
            instance_config=instance_config,
    ) as (plugin, version, instance):
        with upload_file(client, "utterances.csv") as file:
            assert len(file.refresh().data.blocks) == 0
            # Use the plugin we just registered
            file.blockify(plugin_instance=instance.handle).wait()
            assert len(file.refresh().data.blocks) == 5

            # Now make a trainable tagger to train on those tags
            with deploy_plugin(
                    client,
                    trainable_tagger_path,
                    "tagger",
                    training_platform=TrainingPlatform.managed,
            ) as (tagger, taggerVersion, taggerInstance):
                # Now train the plugin
                training_request = TrainingParameterPluginInput(
                    pluginInstance=taggerInstance.handle,
                    exportRequest=ExportPluginInput(
                        pluginInstance=EXPORTER_HANDLE, type="corpus", handle="default"
                    ),
                )

                train_result = taggerInstance.train(training_request)
                train_result.wait()
