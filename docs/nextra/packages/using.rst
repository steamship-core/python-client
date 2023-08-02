.. _UsingPackages:

Using Packages
--------------

.. note::
   Before you begin, make sure you've set up your :ref:`authentication<Auth>`

   And installed a Steamship client library with:

    .. tab:: Python

        .. code-block:: bash

           pip install steamship

    .. tab:: Typescript (Alpha)

        .. code-block:: bash

           npm install --save @steamship/client

Steamship packages are listed in our `package directory <https://www.steamship.com/packages>`_.
To use one, instantiate it with ``Steamship.use``, giving it a package handle and an instance handle.

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship

       instance = Steamship.use("package-handle", "instance-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance = Steamship.use("package-handle", "instance-handle")

The **package handle** references the package you'd like to use.
The **instance handle** creates a private stack for data and infrastructure that package depends on.

Once you have a package instance, invoke a method by calling ``invoke``.
The method name is the first argument.
All other arguments are passed as keyword args.

.. tab:: Python

    .. code-block:: python

       result = instance.invoke('method_name', arg1=val1, arg2=val2)

.. tab:: Typescript

    .. code-block:: typescript

       const result = await instance.invoke('method_name', {arg1: val1, arg2: val2})

The method will run in the cloud, and you'll get back the response as a Python object.
Packages can also be used as :ref:`HTTP APIs<HTTP>`.

Package FAQ
~~~~~~~~~~~

- :ref:`What is a Package Handle?<what-is-a-package-handle>`
- :ref:`What is an Instance Handle?<what-is-an-instance-handle>`
- :ref:`Do I need an Instance Handle?<do-i-need-an-instance-handle>`
- :ref:`Can I reload the same instance?<can-i-reload-the-same-instance>`
- :ref:`How do I specify a package version?<how-do-i-specify-a-package-version>`
- :ref:`How do I provide package configuration?<how-do-i-provide-package-configuration>`
- :ref:`How do I know what methods to call?<how-do-i-know-what-methods-to-call>`
- :ref:`Can I access my package over HTTP?<can-i-access-my-package-over-http>`

.. _what-is-a-package-handle:

What is a Package Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^

A **Package Handle** identifies a Steamship package, in the same way that NPM and PyPI packages have identifiers.

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship
       instance = Steamship.use("package-handle", "instance-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"
       const instance = Steamship.use("package-handle", "instance-handle")


Package handles always composed of lowercase letters and dashes.

.. _what-is-an-instance-handle:

What is an Instance Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An **Instance Handle** identifies a particular instance of the package.

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship
       instance = Steamship.use("package-handle", "instance-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"
       const instance = Steamship.use("package-handle", "instance-handle")

Steamship packages manage their own configuration, data, endpoints, and infrastructure in the cloud.
Your instance handle of a package creates a scope, private to you, to contain that.

.. _do-i-need-an-instance-handle:

Do I need an Instance Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not provide an **Instance Handle**, the default value will be identical to the **Package Handle**.

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship
       instance1 = Steamship.use("package-handle")
       instance1_copy = Steamship.use("package-handle")
       instance1_copy2 = Steamship.use("package-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance1 = Steamship.use("package-handle")
       const instance1_copy = Steamship.use("package-handle")
       const instance1_copy2 = Steamship.use("package-handle")

The above code loads three copies of the **same instance**, bound to the **same data and infrastructure**.
It is equivalent to having run this code:

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship
       instance = Steamship.use("package-handle", "package-handle")
       instance1_copy = Steamship.use("package-handle", "package-handle")
       instance1_copy2 = Steamship.use("package-handle", "package-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance1 = Steamship.use("package-handle", "package-handle")
       const instance1_copy = Steamship.use("package-handle", "package-handle")
       const instance1_copy2 = Steamship.use("package-handle", "package-handle")


.. _can-i-reload-the-same-instance:

Can I reload the same instance?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can reload a package instance by providing the same instance handle again.
All of the correct configuration, data, and models will be bound to the instance.

In the below code,

*  ``instance1`` and ``instance1_copy`` are operating upon the same data and infrastructure.
*  ``instance2`` is operating upon a different set of data and infrastructure

.. tab:: Python

    .. code-block:: python

       instance1 = Steamship.use("package-handle", "instance-handle")
       instance1_copy = Steamship.use("package-handle", "instance-handle")
       instace2 = Steamship.use("package-handle", "some-other-handle")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance1 = Steamship.use("package-handle", "instance-handle")
       const instance1_copy = Steamship.use("package-handle", "instance-handle")
       const instance2 = Steamship.use("package-handle", "some-other-handle")

.. _how-do-i-specify-a-package-version:

How do I specify a package version?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When instantiating a package, you can pin it to a particular version with the ``version`` keyword argument.

.. tab:: Python

    .. code-block:: python

       instance = Steamship.use("package-handle", "instance-handle", version="1.0.0")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance = Steamship.use("package-handle", "instance-handle", "1.0.0")

If you do not specify a version, the last deployed version of that package will be used.

.. _how-do-i-provide-package-configuration:

How do I provide package configuration?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When instantiating a package, you can provide configuration with the ``config`` keyword argument.

.. tab:: Python

    .. code-block:: python

       instance = Steamship.use("package-handle", "instance-handle", config=config_dict)

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const instance = Steamship.use("package-handle", "instance-handle", undefined, {key: "value"})

To learn what configuration is required, consult the README.md file in the package's GitHub repository.

.. _how-do-i-know-what-methods-to-call:

How do I know what methods to call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To learn what methods are available on a package, consult the README.md file in the package's GitHub repository.

We are working on a more streamlined way to generate and publish per-package documentation.

In the meantime, you can also explore a package's methods from your REPL with:

.. tab:: Python

    .. code-block:: python

       instance = Steamship.use("package-handle")
       instance.invoke("__dir__")

.. tab:: Typescript

    .. code-block:: typescript

       const instance = Steamship.use("package-handle")
       instance.invoke("__dir__")

.. _can-i-access-my-package-over-http:

Can I access my package over HTTP?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every instance of your package exposes an HTTP API that you can call. The **Instance Base URL** is:

    .. code-block::

       https://{userHandle}.steamship.run/{workspaceHandle}/{instanceHandle}/

In that URL:

- ``{userHandle}`` is your user handle (not the handle of the person who create the package)
- ``{workspaceHandle}`` is the handle of the workspace that package is running in. It is usually equal to the ``instanceHandle``
- ``{instanceHandle}`` is the name you gave your instance

You can always find out your **Instance Base URL** via the Python Client with the ``PackageInstance.invocation_url`` property:

    .. code-block:: python

       instance = Steamship.use('some-package', 'my-handle')
       print(instance.invocation_url)

       # Prints:
       # https://{you}.steamship.run/my-handle/my-handle/

Calling this URL is simple with a few conventions:

- Set the ``Content-Type`` header to ``application/json``
- Set the ``Authorization`` header to ``Bearer {api-key}``, replacing ``{api-key}`` with your API Key
- Default to ``HTTP POST`` if you're not sure which verb to use. The package documentation should specify.
- Add the method name you wish to invoke as the path.
- Add the arguments as a JSON-encoded POST Body

For example, the HTTP equivalent of:

    .. code-block:: python

       instance.invoke('greet', name='Beautiful')

would be:

    .. code-block::

       POST /{workspace-handle}/{instance-handle}/greet
       Content-Type: application/json
       Authorization: Bearer {api-key}

       {"name": "Beautiful"}

