from pathlib import Path

from steamship_tests import PACKAGES_PATH, PLUGINS_PATH
from steamship_tests.utils.deployables import zip_deployable

output_path = "../../nludb/TestAssets/"


def build_asset(py_path: Path, output_file: str):
    zip_bytes = zip_deployable(py_path)
    with open(output_path + output_file, "wb") as f:
        f.write(zip_bytes)


def main():

    assets_to_build = [
        (PLUGINS_PATH / "blockifiers" / "csv_blockifier.py", "csv-blockifier.zip"),
        (PACKAGES_PATH / "demo_package.py", "demo-package.zip"),
        (PACKAGES_PATH / "configurable_hello_world.py", "configurable_hello_world.zip"),
        (PLUGINS_PATH / "blockifiers" / "blockifier.py", "dummy-blockifier.zip"),
        (PACKAGES_PATH / "bad_package.py", "bad-package.zip"),
        (PACKAGES_PATH / "package_with_instance_init.py", "package-with-instance-init.zip"),
        (
            PACKAGES_PATH / "package_with_failing_instance_init.py",
            "package-with-failing-instance-init.zip",
        ),
        (
            PLUGINS_PATH / "generators" / "plugin_with_instance_init.py",
            "plugin-with-instance-init.zip",
        ),
        (
            PLUGINS_PATH / "generators" / "request_id_generator.py",
            "request-id-generator.zip",
        ),
        (
            PACKAGES_PATH / "request_id_plumbing_test_package.py",
            "request-id-plumbing-test-package.zip",
        ),
    ]

    for path, output in assets_to_build:
        build_asset(path, output)


main()
