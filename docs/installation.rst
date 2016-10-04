Installation
============

Requirements
------------

**Main requirements:**

* pytz
* SQLAlchemy
* falcon
* jinja2
* pycrypto
* tabulate
* pytest
* python-datutil
* gunicorn

**Optional requirements:**

* redis (for redis cache support)
* Sphinx (for document generation)
* colorama (for pretty output)
* pyfiglet (for pretty output)

PyPy
----

`PyPy <http://pypy.org/>`_ is the fastest way to run your FRF app.

.. code-block:: bash

    $ pip install frf

From Source
-----------

.. code-block:: bash

    $ git clone https://github.com/enderlabs/frf
    $ cd frf
    $ python setup.py install
