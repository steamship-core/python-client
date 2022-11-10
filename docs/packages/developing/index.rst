Developing Packages
-------------------

Steamship is the fastest way to build and deploy a full-stack language AI package.

Here's how to go from zero-to-deployed in about 60 seconds.
Then you can customize your new package from there.

First, create a new package with our CLI.

.. code-block:: bash

   ship create

   > Select *Package*
   > Select *Empty Package*

Then deploy the package to the cloud:

.. code-block:: bash

   ship deploy

Now create a new instance of your package. If you used the **Empty Package** template, you can use the CLI to create one:

.. code-block:: bash

   ship package:instance:create --default_name="Beautiful"

That keyword argument above is part of the required configuration.
You can see where that argument is defined in the ``src/api.py`` file of your new package, and you can see
where it is required in the ``steamship.json`` file.

The response you get back will contain your **Instance Handle**.

Let's invoke a method on that instance. Replacing your Instance Handle below, run:

.. code-block:: bash

   ship package:instance:invoke --instance="INSTANCE_HANDLE" --method="greet"

Now let's create an instance and invoke it from Python.
After running ``pip install steamship``, run the following code, replacing your package and instance handles:

.. code-block:: python

   from steamship import Steamship

   # TODO: Replace with your package and instance handle below
   instance = Steamship.use("PACKAGE_HANDLE", "INSTANCE_HANDLE", config={
       "default_name": "Beautiful"
   })

   print(instance.invoke("greet"))

That's it!
You've just created a new package, deployed it, and invoked it from two different environments.

Now the real fun begins...

Customizing your Package
~~~~~~~~~~~~~~~~~~~~~~~~

Steamship packages run on top of a cloud stack designed for Language AI.
You can import files, parse and tag them, query over them, return custom results -- and far more.

.. grid::  1 1 2 3

   .. grid-item-card:: **Package Project Structure**
      :link: project-structure.html

      Understand the basic project structure that defines a package and how to develop in it.

   .. grid-item-card:: **Package Cookbook**
      :link: ../cookbook/index.html

      A cookbook of common operations you may want to perform, such as parsing files, transcribing audio, and querying results.

   .. grid-item-card:: **Developer Reference**
      :link: ../../developing/index.html

      Lower-level details on Steamship development, such as environment setup, configuration, testing, and secret management.
