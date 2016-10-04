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

This example displays the spreading of knowledge of a rumor through a distributed population of agents.  An initial group of agents have knowledge of the model and spread this knowledge.  The probability of the rumor reaching an agent is proportional to the number of neighbors that have knowledge of the rumor.

The network is generated within the model.

Run the Model:
```
mpiexec -np number_of_processors python rumor-model-main.py  number_of_persons rumor_prob
```

Use the help command to find additional options for the model.
```
python rumor-model-main.py --help
```

#### Tax Model

Description here: link to paper

The tax model generates the networks from an input file of networks, this saves time within Python and allows for repeated networks.


Run the Model:
```
mpiexec -np number_of_processors python tax-chapter-main.py taxpayers tax_rate t_steps penalty_rate audit_prob
    app_rate max_audit apprehension network_file prop_honest prop_dishonest
```

Use the help command to find additional options for the model.
```
python tax-chapter-main.py --help
```

