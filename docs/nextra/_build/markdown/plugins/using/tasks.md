<a id="tasks"></a>

# Tasks

Most [Plugin](../index.md#plugins) operations return a `Task`.  This allows you to conveniently handle the long,
asynchronous aspect of many plugin invocations.

## Waiting on Tasks

If your code does not need to do any other work while the `Plugin` is running, you may `wait()` on the `Task`:

This will make your code poll the Steamship service until either the `Task` is complete, or the wait timeout is reached.

#### NOTE
Waiting on the task may time out before the `Task` is complete. Don’t worry, the `Task` is still running on the server.
You can increase the time you wait by passing the `max_timeout_s` parameter.

## Returning Tasks from a Package

One common pattern when your package does long asynchronous work is to return a `Task` id which can
be used later to check on the status of the `Task`. To check the status of a `Task` from its id:

Once you have a task object again, you can `wait()` on it, or check its `state` variable.
