# import contextlib
# import time
# from pathlib import Path
# from typing import Dict
#
# from steamship import App, AppVersion, AppInstance, Steamship
# from steamship.data.user import User
#
#
# @contextlib.contextmanager
# def deploy_app(
#         client: Steamship,
#         py_path: Path,
#         version_config_template: Dict[str, Any] = None,
#         instance_config: Dict[str, Any] = None,
# ):
#     app = App.create(client)
#     assert app.error is None
#     assert app.data is not None
#     app = app.data
#
#     zip_bytes = zip_app(py_name)
#     version = AppVersion.create(
#         client,
#         app_id=app.id,
#         filebytes=zip_bytes,
#         config_template=version_config_template,
#     )
#     # TODO: This is due to having to wait for the lambda to finish deploying.
#     # TODO: We should update the task system to allow its .wait() to depend on this.
#     time.sleep(15)
#     version.wait()
#     assert version.error is None
#     assert version.data is not None
#     version = version.data
#
#     instance = AppInstance.create(
#         client, app_id=app.id, app_version_id=version.id, config=instance_config
#     )
#     instance.wait()
#     assert instance.error is None
#     assert instance.data is not None
#     instance = instance.data
#
#     assert instance.app_id == app.id
#     assert instance.app_version_id == version.id
#
#     user = User.current(client).data
#
#     assert instance.user_handle == user.handle
#     assert instance.user_id == user.id
#
#     yield app, version, instance
#
#     res = instance.delete()
#     assert res.error is None
#
#     res = version.delete()
#     assert res.error is None
#
#     res = app.delete()
#     assert res.error is None
