The pg_guyton database
===============================================================================

This set of tools defines the schema of a (PostgreSQL) database, intended for
storing the results of vast sets of simulations with various incarnations of
the Guyton model of whole-body physiology
(such as [this version](https://github.com/rma/guyton92)).

Prerequisite software:

* [Python](http://www.python.org/)
* [psycopg2](http://initd.org/psycopg/)
* [PostgreSQL](http://www.postgresql.org/)

Configuring PostgreSQL
===============================================================================

Step 1: Creating a PostgreSQL account
-------------------------------------------------------------------------------

The owner of the database should create an account (a `role`) in PostgreSQL.
The name of the role should correspond to the user name of the owner's account
on the host computer. In the following example, the role `rma` is created:

    # sudo -u postgres psql
    template1=> CREATE ROLE rma WITH CREATEDB CREATEROLE LOGIN;
    template1=> \q

If the first command (`su postgres`) asks for a password, and trusted
connections are enabled (see the PostgreSQL documentation for
`pg_hba.conf`), the following example can be used instead:

    # psql -U postgres
    template1=> CREATE ROLE rma WITH CREATEDB CREATEROLE LOGIN;
    template1=> \q

Step 2: Accessing the PostgreSQL terminal
-------------------------------------------------------------------------------

Once you have created a role, you can access PostgreSQL through the interactive
terminal `psql`:

    # psql template1

Here you can enter any SQL commands (if you have the necessary privileges) and
psql commands. Type `help` for more information, or `\q` to quit.

Initialising the database
===============================================================================

Step 1: Setting the database options
-------------------------------------------------------------------------------

The file `psql_conf.sh` contains the configuration settings for the various
scripts that create and manipulate the pg_guyton database. Check that these
settings are correct before continuing.

Step 2: Creating the database
-------------------------------------------------------------------------------

The script `create_db.sh` will create the database according to the schema in
`schema.sql`. Once you have a role that has been assigned the LOGIN and
CREATEDB privileges, you can execute the following script:

    # ./create_db.sh

Step 3: Populating the model metadata
-------------------------------------------------------------------------------

The previous step created the database as per the schema, but did not populate
any of the tables. To add the necessary parameters and variables to the Guyton
database, execute the following script:

    # ./create_metadata.py metadata.txt

Step 4: Adding roles for other people
-------------------------------------------------------------------------------

Each person that needs direct access to the database needs a role whose name
corresponds to their user name on the host computer. In the following example,
a role is created for the user `abc`:

    # ./create_role.sh abc

Importing simulation results
===============================================================================

Once each user has been assigned a role and the database has been configured,
simulation results can be imported using the following script:

    # ./import_results.py -t "some tag name" results.txt

Any number of tags can be associated with each of the imported simulations, by
providing multiple `-t "tag name"` arguments. Any tags that don't already
exist in the database will be automatically created.

**NOTE:** The `import_results.py` script currently only supports perturbation
experiments performed with the Guyton model (1992 version).
