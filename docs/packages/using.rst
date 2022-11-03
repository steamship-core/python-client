.. _UsingPackages:

Using Packages
--------------

.. note::
   Before you begin, make sure you've created your Steamship keys with:

   ``npm install -g @steamship/cli && ship login``

   And installed our Python Client with:

   ``pip install steamship``

Steamship packages are listed in our `package directory <https://www.steamship.com/packages>`_.
To use one, instantiate it with ``Steamship.use``, giving it a package handle and an instance handle.

.. code-block:: python

   from steamship import Steamship

   instance = Steamship.use("package-handle", "instance-handle")

The **package handle** references the package you'd like to use.
The **instance handle** creates a private stack for data and infrastructure that package depends on.

Once you have a package instance, invoke a method by calling ``invoke``.
The method name is the first argument.
All other arguments are passed as keyword args.

.. code-block:: python

   result = instance.invoke('method_name', arg1=val1, arg2=val2)

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

.. _what-is-a-package-handle:

What is a Package Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^

A **Package Handle** identifies a Steamship package, in the same way that NPM and PyPI packages have identifiers.

.. code-block:: python

   from steamship import Steamship
   instance = Steamship.use("package-handle", "instance-handle")

Package handles always composed of lowercase letters and dashes.

.. _what-is-an-instance-handle:

What is an Instance Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An **Instance Handle** identifies a particular instance of the package.

.. code-block:: python

   from steamship import Steamship
   instance = Steamship.use("package-handle", "instance-handle")


Steamship packages manage their own configuration, data, endpoints, and infrastructure in the cloud.
Your instance handle of a package creates a scope, private to you, to contain that.

.. _do-i-need-an-instance-handle:

Do I need an Instance Handle?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not provide an **Instance Handle**, the default value will be identical to the **Package Handle**.

.. code-block:: python

   from steamship import Steamship
   instance = Steamship.use("package-handle")
   instance = Steamship.use("package-handle")
   instance = Steamship.use("package-handle")

The above code loads three copies of the **same instance**, bound to the **same data and infrastructure**.
It is equivalent to having run this code:

.. code-block:: python

   from steamship import Steamship
   instance = Steamship.use("package-handle", "package-handle")
   instance = Steamship.use("package-handle", "package-handle")
   instance = Steamship.use("package-handle", "package-handle")

.. _can-i-reload-the-same-instance:

Can I reload the same instance?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can reload a package instance by providing the same instance handle again.
All of the correct configuration, data, and models will be bound to the instance.

In the below code,

*  ``instance_1`` and ``instance_2`` are operating upon the same data and infrastructure.
*  ``instance_3`` is operating upon a different set of data and infrastructure

.. code-block:: python

   instance_1 = Steamship.use("package-handle", "instance-handle")
   instance_2 = Steamship.use("package-handle", "instance-handle")
   instance_3 = Steamship.use("package-handle", "some-other-handle")

.. _how-do-i-specify-a-package-version:

How do I specify a package version?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When instantiating a package, you can pin it to a particular version with the ``version`` keyword argument.

.. code-block:: python

   instance_1 = Steamship.use("package-handle", "instance-handle", version="1.0.0")

If you do not specify a version, the last deployed version of that package will be used.

.. _how-do-i-provide-package-configuration:

How do I provide package configuration?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When instantiating a package, you can provide configuration with the ``config`` keyword argument.

.. code-block:: python

   instance_1 = Steamship.use("package-handle", "instance-handle", config=config_dict)

To learn what configuration is required, consult the README.md file in the package's GitHub repository.

.. _how-do-i-know-what-methods-to-call:

How do I know what methods to call?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To learn what methods are available on a package, consult the README.md file in the package's GitHub repository.

We are working on a more streamlined way to generate and publish per-package documentation.

In the meantime, you can also explore a package's methods from your REPL with:

.. code-block:: python

   instance = Steamship.use("package-handle")
   instance.invoke("__dir__")