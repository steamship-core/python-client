from steamship import App, AppVersion, AppInstance

from .helpers import _random_name, _steamship, create_app_zip

__copyright__ = "Steamship"
__license__ = "MIT"

def test_instance_invoke():
  client = _steamship()
  name = _random_name()

  app = App.create(client, name=name).data
  zip_bytes = create_app_zip('demo_app.py')

  version = AppVersion.create(
    client, 
    appId=app.id, 
    filebytes=zip_bytes
  )

  version.wait()

  instance = AppInstance.create(
    client, 
    appId=app.id,
    appVersionId=version.data.id, 
  )
  instance.wait()
  assert(instance.error is None)
  assert(instance.data is not None)
  instance = instance.data
  assert(instance.appId == app.id)
  assert(instance.userHandle is not None)
  assert(instance.userId is not None)


  # Now let's invoke it!
  # Note: we're invoking the data at demo_app.py in the tests/demo_apps folder

  res = instance.get('greet').data
  assert(res == "Hello, Person!")

  res = instance.get('greet', name="Ted").data
  assert(res == "Hello, Ted!")

  res = instance.post('greet').data
  assert(res == "Hello, Person!")

  res = instance.post('greet', name="Ted").data
  assert(res == "Hello, Ted!")

  res = instance.delete()
  assert(res.error is None)

  res = version.data.delete()
  assert(res.error is None)

  res = app.delete()
  assert(res.error is None)


  
