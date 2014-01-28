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
import subprocess
import getpass
import urllib2
import socket

## MAIN
def main ():
    # Initialization
    set_gvars()
    parse_options()

    # Get the list of Radmind IPs
    rm_list = get_radmind()

    # Get the list of InterMapper IPs
    # If the user specifies a file to get them from, use that.  Otherwise,
    # attempt to connect to im_address and use a new version.
    if im_file:
        im_list = get_intermapper_file()
    else:
        im_list = get_intermapper_web()

    '''
    Attempting to sort the IP addresses, following suggestions at:
    http://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-stored-in-dictionary-in-python
    Presently it does not work properly.

    Also consider moving these four lists into just two dictionaries, with the
    entries formatted as:
        ( ip_address, hostname )
    '''
    sorted_im_list = sorted(im_list, key=lambda item: socket.inet_aton(item[0]))
    for item in sorted_im_list:
        print item

#     rm_hosts = get_hosts(rm_list)
#     im_hosts = get_hosts(im_list)
#
#     print "rm_list length:", len(rm_list)
#     print "im_list length:", len(im_list)
#     print
#     print "rm_hosts length:", len(rm_hosts)
#     print "im_hosts length:", len(im_hosts)
#     print
#     print "Radmind Hosts"
#     for x in range (0, len(rm_list)):
#         if rm_hosts[x]:
#             print "\t" + rm_list[x] + "\t" + rm_hosts[x]
#         else:
#             print "\t" + rm_list[x] + "\tNo hostname found."
#     print
#     print "InterMapper Hosts"
#     for x in range (0, len(im_list)):
#         if im_hosts[x]:
#             print "\t" + im_list[x] + "\t" + im_hosts[x]
#         else:
#             print "\t" + im_list[x] + FBYEL + "\tNo hostname found." + RS

    if explicit:
        print "\nThese variables were used:"
        print "\t{:10} : {}".format('full', full)
        print "\t{:10} : {}".format('quiet', quiet)
        print "\t{:10} : {}".format('im_file', im_file)
        print "\t{:10} : {}".format('im_address', im_address)
        print "\t{:10} : {}".format('rm_file', rm_file)
        print "\t{:10} : {}".format('out_file', out_file)

## DEFINE GLOBAL VARIABLES
def set_gvars ():
    # REGEX PATTERNS
    global IP_PATTERN   # Generic IP address

    IP_PATTERN = re.compile('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

    # COLORS
    global RS       # Reset color settings
    global FBRED    # Foreground bright red
    global FBGRN    # Foreground bright green
    global FBYEL    # Foreground bright yellow
    global FBCYN    # Foreground bright cyan
    global CARET    # Carriage return

    RS = "\033[0m"
    FBRED = "\033[1;91m"
    FBGRN = "\033[1;92m"
    FBYEL = "\033[1;93m"
    FBCYN = "\033[1;96m"
    CARET = "\r\033[K"

    # ADDRESSES
    # Change these for your local environment!  It'll make your life easier.
    global RADMIND_CONFIG       # Default location of Radmind config file
    global INTERMAPPER_ADDRESS  # Default web address of InterMapper full list

    RADMIND_CONFIG = "/radmind_server_root/radmind/config"
    INTERMAPPER_ADDRESS = "https://intermapper.address/~admin/full_screen.html"

    # OTHER
    # DON'T CHANGE THESE
    global VERSION      # Current version of the script

    VERSION = "1.8.0"

## GET HOSTNAMES
def get_host (ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        return False

## GET HOSTS LIST
def get_hosts (list):
    hosts = []
    for address in list:
        hosts.append(get_host(address))
    return hosts

## RADMIND ADDRESSES
def get_radmind ():
    matches = []
    prompt = ("Getting Radmind list from " + FBCYN + "[" + rm_file + "]" + RS
              + "...")

    print prompt,
    legit_file (rm_file, "rm", prompt)
    prompt = ("Getting Radmind list from " + FBCYN + "[" + rm_file + "]"
              + RS + "...")
    with open(rm_file) as f:
        matches = IP_PATTERN.findall(f.read())
        print CARET,
        pretty_print (prompt, 0)

    return matches

## INTERMAPPER ADDRESSES
# If InterMapper denies whitelist authentication.
def im_authenticate ():
    # Get username and password from the user.
    username = raw_input("InterMapper Username: ")
    password= getpass.getpass("InterMapper Password: ", stream=sys.stderr)

    # The following is the recommended method of authenticating to a secure
    # website, as per the Python documentation at the time of this writing.
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, im_address, username, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    opener.open(im_address)
    urllib2.install_opener(opener)

def get_intermapper_web ():
    prompt = ("Getting InterMapper list from " + FBCYN + "[" + im_address + "]"
              + RS + "...")

    print prompt,
    while True:
        try:
            page = urllib2.urlopen(im_address).read()
            matches = IP_PATTERN.findall(page)
            print CARET,
            pretty_print (prompt, 0)
            return matches
        except urllib2.HTTPError as e:
            print CARET,
            pretty_print (prompt, 1)
            print ("HTTP Error", e.code)
            print (RS + "You are not authorized to access " + FBCYN + "'"
                   + im_address + "'" + RS + ".")
            print "Attempting authentication..."
            im_authenticate()
        except urllib2.URLError as e:
            print CARET,
            pretty_print (prompt, 1)
            print ("Error: The address " + FBCYN + "'"
                   + im_address + "'" + RS + " could not be accessed.")
            print "Reason:", e.reason
            sys.exit(1)

def get_intermapper_file ():
    matches = []
    prompt = ("Getting InterMapper list from " + FBCYN + "[" + im_file + "]"
              + RS + "...")

    print prompt,

    legit_file (im_file, "im", prompt)
    prompt = ("Getting InterMapper list from " + FBCYN + "[" + im_file + "]"
              + RS + "...")
    with open(im_file) as f:
        matches = IP_PATTERN.findall(f.read())
        print CARET,
        pretty_print (prompt, 0)

    return matches


## CHECK FILE LEGITIMACY
# Determines whether an inputted file is able to be opened.  If not,
# print the error message.
def legit_file (location, switch, prompt = ''):
    try:
        with open(location) as f:
            return
    except IOError as e:
        if prompt:
            print CARET,
            pretty_print (prompt, 1)
        print "Error:", e.strerror + "."
        if switch == "im":
            print "Try using the [-i] switch to specify the file manually."
        elif switch == "rm":
            print "Try using the [-r] switch to specify the file manually."
        sys.exit(1)
        return

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
                        default='')
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

## PROPER SPACING FOR RESULTS
def pretty_print (s, i):
    if len(s) < 70:
        if i == 0:
            print "\b" + s + " " * (85 - len(s)) + FBGRN + "[done]" + RS
        elif i == 1:
            print "\b" + s + " " * (83 - len(s)) + FBRED + "[failed]" + RS
        else:
            print "\b" + " " * (91 - len(s)) + s
    else:
        print "\b" + s
        if i == 0:
            print " " * 74 + FBGRN + "[done]" + RS
        elif i == 1:
            print " " * 72 + FBRED + "[failed]" + RS

## CALL TO MAIN
if __name__ == "__main__":
    main()

