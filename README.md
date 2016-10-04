# Massive-Scale Agent-Based Modeling (MABM) Module

Welcome to the Massive-Scale Agent-Based Modeling (MABM) Module for Python.  This toolkit allows developers to create
a distributed Agent-Based model in Python.

The Massive-Scale Agent-Based Modeling (MABM) Toolkit is a Python module that enables developers to create distributed Agent-Based Models. This toolkit was developed under the Massive Scale Agent Based Model of US Individual Tax Paying Population to Study Individual Reporting Compliance Behaviors and Massive-Scale Agent Based Models for Compliance and Service MIP Projects at the MITRE Corporation. Original development was completed by James Gentile and Christine Harvey.

For more information on the MABM toolkit, please contact Christine Harvey (ceharvey@mitre.org).

## Toolkit Purpose

To date, agent-based models generally work at a very small scale (generally around 10,000 agents). The emergent behaviors from these small-scale models may not hold at the larger scale. Our goal has been to develop models with 100,000,000 (100M) agents, a representation of large national or worldwide populations. This scale requires a distributed modeling framework. In a lean Python implementation, an agent consumes 1 Kilobyte of RAM (including model overhead) so a large-scale model would consume at least 100 Gigabytes of memory. Agent memory consumption will increase as complex attributes, networks and interactions are developed. A distributed implementation will require entity state to be communicated across processes.

## Model Layout

![Layout of the MABM module for the toolkit.  The blue text represents attributes of the class.](https://gitlab.mitre.org/ceharvey/MABM/raw/720c5dc7579327ffc15c77fc8596ee416b31cd8d/Images/1000px-MABM_Module_Desgin.png)
The MABM Module is designed to build and schedule distributed Agent-Based models while abstracting the used from the distributed nature of the program.  The base MABM module is used to build these models and these classes are built on to develop Agent Based Models.  The diagram to the right explains the design and overall layout of the MABM module.
* Element - Every model will contain elements, these are the entities that interact in the model and make decisions.  Each element has a distinct element_id
** Agent - The agent class is an instance of the Element class.  An agent is a more specific form of an entity.  Each Agent is assigned a specific model and container.
* ElementForm - The element form is a basic shadow or ghost copy of an element.  This basic copy contains less information and takes up less space in memory.  These forms are used to represent shadow images of agents actually located on foreign processors.  Each ElementForm has an element_id.
* ElementID - An element ID is a unique identifier for every agent in the model.  Each ElementID has a type, number, process, and birth_process.  The number represents the birth order on the process and the type represents the agent type.  For example, in a model with humans and zombies, a human would be type 1, and zombie would be type 2.
* ElementIDGenerator - This controls a dictionary of all element types with an enumerated form of each and number for each type.  This class contains a type_dict, enum_form_duct, type_number, and process.  All of these features help the generator keep track of everything in the simulation.
* ElementDirectory - This is a dictionary of all elements and simply contains a dict.
* Scheduler  - This class controls the scheduling of events using a dictionary of events and agents to be updated at each time step. This class contains an ordered dictionary, time_series.
* Container - This is a holding bin for specific types of elements.
* Model - The model is the abstract class that handles all agent communication.  This class contains an element_directory, rank, world_size, element_requests, element_watched, element_watching, element_changes_and_watched, element_id_generator, element_forms, and a scheudler.

## Agent Synchronization

![Communication diagram illustrating communication techniques used in the MABM toolkit.](https://gitlab.mitre.org/ceharvey/MABM/raw/720c5dc7579327ffc15c77fc8596ee416b31cd8d/Images/ProcessCommms.png)
One of the novel techniques in Agent-Based modeling implemented in this toolkit is the communication process between processors.   The protocol used to synchronize agent states across processors has a significant impact on the efficiency of the tool.  Repast HPC is one of the currently available tools for distributed ABMs<ref>Collier, N., and M. North. 2013, Oct.. “Parallel agent-based simulation with Repast for High Performance Computing”. SIMULATION 89 (10): 1215–1235.</ref>.  This framework approaches the problem by performing a complete synchronization of all entities of interest at every time step.

This toolkit also implements an alternative approach to entity synchronization, a design which manages persistent, pertinent information.  This protocol performs an initial synchronization between all entities with relationships to other agents and then only performs updates and synchronization following changes to relevant information.  The pertinent data synchronization technique is an event-driven method to manage the communication and synchronization between the processors.  The conservative and the event-driven approaches are both described and analyzed in the following sections.

### Agent Requests
The conservative approach to the problem performs a consistent synchronization of pertinent information at every time step of the simulation.  Each processor cycles through their agents and compiles a list of non-local agents from which information is needed.  The root processor aggregates this information and broadcasts the requests to all processors which return the requested state information to the root processor.  Once the root processor distributes the information gathered, each processor creates local copies of their non-local agents of interest.  These temporary copies only contain necessary state information on the requested entity.  Therefore, each processor has information regarding the current state of their own agents as well as state information on all agents of interest.  This entire process is repeated at the beginning of every time step.

### Agent Watches
The alternate approach recognizes that not all pertinent information changes at every time step in the simulation.  Complete synchronization can be achieved by only tracking and reporting the changes to relevant information.  Agent watching only synchronizes information when an entity has experienced a change in state.  After the creation of a relationship between two entities, if the agent of interest is not local, it is added to a global list of watched entities.  During the synchronization process, the states of newly watched agents are communicated to any processor which has an interest in the agent. Basic, persistent local copies of these watched agents are made on the processors that require the state information of the non-local agent.  The processor uses these local copies as a source of information for the updates on their local agents.  When watched agents experience a change in state the processor sends the updated state information to the root node to be broadcast to all processors.  Then, at the start of the next time step, remote copies of agents are updated to the correct, current state.  With this method, fewer and smaller messages are sent at each time step than with the previous technique.

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

