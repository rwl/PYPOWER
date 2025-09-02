# PyPOWER API

As of Version 5.1.20 a Python convenience API is available for developers who wish to use PyPOWER as part of their applications.  The API provides the following convenience classes

The `Case`: handles cases, include creating, reading, editing, solving, and writing cases. Cases use the following data accessor classes:

    * `Bus`: access bus objects

    * `Branch`: access branch objects

    * `Gen`: access generator objects

    * `Gencost`: access generator cost objects

    * `Dcline`: access DC line objects

    * `Dclinecost`: access DC line cost objects

The `Case` class also provide runners for powerflow, OPF, and CDF solvers, including non-linear heuristic solvers.  In addition, all solver options may be set using the `Case` class.

## Create a new case

## Adding objects

## Delete objects

## Access object data

## Iterating over objects

## Saving a case

## Reading a case

## Solving a case

## Extracting matrices
