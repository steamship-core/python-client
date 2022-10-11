Using Packages
--------------

Instantiating Packages
~~~~~~~~~~~~~~~~~~~~~~

To use a package, first create an instance with the ``Steamship.use`` command:

.. code:: python

   from steamship import Steamship

   instance = Steamship.use("package-handle", "instance-handle")

In the above code, ``package-handle`` identifies which package you would like to use,
and ``instance-handle`` identifies your particular instance of the package.

The ``instance`` object returned is a client-side stub for the cloud package whose state is isolated to a :ref:`workspace<Workspaces>` named ``instance-handle``:

-  Providing a different ``instance-handle`` will result in an instance with a different workspace, and thus distinct state.
-  Providing the same ``instance-handle`` will result in an instance with the same workspace, and thus the same state.

Additional Options
^^^^^^^^^^^^^^^^^^

The ``Steamship.use`` command supports a few additional keyword arguments that may be useful:

- ``version_handle`` lets you pin an instance to a specific package version.
- ``config`` accepts a Python ``dict`` that acts as required configuration for the package

Both ``version_handle`` and ``config`` are frozen upon the first instantiation of a package, per ``instance_handle``.
Creating an instance with the same ``instance_handle``, but different ``version_handle`` or ``config`` will result in an Exception.

Invoking Methods on Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have a package instance, you can invoke methods on packages similarly to regular Python objects.

- ``instance.get`` invokes an HTTP GET-bound package method
- ``instance.post`` invokes an HTTP POST-bound package method
- The first argument is the method name
- All remaining keyword arguments are conveyed in an HTTP-appropriate manner, depending on the verb

For example, you might issue one of the following method invocations:

.. code:: python

   greeting = instance.get("greeting")
   custom_greeting = instance.get("greeting", name="Ted")
   status = instance.post("upload_url", url="https://example.org/some.pdf")

Usability Notes
~~~~~~~~~~~~~~~

We're currently working on ways to make package invocation feel like a first-class citizen,
both from a Python perspective and from an HTTP perspective.

While we pursue that, the preferred way to document (and discover) the available methods on a package is the README
file in its GitHub repository.

