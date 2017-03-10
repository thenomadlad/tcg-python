# TCG-Python

This is a test case generator for software (or anything, really) with a clear
set of states, and transitions connecting all the states.

## Core:
The python code has the logic for traversing the states and transitions in the
form of a Multi-DiGraph. This allows us to find the smallest path that covers
the transitions, and as a result also covers the states in that graph.

This is basically a solution to the chinese postman path problem.
(Not to be confused with the Travelling Salesman problem)
