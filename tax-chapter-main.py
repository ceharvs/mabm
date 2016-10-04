#!/home/ceharvey/local/python-2.7/bin/python
__author__ = 'jgentile', 'ceharvey'

'''
Run Instructions
mpiexec -np 2 python tax-chapter-main.py 5 0.5 20 0.5 0.5 0.5 0.5 0.5 temp

mpiexec -np 2 python tax-chapter-main.py [-h] [-w] [-l] [-W] [-P] [-s] [-n [NOTIFY]]
                           [-a [APPEND]]
                           taxpayers tax_rate t_steps penalty_rate audit_prob
                           app_rate max_audit apprehension network_file
                           prop_honest prop_dishonest

This model reads in the agent's network from an external file.
'''

import tax_model
import os
import psutil
import time
from subprocess import call
import argparse
import cProfile
import numpy.random as npr


def memory_usage_psutil():
    """
    Perform profiling of memory usage
    """
    import os
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info()[0] / float(2 ** 20)
    return mem


def main():
    """
    Generate a new instance of the tax-chapter model with:
        : taxpayers:   Total number of taxpayers
        : time_steps:  The number of discrete steps of time (also called "ticks") that occur in a single run of
                            the model. Each time step consists of each agent activating, surveying its network, and
                            making a decision based on its defining parameters.
        : tax_rate:    The income tax rate, or percent of total income that will be collected after each time
                            step.  This model assumes a flat tax, irrespective of an agent's current income or wealth.
                            This tax rate becomes important in the agent's decision making heuristic, whether or not
                            the agent will evade taxes.

        : penalty_rate:
        : audit_prob:  The objective probability that any agent that is evading taxes will be audited in any
                            given time step.
        : app_rate:    Same as audit probability.
        : max_audit:   If apprehension is True, this is the number of timesteps an imitator agent will act honestly
                       immediately after being audited.
        : apprehension: A Boolean variable, indicating whether an agent has been apprehended for tax evasion
                            (True) or not (False).
        : network_file: File to read in the network structure.
        : prop_honest: Proportion of agents that are completely honest taxpayers and will never attempt to evade
                            taxes.
        : prop_dishonest: Proportion of agents that are utility maximizers who, given their bounded rational
                            belief that they will be audited and their individual level of risk aversion, will attempt
                            to evade paying taxes as much as possible.
    """

    """
    Generate a new Tax Model using the command line parameters
    """
    # Record start time
    start_time = time.time()

    identifier = args.network_file.split("/")[1] + '_app_rate-' + str(args.app_rate) + '_rep-' + str(args.repetition)

    m = tax_model.Model(args.taxpayers, args.t_steps, args.tax_rate, args.penalty_rate, args.audit_prob,
                        args.app_rate, args.max_audit, args.apprehension, args.network_file, args.prop_honest,
                        args.prop_dishonest, identifier, args.write, args.notify)
    # Print out command line arguments
    if m.get_rank() == 0:
        print '\nModel Running with:\n\tTaxpayers = \t\t{}\n\tTime Steps = \t\t{}\n\tTax Rate = \t\t{}\n\t' \
              'Penalty Rate = \t\t{}\n\tAudit Prob = \t\t{}\n\tApp. Rate = \t\t{}\n\tMax Audit = \t\t{}\n\t' \
              'Apprehension = \t\t{}\n\tNetwork File = \t\t{}\n\t% Honest = \t\t{}\n\t% Dishonest = \t\t{}\n\t' \
              ''.format(args.taxpayers, args.t_steps, args.tax_rate, args.penalty_rate, args.audit_prob,
                        args.app_rate, args.max_audit, args.apprehension, args.network_file, args.prop_honest,
                        args.prop_dishonest)

    p = psutil.Process(os.getpid())
    #a = p.get_memory_info()

    # Use a random seed if specified in the command line
    if args.seed:
        npr.seed(10)

    # Build the agents in the model
    m.build_agents() #args.notify, args.cross, args.rumor_prob)
    if m.get_rank() == 0:
        build_mem = memory_usage_psutil()

    # Depending on the command line args, run the profile or the main
    if args.Profile:
        file_name = str(args.taxpayers)+'people_'+str(args.tax_rate)+'taxrate_'+str(args.penalty_rate)+'penaltyrate'
        if args.append:
            file_name += '_'+args.append+'.profile'
        else:
            file_name += '.profile'
        # cProfile.run('m.run()', profile_file_name)
        pr = cProfile.Profile()
        pr.enable()
        m.run()
        pr.disable()
        pr.dump_stats(profile_file_name)
    else:
        vmtr_list = m.run()

    # Record Memory
    my_file = open('memory.csv', 'a')
    if m.get_rank() == 0:
        # Split to only use the second part of network file
        # Print: network, taxpayers, number processors, memory after build, memory final
        my_file.write(args.network_file.split("/")[1]+','+str(args.taxpayers)+','+str(m.get_world_size())+','
                      +str(build_mem)+','+str(memory_usage_psutil())+'\n')

    # When finished write output to results.txt
    # Results is of the format: Network File, Processors, Apprehension Rate, Rep #, Run Time, Output
    my_file = open('results.txt', 'a')
    if m.get_rank() == 0:
        # Split to only use the second part of network file
        my_file.write(args.network_file.split("/")[1]+','+str(args.taxpayers)+','+str(m.get_world_size())+','+str(args.app_rate)+','
                      +str(args.repetition)+','+str(time.time()-start_time)+','+str(vmtr_list)+'\n')

    # If file writing is turned on, have the root node run the appropriate scripts to
    # concatenate the files if option is on
    if m.get_rank() == 0 and args.write and m.get_world_size > 1:
        if args.Linux:
            identifier += '_np-' + str(m.get_world_size()) + '_'
            my_call = 'sh fix_output.sh output/' + args.network_file.split("/")[1] + '_np-' + str(m.get_world_size()) + '_app_rate-' \
                      + str(args.app_rate) + '_rep-' + str(args.repetition) + ' ' + identifier
            call([my_call], shell=True)
        if args.Windows:
            call(['fix_output.bat'])

