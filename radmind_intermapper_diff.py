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
import traceback
import textwrap

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

    # Get the hostnames for Radmind IPs
    rm_stuff = {}
    rm_longest = 0
    for item in rm_list:
        if len(item) > rm_longest:
            rm_longest = len(item)
        rm_stuff[item] = str(get_host(item)).replace("'", "")

    # Get the hostnames for InterMapper IPs
    im_stuff = {}
    im_longest = 0
    for item in im_list:
        if len(item) > im_longest:
            im_longest = len(item)
        im_stuff[item] = str(get_host(item)).replace("'", "")

    '''
    Sort the IP addresses.

    The following sort method was detailed in an answer by Ferdinand Beyer to
    the question "How to sort IP addresses stored in dictionary in Python?" at:
        http://stackoverflow.com/questions/6545023/how-to-sort-ip-addresses-
        stored-in-dictionary-in-python
    It returns the values with the IP addresses sorted properly, and keeps
    their hostnames attached.
    '''
    rm_sorted = []
    im_sorted = []
    try:
        rm_sorted = sorted(rm_stuff.items(),
                           key=lambda item: socket.inet_aton(item[0]))
        im_sorted = sorted(im_stuff.items(),
                           key=lambda item: socket.inet_aton(item[0]))
    except:
        traceback.print_exc(file=sys.stdout)

    longest = rm_longest if (rm_longest > im_longest) else im_longest

    # Find the Radmind positive disparities
    rm_diff = differences(rm_sorted, im_sorted)
    # Find the InterMapper positive disparities
    im_diff = differences(im_sorted, rm_sorted)

    if out_file:
        file_output()

    if not quiet:
        if full:
            # Full console output
            print "Radmind items (" + str(len(rm_stuff)) + "):"
            for item in rm_sorted:
                if not item[1] == "False":
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2),
                                                   item[1]))
                else:
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL
                                                   + "No DNS Entry" + RS))

            print
            print "InterMapper items (" + str(len(im_stuff)) + "):"
            for item in im_sorted:
                if not item[1] == "False":
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2),
                                                   item[1]))
                else:
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL
                                                   + "No DNS Entry" + RS))
        else:
            # Differences console output
            print "Radmind items (" + str(len(rm_diff)) + "):"
            for item in rm_diff:
                if not item[1] == "False":
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2),
                                                   item[1]))
                else:
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL
                                                   + "No DNS Entry" + RS))

            print
            print "InterMapper items (" + str(len(im_diff)) + "):"
            for item in im_diff:
                if not item[1] == "False":
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2),
                                                   item[1]))
                else:
                    print ("  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL
                                                   + "No DNS Entry" + RS))

    # If the user specified the explicit option, show all of the variables used.
    if explicit:
        print "\nThese variables were used:"
        print "\t{:10} : {}".format('full', full)
        print "\t{:10} : {}".format('quiet', quiet)
        print "\t{:10} : {}".format('im_file', im_file)
        print "\t{:10} : {}".format('im_address', im_address)
        print "\t{:10} : {}".format('rm_file', rm_file)
        print "\t{:10} : {}".format('out_file', out_file)

def file_output ():
    print "Outputting to file..."
    return

## DEFINE GLOBAL VARIABLES
def set_gvars ():
    # REGEX PATTERNS
    global IP_PATTERN   # Generic IP address
    global RM_PATTERN   # Radmind shorthand addresses: a.b.c.<d-e>
    global RM_3         # Radmind three-deep match: 'a.b.c.'
    global RM_FIRST     # Radmind first match: d in a.b.c.<d-e>
    global RM_LAST      # Radmind last match: e in a.b.c.<d-e>

    IP_PATTERN = re.compile('\d+\.\d+\.\d+\.\d+')
    RM_PATTERN = re.compile('\d+\.\d+\.\d+\.[^\s)]+')
    RM_3       = re.compile('\d+\.\d+\.\d+\.')
    RM_FIRST   = re.compile('<(\d+)')
    RM_LAST    = re.compile('(\d+)>')

    # COLORS
    global RS       # Reset color settings
    global FBRED    # Foreground bright red
    global FBGRN    # Foreground bright green
    global FBYEL    # Foreground bright yellow
    global FBCYN    # Foreground bright cyan
    global CARET    # Carriage return

    RS    = "\033[0m"
    FBRED = "\033[1;91m"
    FBGRN = "\033[1;92m"
    FBYEL = "\033[1;93m"
    FBCYN = "\033[1;96m"
    CARET = "\r\033[K"

    # ADDRESSES
    # Change these for your local environment!  It'll make your life easier.
    global RADMIND_CONFIG       # Default location of Radmind config file
    global INTERMAPPER_ADDRESS  # Default web address of InterMapper full list

    RADMIND_CONFIG      = "/radmind_server_root/radmind/config"
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

