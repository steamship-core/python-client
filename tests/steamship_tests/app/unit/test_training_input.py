from steamship.plugin.inputs.train_plugin_input import TrainPluginInput


def test_training_input():
    input = TrainPluginInput.parse_obj({"pluginInstance": "test", "trainingDataUrl": "test"})
    assert input.training_data_url == "test"
