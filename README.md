empdb
=====

    A WSGI app for viewing the `test employees database`_ provided by MySQL.

    .. _test employees datbase: http://dev.mysql.com/doc/employee/en/index.html.


Installation
------------

1. Create and activate a virtual environment (so that your system doesn't get
   polluted)::

      [~/work] virtualenv emptest
      [~/work] . emptest/bin/activate


2. install the Employees-0.1.tar.gz package::

    (emptest)[~/work/Employees-0.1] python ./setup.py install
   or::
    easy_install Employees-0.1.tar.gz
   or::
    easy_install Employees-0.1
   or::
    pip install Employees-0.1.tar.gz
   or::
    pip install Employees-0.1

Also make sure the DB driver you plan to use is installed.


Configure the Application
-------------------------

1. Edit the config file you wish to use:

    development.ini
        lots of verbose output, don't need to restart if templates are
        modified. Suitable for development.
    production.ini
        faster than development, no debug output. Need to restart if anything
        changes.

NOTE: the "sqlalchemy.url" config *MUST* be modified to point to the
appropriate DB.  Due to resource constraints, the application has been tested
only (on linux) with with only a fraction of the mysql database entries (124
employees).
    
The application has been tested against Sqlite3 as well.


Running the Application
-----------------------

1. Start the server::

    pserve development.ini

or::
    pserve production.ini


2. Point your browser to the configured IP:PORT.

Login is any user's Firstname.Lastname
Password is the user's employee number


Acknowledgements
----------------
This software uses:
    * Python (of course)
    * Pyramid
    * JQuery
    * Bootstrap
    * "Jasny Bootstrap" from Arnold Daniels (https://github.com/jasny/bootstrap/) for the "row link" plugin
    * An magnifying glass icon from https://openclipart.org/detail/78163/office-glass-magnify-by-sheikh_tuhin
    * A modified cancel icon from https://openclipart.org/detail/34729/architetto----tasto-8-by-anonymous
