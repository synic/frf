Create a Virtualenv
====================

To keep the packages that you install that are required for FRF separate from
system packages, I recommend using virtualenv.  You can install virtualenv like so:

.. code-block:: text

   $ pip install virtualenv virtualenvrapper

Now, create your virtualenv for our ``blogapi`` application:

.. code-block:: text

   $ mkvirtualenv --python=/usr/bin/python3 blogapi

The location of your python3 executable may be in a different location, and you
may need to change the ``--python`` flag accordingly.

Now, create your project directory, something like the following:

.. code-block:: text

   $ mkdir ~/blogapi
   $ cd ~/blogapi
   $ add2virtualenv .
