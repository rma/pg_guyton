--
-- schema.sql
--
-- This defines the schema for the database of simulation results obtained with
-- various incarnations of the Guyton model of whole-body physiology. This file
-- can be executed by psql to create a PostgreSQL database.
--
-- PostgreSQL-specific queries for examining tables:
--
-- SELECT tablename FROM pg_tables WHERE tablename !~ '^(pg|sql)_+';
-- SELECT column_name FROM information_schema.columns
--        WHERE table_name = 'table_name';
--

-- Each parameter has a (unique) name, some associated unit of measurement, a
-- description of what value it represents, a permitted range of values, and
-- some default value. Parameters are identified by a unique ID.
CREATE TABLE parameter (
  id SERIAL,
  name text NOT NULL,
  units text,
  description text,
  min_val double precision NOT NULL,
  max_val double precision NOT NULL,
  default_val double precision NOT NULL,
  PRIMARY KEY (id)
);

-- Each variable has a (unique) name, some associated unit of measurement, a
-- description of what quantity it represents, and some default value.
-- Variables are identified by a unique ID.
CREATE TABLE variable (
  id SERIAL,
  name text NOT NULL,
  units text,
  description text,
  default_val double precision NOT NULL,
  PRIMARY KEY (id)
);

-- A model is a combination of input parameters and variables, equations for
-- calculating the output variables, and an algorithm for solving each of the
-- equations. The only details recorded here are a (unique) name, a description
-- of the model and a reference to some publication that describes the model in
-- sufficient detail to reproduce any associated results. Models are identified
-- by a unique ID.
CREATE TABLE model (
  id SERIAL,
  name text NOT NULL,
  description text NOT NULL,
  reference text NOT NULL,
  PRIMARY KEY (id)
);

-- Each parameter is defined in one (or more) models. If a parameter name is
-- shared by two models but other details (such as the units) differ, then two
-- different parameters must be defined. This is why there is no explicit
-- uniqueness constraint on parameter names. The same reasoning also applies to
-- the lack of uniqueness constraint on variable names.
CREATE TABLE defined_for (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  model integer REFERENCES model ON DELETE CASCADE ON UPDATE CASCADE,
  parameter integer REFERENCES parameter ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (model, parameter)
);

-- The recorded results of a single experiment include the values of all model
-- parameters and the values of the output variables at multiple points in the
-- simulation; these details are recorded in the "param_value" and "var_value"
-- tables. Any number of pre-defined tags can also be associated with a single
-- experiment; this is recorded in the "tagged_with" table. In addition, the
-- following details are stored on a per-experiment basis: the model that was
-- used in the experiment, the (real-world) time when the experiment was either
-- performed or added to the database, the person who performed the experiment,
-- and the computer on which the experiment was performed.
CREATE TABLE experiment (
  id SERIAL,
  model integer REFERENCES model ON DELETE CASCADE ON UPDATE CASCADE,
  at_time timestamp with time zone NOT NULL,
  by_user text NOT NULL,
  on_host text NOT NULL,
  PRIMARY KEY (id)
);

-- Tags can be applied arbitrarily to experiments. Each tag consists of a
-- (unique) name and a description of the tag. Tags are identified by a unique
-- ID.
CREATE TABLE tag (
  id SERIAL,
  name text NOT NULL,
  description text NOT NULL,
  PRIMARY KEY (id)
);

-- Each experiment is associated with zero or more tags. This many-to-many
-- relationship is recorded in the following table, with no additional details.
CREATE TABLE tagged_with (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  experiment integer REFERENCES experiment ON DELETE CASCADE ON UPDATE CASCADE,
  tag integer REFERENCES tag ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (experiment, tag)
);

-- The values of output variables are recorded at various times throughout a
-- simulation. In addition to identifying the (simulation) time at which a
-- value was recorded, it is desirable to identify why that specific time was
-- chosen. This information consists of a (unique) name and a description.
CREATE TABLE time_detail (
  id SERIAL,
  name text NOT NULL,
  description text NOT NULL,
  PRIMARY KEY (id)
);

-- In each simulation the initial parameter values are recorded, as are any
-- changes to these values at later times in the simulation. In addition to
-- the simulation time and the value of the parameter, it is also recorded
-- whether this parameter was identified as being "of interest".
CREATE TABLE param_value (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  experiment integer REFERENCES experiment ON DELETE CASCADE ON UPDATE CASCADE,
  parameter integer REFERENCES parameter ON DELETE CASCADE ON UPDATE CASCADE,
  at_time double precision NOT NULL,
  value double precision NOT NULL,
  of_interest boolean NOT NULL,
  PRIMARY KEY (experiment, parameter, at_time),
  UNIQUE (id)
);

-- In each simulation the values of the output variables are recorded at any
-- number of points during the simulation. In addition to the simulation time
-- and the value of the variable, it is also recorded why this point in the
-- simulation was chosen and whether this variable was identified as being
-- "of interest".
CREATE TABLE var_value (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  experiment integer REFERENCES experiment ON DELETE CASCADE ON UPDATE CASCADE,
  variable integer REFERENCES variable ON DELETE CASCADE ON UPDATE CASCADE,
  at_time double precision NOT NULL,
  value double precision NOT NULL,
  why_now integer REFERENCES time_detail ON DELETE CASCADE ON UPDATE CASCADE,
  of_interest boolean NOT NULL,
  PRIMARY KEY (experiment, variable, at_time),
  UNIQUE (id)
);

CREATE TABLE individual (
  id SERIAL,
  experiment integer REFERENCES experiment ON DELETE CASCADE ON UPDATE CASCADE,
  perturbed boolean NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE indiv_param (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  individual integer REFERENCES individual ON DELETE CASCADE ON UPDATE CASCADE,
  value bigint REFERENCES param_value (id) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (id)
);

CREATE TABLE indiv_var (
  id BIGSERIAL, -- Django doesn't support multiple-field primary keys.
  individual integer REFERENCES individual ON DELETE CASCADE ON UPDATE CASCADE,
  value bigint REFERENCES var_value (id) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (id)
);