def run_model(model):
    model.run()

if __name__ == '__main__':
    global args

    # Necessary Command Line Arguments
    parser = argparse.ArgumentParser(description='Process command line options for the program.')
    parser.add_argument('taxpayers', help="Number of taxpayers per processor", type=int)
    parser.add_argument('tax_rate', help="Initial tax rate", type=float)
    parser.add_argument('t_steps', help="Number of time steps in the model", type=int)
    parser.add_argument('penalty_rate', help="Penalty rate", type=float)
    parser.add_argument('audit_prob', help="Probability of auditing", type=float)
    parser.add_argument('app_rate', help="Apprehension rate", type=float)
    parser.add_argument('max_audit', help="Max Audit", type=float)
    parser.add_argument('apprehension', help="True or False for apprehensions", type=bool)
    parser.add_argument('network_file', help="Specify the network file to be read in", type=str)
    parser.add_argument('prop_honest', help="Proportion of the population that is honest", type=float)
    parser.add_argument('prop_dishonest', help="Proportion of the population that is dishonest", type=float)


    # Option Flags
    parser.add_argument('-w', '--write', help="Write output files for agent knowledge and values",
                        action="store_true")
    parser.add_argument('-l', '--Linux', help="Concatenate output files using Shell Script",
                        action="store_true")
    parser.add_argument('-W', '--Windows', help="Concatenate output files using Batch Script",
                        action="store_true")
    parser.add_argument('-P', '--Profile', help="Option to include profiling for the program.  Profiling name has a "
                                                "default with num agents, num processors, rumor prob and cross-process "
                                                "probability.  You can optionally append something to the file name "
                                                "using -a.", action="store_true")
    parser.add_argument('-r', '--repetition', help="Repetition number", nargs='?', type=int)

    parser.add_argument('-s', '--seed', help="Use a random seed for the model",
                        action="store_true")

    # Optional Arguments for the Parser
    parser.add_argument('-n', '--notify', help="Give notifications after a certain number of agents"
                                               "have been created on the processor",
                        nargs='?', const=500000, type=int, default=500000)
    parser.add_argument('-a', '--append', help="Optional text to append to the profile output file name, avoids "
                                               "overwriting other files.", nargs='?', const=None, type=str, default=None)
    args = parser.parse_args()

    # Depending on the command line args, run the profile or the main
    if args.Profile:
        profile_file_name = str(args.taxpayers) + 'people_' + str(args.tax_rate) + 'taxrate_' \
                            + str(args.penalty_rate) + 'penaltyrate'
        if args.append:
            profile_file_name += '_'+args.append+'_FULL.profile'
        else:
            profile_file_name += '_FULL.profile'
        cProfile.run('main()', profile_file_name)
    else:
        main()
