#!/home/ceharvey/local/python-2.7/bin/python
__author__ = 'jgentile', 'ceharvey'

'''
Run Instructions
mpiexec -np num_processors python rumor-model-main.py people_per_processor rumor_prob [options]

mpiexec -np 2 python main.py [-h] [-w] [-l] [-W] [-P] [-a [APPEND]] [-c [CROSS]] [-z [ZIPF]]
    number_of_persons rumor_prob

'''

import rumor_model
import os
import psutil
import sys
from subprocess import call
import argparse
import cProfile
import numpy.random as npr


def main():
    """
    Generate a new instance of the rumor model with:
    Number of Agents per processor, the zipF parameter, the initial probability of rumor knowledge
    and the probability of cross processes (which is not used)

    This model creates the agents in the model.
    """

    """
    Generate a new Rumor model using the command line parameters
    """
    m = rumor_model.Model(args.number_of_persons, args.zipf, args.rumor_prob,
                          args.cross, args.write, args.notify, args.requests)

    # Print out command line arguments
    if m.get_rank == 0:
        print sys.argv

    # If a random seed if requested, set the seed to 10
    if args.seed:
        npr.seed(10)

    # Build the model's agents
    m.build_agents(args.notify, args.cross, args.rumor_prob)

    # Write experiment settings to an output file
    my_file = open('o.txt', 'a')
    if m.get_rank() == 0:
        my_file.write(str(sys.argv[1])+','+str(m.get_world_size())+'\n')

    my_file.close()

    # Run the model!
    m.run()

    # If file writing is turned on, have the root node run the appropriate scripts to
    # concatenate the files if option is on.
    if m.get_rank() == 0 and args.write:
        if args.Linux:
            call(['./fix_output.sh'])
        if args.Windows:
            call(['fix_output.bat'])

# TODO: Remove this method if unnecessary
def run_model(model):
    model.run()

if __name__ == '__main__':
    global args

    # Necessary Command Line Arguments
    parser = argparse.ArgumentParser(description='Process command line options for the program.')
    parser.add_argument('number_of_persons', help="Number of people for each node to handle", type=int)
    parser.add_argument('rumor_prob', help="Initial probability of a person knowing the rumor",
                        type=float)
    # Option Flags
    parser.add_argument('-w', '--write', help="Write output files for agent knowledge and values",
                        action="store_true")
    parser.add_argument('-l', '--Linux', help="Concatenate output files using Shell Script",
                        action="store_true")
    parser.add_argument('-W', '--Windows', help="Concatenate output files using Batch Script",
                        action="store_true")
    parser.add_argument('-r', '--requests', help="Use requests System",
                        action="store_true")

    parser.add_argument('-s', '--seed', help="Use a seed for random numbers for the model",
                        action="store_true")

    # Optional Arguments for the Parser
    parser.add_argument('-c', '--cross', help="Probability of neighbors crossing to other processors.  "
                                              "To remove the probability of cross process and make the model"
                                              " completely random, set to a negative number.",
                        nargs='?', const=0.1, type=float, default=0.1)
    parser.add_argument('-n', '--notify', help="Give notifications after a certain number of agents"
                                               "have been created on the processor",
                        nargs='?', const=500000, type=int, default=500000)
    parser.add_argument('-z', '--zipf', help="Parameter for the zipf distribution to determine the number"
                                             "of neighbors a person will have",
                        nargs='?', const=3, type=float, default=3)

    args = parser.parse_args()

    main()
