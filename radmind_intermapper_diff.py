#!/usr/bin/python -tt

################################################################################
##                                                                            ##
## radmind_intermapper_diff.py                                                ##
##                                                                            ##
## This script takes the Radmind configuration file (default is ./config) and ##
## generates a list of just the IP addresses.  Then it takes the latest       ##
## InterMapper full device list and generates a list of just those IP         ##
## addresses.  Lastly, it puts the lists against one another to determine the ##
## disparity and reports this back to the user in an easily-readable format.  ##
##                                                                            ##
################################################################################
##                                                                            ##
## DETAILED USAGE INSTRUCTIONS                                                ##
##                                                                            ##
## Command-line options available:                                            ##
##                                                                            ##
##   -h : display help information and quit                                   ##
##   -v : display version information and quit                                ##
##   -f : give full output (prints all addresses)                             ##
##   -q : suppress output to the console (nice for file output)               ##
##   -x : lists all declared variables at the beginning of runtime            ##
##   -E : list all built-in exclusions and quit                               ##
##                                                                            ##
##   -i 'file' : use 'file' as InterMapper address list                       ##
##   -r 'file' : use 'file' as Radmind config file                            ##
##   -o 'file' : use 'file' as the output destination file                    ##
##               Note: there is still console output by default!              ##
##                                                                            ##
##   -s # : only print one set of results:                                    ##
##      1 : Radmind                                                           ##
##      2 : InterMapper                                                       ##
##                                                                            ##
################################################################################
##                                                                            ##
## COPYRIGHT (c) 2014 Marriott Library IT Services.  All Rights Reserved.     ##
##                                                                            ##
## Author:          Pierce Darragh - pierce.darragh@utah.edu                  ##
## Creation Date:   November 18, 2013                                         ##
## Last Updated:    January  17, 2014                                         ##
##                                                                            ##
## Permission to use, copy, modify, and distribute this software and its      ##
## documentation for any purpose and without fee is hereby granted, provided  ##
## that the above copyright notice appears in all copies and that both that   ##
## copyright notice and this permission notice appear in supporting           ##
## documentation, and that the name of The Marriott Library not be used in    ##
## advertising or publicity pertaining to distribution of the software        ##
## without specific, written prior permission. This software is supplied as-  ##
## is without expressed or implied warranties of any kind.                    ##
##                                                                            ##
################################################################################

## IMPORTS
import argparse
import sys
import re

## DEFINE GLOBAL VARIABLES
def set_gvars ():
    # COLORS
    global RS
    global FBRED
    global FBGRN
    global FBYEL
    global FBCYN
    
    RS = "\033[0m"
    FBRED = "\033[1;91m"
    FBGRN = "\033[1;92m"
    FBYEL = "\033[1;93m"
    FBCYN = "\033[1;96m"
    
    # ADDRESSES
    # Change these for your local environment!  It'll make your life easier.
    global RADMIND_CONFIG
    global INTERMAPPER_ADDRESS
    global INTERMAPPER_DEFAULT
    
    RADMIND_CONFIG = "/radmind_server_root/radmind/config"
    INTERMAPPER_ADDRESS = "https://intermapper.address/~admin/full_screen.html"
    INTERMAPPER_DEFAULT = "./intermapper_list.html"
    
    # OTHER
    global VERSION
    
    VERSION = "1.8.0"

## MAIN
def main ():
    set_gvars()
    
    parse_options()
    
    if explicit:
        print "{:10} : {}".format('full', full)
        print "{:10} : {}".format('quiet', quiet)
        print "{:10} : {}".format('im_file', im_file)
        print "{:10} : {}".format('im_address', im_address)
        print "{:10} : {}".format('rm_file', rm_file)
        print "{:10} : {}".format('out_file', out_file)
    
    rm_list = get_radmind()
    
## RADMIND ADDRESSES
def get_radmind ():
	print "Getting Radmind list...\t\t\t\t" + FBCYN + "[" + rm_file + "]" + RS
	f = open(rm_file)
	
	ip_pattern = re.compile('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
	for line in f:
		match = ip_pattern.search(line)
		if match:
			process(match)
	
	f.close()

## PARSE FOR OPTIONS
def parse_options ():
    # Add arguments to the parser.
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--version",
                        help="display the current version and quit",
                        action="store_true")
    parser.add_argument("-f", "--full",
                        help="gives full output",
                        action="store_true")
    parser.add_argument("-q", "--quiet",
                        help="don't output the lists",
                        action="store_true")
    parser.add_argument("-x", "--explicit",
                        help="show all declared variables at run-time",
                        action="store_true")
    
    parser.add_argument("-i", "--intermapper_file",
                        help="use 'file' as InterMapper file",
                        metavar='\'file\'',
                        dest='im_file',
                        default=INTERMAPPER_DEFAULT)
    parser.add_argument("-I", "--intermapper_address",
                        help="use 'address' to get InterMapper list",
                        metavar='\'address\'',
                        dest='im_address',
                        default=INTERMAPPER_ADDRESS)
    parser.add_argument("-r", "--radmind_file",
                        help="use 'file' as Radmind config file",
                        metavar='\'file\'',
                        dest='rm_file',
                        default=RADMIND_CONFIG)
    parser.add_argument("-o", "--output",
                        help="use 'file' to record results",
                        metavar='\'file\'',
                        dest='out_file',
                        default="")
    
    # Make all arguments globally accessible
    globals().update(vars(parser.parse_args()))
    
    # -v: Display version information and quit
    if version:
        print "%s" % VERSION
        sys.exit(0)
    
## CLASSES

## CALL TO MAIN
if __name__ == "__main__":
    main()

