# Massive-Scale Agent-Based Modeling (MABM) Module

Welcome to the Massive-Scale Agent-Based Modeling (MABM) Module for Python.  This toolkit allows developers to create
a distributed Agent-Based model in Python.

## Getting Started

The module requires Python 2.7 as well as the following Python Modules:
- mpi4py
- numpy
- argparse

### Included Models

This setup includes a basic rumor model as well as a tax model.

#### Rumor Model
This example displays the spreading of knowledge of a rumor through a distributed population of agents.  An initial
group of agents have knowledge of the model and spread this knowledge.  The probability of the rumor reaching an agent
is proportional to the number of neighbors that have knowledge of the rumor.

Run the Model:
```
mpiexec -np num_processors python main.py people_per_processor rumor_prob [options]
```

OR

```
mpiexec -np 2 python main.py [-h] [-w] [-l] [-W] [-P] [-a [APPEND]] [-c [CROSS]] [-z [ZIPF]]
    number_of_persons rumor_prob
```

#### Tax Model
Description here: link to paper



Run the Model:
```
mpiexec -np num_processors python main.py people_per_processor rumor_prob [options]
```

OR

```
mpiexec -np 2 python main.py [-h] [-w] [-l] [-W] [-P] [-a [APPEND]] [-c [CROSS]] [-z [ZIPF]]
    number_of_persons rumor_prob
```

