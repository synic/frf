Install Falcon Rest Framework
=============================

Make sure you are in the project directory, and that the virtualenv is active:

.. code-block:: text

   $ cd ~/blogapi
   $ workon blogapi

Now, install FRF:

.. code-block:: text

   $ pip install frf

If you want stdout output to be a bit prettier, install
``colorama`` and ``pyfiglet``:

.. code-block:: text

   $ pip install colorama pyfiglet


And, now, you should be able to initialize your project directory:

.. code-block:: text

   $ frf-setupproject -o .
