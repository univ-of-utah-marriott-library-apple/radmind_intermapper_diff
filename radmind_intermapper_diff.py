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
## COPYRIGHT (c) 2014 Marriott Library IT Services.  All Rights Reserved.     ##
##                                                                            ##
## Author:          Pierce Darragh - pierce.darragh@utah.edu                  ##
## Creation Date:   November 18, 2013                                         ##
## Last Updated:    January  15, 2014                                         ##
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

## DEFINE GLOBAL VARIABLES
def set_gvars():
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
	global RADMIND_CONFIG
	global INTERMAPPER_ADDRESS
	global INTERMAPPER_DEFAULT
	
	RADMIND_CONFIG = "/radmind_server_root/radmind/config"
	INTERMAPPER_ADDRESS = "https://intermapper.address/~admin/full_screen.html"
	INTERMAPPER_DEFAULT = "./intermapper_list.html"
	
	# FLAGS
	global full
	global quiet
	
	# OTHER
	global VERSION
	
	VERSION = "1.8.0"

## MAIN
def main():
	set_gvars()
	
	parse_options()
	
	if full:
		print "Full!"
	if quiet:
		print "quiet"

## PARSE FOR OPTIONS
def parse_options():
	# Add arguments to the parser for formatting.
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
	parser.add_argument("-i", "--im-file",
						help="use specified InterMapper file")
	
	args = parser.parse_args()
	
	# Now do stuff to those arguments!
	if args.version:
		print "%s" % VERSION
		sys.exit(99)
	
	global full
	full = args.full
	global quiet
	quiet = args.quiet

## CLASSES

## CALL TO MAIN
if __name__ == "__main__":
	main()