## RADMIND ADDRESSES
def get_radmind ():
    matches = []
    prompt = "Getting Radmind list from [" + rm_file + "]..."

    pretty_print (prompt)
    legit_file (rm_file, "rm", prompt)
    addresses = []
    with open(rm_file) as f:
        for line in f:
            result = RM_PATTERN.match(line)
            if result:
                addresses.append(result.group(0))

    for item in addresses:
        first = RM_FIRST.findall(item)
        if first:
            base = RM_3.findall(item)
            last = RM_LAST.findall(item)
            for x in range (int(first[0]), int(last[0]) + 1):
                full = base[0] + str(x)
                matches.append(full)
        else:
            if not re.search('-', item):
                matches.append(item)

    pretty_print (prompt, 1)

    return matches

## INTERMAPPER ADDRESSES
# If InterMapper denies whitelist authentication.
def im_authenticate ():
    # Get username and password from the user.
    username = raw_input("InterMapper Username: ")
    password= getpass.getpass("InterMapper Password: ", stream=sys.stderr)

    # The following is the recommended method of authenticating to a secure
    # website, as per the Python documentation at the time of this writing.
    try:
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, im_address, username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        opener.open(im_address)
        urllib2.install_opener(opener)
    except:
        print "Something went wrong during authentication.  Quitting..."
        sys.exit(1)

def get_intermapper_web ():
    prompt = "Getting InterMapper list from [" + im_address + "]..."

    pretty_print (prompt)
    while True:
        try:
            page = urllib2.urlopen(im_address).read()
            matches = IP_PATTERN.findall(page)
            pretty_print (prompt, 1)
            return matches
        except urllib2.HTTPError as e:
            pretty_print (prompt, 2)
            print "HTTP Error", e.code
            message = ("You are not authorized to access the addres: ["
                       + im_address + "]")
            pretty_print (message)
            print
            print "Attempting authentication..."
            im_authenticate()
        except urllib2.URLError as e:
            pretty_print (prompt, 2)
            message = "Error:  The address could not be accessed."
            pretty_print (message)
            print
            print "Reason:", e.reason
            sys.exit(1)
        except Exception as e:
            pretty_print (prompt, 2)
            print e.print_stack()
            sys.exit(1)

def get_intermapper_file ():
    matches = []
    prompt = ("Getting InterMapper list from " + FBCYN + "[" + im_file + "]"
              + RS + "...")

    print prompt,

    legit_file (im_file, "im", prompt)
    with open(im_file) as f:
        matches = IP_PATTERN.findall(f.read())
        print CARET,
        pretty_print (prompt, 1)

    return matches

## FIND DISPARITY
# Takes in two dictionaries, assumed to be formatted as:
#   IP_Address, hostname
# and finds out which items exist in the first list and not the second.
def differences (positive, negative):
    different = []
    for index in range (0, len(positive)):
        if not (compare (positive[index][0], negative)):
            different.append(positive[index])
    return different

def compare (value, list):
    for other in list:
        if value == other[0]:
            return True
    return False

## CHECK FILE LEGITIMACY
# Determines whether an inputted file is able to be opened.  If not,
# print the error message.
def legit_file (location, switch, prompt = ''):
    try:
        with open(location) as f:
            return
    except IOError as e:
        if prompt:
            pretty_print (prompt, 2)
        print
        print "Error:", e.strerror + "."
        if switch == "im":
            print "Try using the [-i] switch to specify the file manually."
        elif switch == "rm":
            print "Try using the [-r] switch to specify the file manually."
        sys.exit(1)

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
                        default='')

    # Make all arguments globally accessible
    globals().update(vars(parser.parse_args()))

    # -v: Display version information and quit
    if version:
        print "{}".format(VERSION)
        sys.exit(0)

'''
################################################################################
PROPER SPACING FOR RESULTS

    The proper way to use this method is to first create a string to hold your
    message; we'll call ours MESSAGE.  Then do:
        pretty_print (MESSAGE)
    This sets up the formatting by outputting the text, without inserting a
    newline at the end.  Then call:
        pretty_print (MESSAGE, 1)        // or 2 for [failed]
    This will append the "[done]" message, right-aligned at 80 characters.
################################################################################
'''
def pretty_print (s, i = 0):
    # Create the wrapped text.
    # By default, it will wrap at 70 characters.
    dedented_text = textwrap.dedent(s).strip()
    text = textwrap.fill(dedented_text,
                         initial_indent='',
                         subsequent_indent='    ')
    # The text gets put in this array so we can find the length of the last
    # line to properly format the "[done]" and "[failed]" messages.
    lines = []
    for line in text.split('\n'):
        lines.append(line)
    # Success
    if i == 1:
        print "{0:>{1}}".format("[done]", 79 - len(lines[-1]))
    # Failure
    elif i == 2:
        print "{0:>{1}}".format("[failed]", 79 - len(lines[-1]))
    # Print the message
    else:
        print text,

## CALL TO MAIN
if __name__ == "__main__":
    main()

