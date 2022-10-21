from __future__ import annotations

from typing import Dict, Optional

from steamship.base.model import CamelModel
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


class TrainingParameterPluginInput(CamelModel):
    # The plugin instance handle that should perform the training.
    plugin_instance: Optional[str] = None
    # An export request to produce the training data file, if training data is required.
    export_plugin_input: Optional[ExportPluginInput] = None

    # How many epochs to train (if supported by the supplied `pluginInstance`)
    training_epochs: Optional[int] = None

    # How much of the data to hold out for testing (if supported by the supplied `pluginInstance`)
    testing_holdout_percent: Optional[float] = None

    # Random seed for performing the train/test split (if supported by the supplied `pluginInstance`)
    test_split_seed: Optional[int] = None

    # Custom training-time parameters, specific to the pluginInstance
    training_params: Optional[Dict] = None

    # Custom inference-time parameters, specific to the pluginInstance
    inference_params: Optional[Dict] = None
