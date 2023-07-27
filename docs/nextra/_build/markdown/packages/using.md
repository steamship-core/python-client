<a id="usingpackages"></a>

# Using Packages

#### NOTE
Before you begin, make sure you’ve set up your authentication

And installed a Steamship client library with:

> ```bash
> pip install steamship
> ```

> ```bash
> npm install --save @steamship/client
> ```

Steamship packages are listed in our [package directory](https://www.steamship.com/packages).
To use one, instantiate it with `Steamship.use`, giving it a package handle and an instance handle.

```python
from steamship import Steamship

instance = Steamship.use("package-handle", "instance-handle")
```

```typescript
import { Steamship } from "@steamship/client"

const instance = Steamship.use("package-handle", "instance-handle")
```

The **package handle** references the package you’d like to use.
The **instance handle** creates a private stack for data and infrastructure that package depends on.

Once you have a package instance, invoke a method by calling `invoke`.
The method name is the first argument.
All other arguments are passed as keyword args.

```python
result = instance.invoke('method_name', arg1=val1, arg2=val2)
```

```typescript
const result = await instance.invoke('method_name', {arg1: val1, arg2: val2})
```

The method will run in the cloud, and you’ll get back the response as a Python object.
Packages can also be used as [HTTP APIs](../configuration/http.md#http).

## Package FAQ

- [What is a Package Handle?](#what-is-a-package-handle)
- [What is an Instance Handle?](#what-is-an-instance-handle)
- [Do I need an Instance Handle?](#do-i-need-an-instance-handle)
- [Can I reload the same instance?](#can-i-reload-the-same-instance)
- [How do I specify a package version?](#how-do-i-specify-a-package-version)
- [How do I provide package configuration?](#how-do-i-provide-package-configuration)
- [How do I know what methods to call?](#how-do-i-know-what-methods-to-call)
- [Can I access my package over HTTP?](#can-i-access-my-package-over-http)

<a id="what-is-a-package-handle"></a>

### What is a Package Handle?

A **Package Handle** identifies a Steamship package, in the same way that NPM and PyPI packages have identifiers.

```python
from steamship import Steamship
instance = Steamship.use("package-handle", "instance-handle")
```

```typescript
import { Steamship } from "@steamship/client"
const instance = Steamship.use("package-handle", "instance-handle")
```

Package handles always composed of lowercase letters and dashes.

<a id="what-is-an-instance-handle"></a>

### What is an Instance Handle?

An **Instance Handle** identifies a particular instance of the package.

```python
from steamship import Steamship
instance = Steamship.use("package-handle", "instance-handle")
```

```typescript
import { Steamship } from "@steamship/client"
const instance = Steamship.use("package-handle", "instance-handle")
```

Steamship packages manage their own configuration, data, endpoints, and infrastructure in the cloud.
Your instance handle of a package creates a scope, private to you, to contain that.

<a id="do-i-need-an-instance-handle"></a>

### Do I need an Instance Handle?

If you do not provide an **Instance Handle**, the default value will be identical to the **Package Handle**.

```python
from steamship import Steamship
instance1 = Steamship.use("package-handle")
instance1_copy = Steamship.use("package-handle")
instance1_copy2 = Steamship.use("package-handle")
```

```typescript
import { Steamship } from "@steamship/client"

const instance1 = Steamship.use("package-handle")
const instance1_copy = Steamship.use("package-handle")
const instance1_copy2 = Steamship.use("package-handle")
```

The above code loads three copies of the **same instance**, bound to the **same data and infrastructure**.
It is equivalent to having run this code:

```python
from steamship import Steamship
instance = Steamship.use("package-handle", "package-handle")
instance1_copy = Steamship.use("package-handle", "package-handle")
instance1_copy2 = Steamship.use("package-handle", "package-handle")
```

```typescript
import { Steamship } from "@steamship/client"

const instance1 = Steamship.use("package-handle", "package-handle")
const instance1_copy = Steamship.use("package-handle", "package-handle")
const instance1_copy2 = Steamship.use("package-handle", "package-handle")
```

<a id="can-i-reload-the-same-instance"></a>

### Can I reload the same instance?

You can reload a package instance by providing the same instance handle again.
All of the correct configuration, data, and models will be bound to the instance.

In the below code,

* `instance1` and `instance1_copy` are operating upon the same data and infrastructure.
* `instance2` is operating upon a different set of data and infrastructure

```python
instance1 = Steamship.use("package-handle", "instance-handle")
instance1_copy = Steamship.use("package-handle", "instance-handle")
instace2 = Steamship.use("package-handle", "some-other-handle")
```

```typescript
import { Steamship } from "@steamship/client"

const instance1 = Steamship.use("package-handle", "instance-handle")
const instance1_copy = Steamship.use("package-handle", "instance-handle")
const instance2 = Steamship.use("package-handle", "some-other-handle")
```

<a id="how-do-i-specify-a-package-version"></a>

### How do I specify a package version?

When instantiating a package, you can pin it to a particular version with the `version` keyword argument.

```python
instance = Steamship.use("package-handle", "instance-handle", version="1.0.0")
```

```typescript
import { Steamship } from "@steamship/client"

const instance = Steamship.use("package-handle", "instance-handle", "1.0.0")
```

If you do not specify a version, the last deployed version of that package will be used.

<a id="how-do-i-provide-package-configuration"></a>

### How do I provide package configuration?

When instantiating a package, you can provide configuration with the `config` keyword argument.

```python
instance = Steamship.use("package-handle", "instance-handle", config=config_dict)
```

```typescript
import { Steamship } from "@steamship/client"

const instance = Steamship.use("package-handle", "instance-handle", undefined, {key: "value"})
```

To learn what configuration is required, consult the README.md file in the package’s GitHub repository.

<a id="how-do-i-know-what-methods-to-call"></a>

### How do I know what methods to call?

To learn what methods are available on a package, consult the README.md file in the package’s GitHub repository.

We are working on a more streamlined way to generate and publish per-package documentation.

In the meantime, you can also explore a package’s methods from your REPL with:

```python
instance = Steamship.use("package-handle")
instance.invoke("__dir__")
```

```typescript
const instance = Steamship.use("package-handle")
instance.invoke("__dir__")
```

<a id="can-i-access-my-package-over-http"></a>

### Can I access my package over HTTP?

Every instance of your package exposes an HTTP API that you can call. The **Instance Base URL** is:

> ```default
> https://{userHandle}.steamship.run/{workspaceHandle}/{instanceHandle}/
> ```

In that URL:

- `{userHandle}` is your user handle (not the handle of the person who create the package)
- `{workspaceHandle}` is the handle of the workspace that package is running in. It is usually equal to the `instanceHandle`
- `{instanceHandle}` is the name you gave your instance

You can always find out your **Instance Base URL** via the Python Client with the `PackageInstance.invocation_url` property:

> ```python
> instance = Steamship.use('some-package', 'my-handle')
> print(instance.invocation_url)

> # Prints:
> # https://{you}.steamship.run/my-handle/my-handle/
> ```

Calling this URL is simple with a few conventions:

- Set the `Content-Type` header to `application/json`
- Set the `Authorization` header to `Bearer {api-key}`, replacing `{api-key}` with your API Key
- Default to `HTTP POST` if you’re not sure which verb to use. The package documentation should specify.
- Add the method name you wish to invoke as the path.
- Add the arguments as a JSON-encoded POST Body

For example, the HTTP equivalent of:

> ```python
> instance.invoke('greet', name='Beautiful')
> ```

would be:

> ```default
> POST /{workspace-handle}/{instance-handle}/greet
> Content-Type: application/json
> Authorization: Bearer {api-key}

> {"name": "Beautiful"}
> ```
