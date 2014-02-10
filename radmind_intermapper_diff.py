#!/usr/bin/python -tt

'''
################################################################################

radmind_intermapper_diff.py

This script takes the Radmind configuration file (default is ./config) and
generates a list of just the IP addresses.  Then it takes the latest InterMapper
full device list and generates a list of just those IP addresses.  Lastly, it
puts the lists against one another to determine the disparity and reports this
back to the user in an easily-readable format.

################################################################################

DETAILED USAGE INSTRUCTIONS

Command-line options available:

  -h : display help information and quit
  -v : display version information and quit
  -f : give full output (prints all addresses)
  -q : suppress output to the console (nice for file output)
  -x : lists all declared variables at the beginning of runtime
  -E : list all built-in exclusions and quit

  -r 'file' : use 'file' as Radmind config file
  -i 'file' : use 'file' as InterMapper address list
  -I 'address' : use 'address' as InterMapper web address
  -o 'file' : use 'file' as the output destination file
              Note: there is still console output by default!

  -s # : only print one set of results:
     1 : Radmind
     2 : InterMapper

################################################################################

COPYRIGHT (c) 2014 Marriott Library IT Services.  All Rights Reserved.

Author:          Pierce Darragh - pierce.darragh@utah.edu
Creation Date:   November 18, 2013
Last Updated:    February 10, 2014

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted, provided that
the above copyright notice appears in all copies and that both that copyright
notice and this permission notice appear in supporting documentation, and that
the name of The Marriott Library not be used in advertising or publicity
pertaining to distribution of the software without specific, written prior
permission. This software is supplied as-is without expressed or implied
warranties of any kind.

################################################################################
'''

'''
################################################################################
IMPORTS
################################################################################
'''
import argparse
import getpass
import math
import re
import socket
import subprocess
import sys
import textwrap
import traceback
import urllib2

'''
################################################################################
MAIN

    Program overview:
    1.      Initialization
    1.1.      Set the global variables
    1.2.      Parse for command line options
    2.      Get address lists
    2.1.      Radmind addresses
    2.2.      InterMapper addresses
    3.      Get hostnames for IPs
    3.1.      Radmind hostnames
    3.2.      InterMapper hostnames
    4.      Sort IP addresses
    4.1.      Radmind addresses
    4.2.      InterMapper addresses
    5.      Find disparities
    5.1.      Radmind positive disparity (Radmind has, InterMapper doesn't)
    5.2.      InterMapper positive dispairty (InterMapper has, Radmind doesn't)
    6.      File output
    7.      Console output
################################################################################
'''
def main ():
    # Initialization
    set_gvars()
    parse_options()

    # If the user specified the explicit option, show all of the variables used.
    if explicit:
        print "\nThese variables were used:"
        print "\t{:10} : {}".format('full', full)
        print "\t{:10} : {}".format('quiet', quiet)
        print "\t{:10} : {}".format('im_file', im_file)
        print "\t{:10} : {}".format('im_address', im_address)
        print "\t{:10} : {}".format('rm_file', rm_file)
        print "\t{:10} : {}".format('out_file', out_file)
        print

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
    print "Getting Radmind hostnames..."
    rm_stuff = {}
    rm_longest = 0
    for i in range(0, len(rm_list)):
        update_progress(i/float(len(rm_list)))
        item = rm_list[i]
        if len(item) > rm_longest:
            rm_longest = len(item)
        rm_stuff[item] = str(get_host(item)).replace("'", "")
    update_progress()

    # Get the hostnames for InterMapper IPs
    print "Getting InterMapper hostnames..."
    im_stuff = {}
    im_longest = 0
    for i in range(0, len(im_list)):
        update_progress(i/float(len(im_list)))
        item = im_list[i]
        if len(item) > im_longest:
            im_longest = len(item)
        im_stuff[item] = str(get_host(item)).replace("'", "")
    update_progress()

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
    print "Finding Radmind positive disparity..."
    rm_diff = differences(rm_sorted, im_sorted)
    # Find the InterMapper positive disparities
    print "Finding InterMapper positive disparity..."
    im_diff = differences(im_sorted, rm_sorted)

    if out_file:
        file_output()

    if not quiet:
        print "\n"
        if full:
            # Full console output
            print "Radmind items (" + str(len(rm_stuff)) + "):"
            for item in rm_sorted:
                if not item[1] == "False":
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), item[1])
                else:
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL + "No DNS Entry" + RS)

            print
            print "InterMapper items (" + str(len(im_stuff)) + "):"
            for item in im_sorted:
                if not item[1] == "False":
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), item[1])
                else:
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL + "No DNS Entry" + RS)
        else:
            # Differences console output
            print "Radmind items (" + str(len(rm_diff)) + "):"
            for item in rm_diff:
                if not item[1] == "False":
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), item[1])
                else:
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL + "No DNS Entry" + RS)

            print
            print "InterMapper items (" + str(len(im_diff)) + "):"
            for item in im_diff:
                if not item[1] == "False":
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), item[1])
                else:
                    print "  {0:<{1}} {2}".format(item[0], (longest + 2), FBYEL + "No DNS Entry" + RS)

'''
################################################################################
OUTPUT TO FILE

    If the user specifies the '-o' option for output, this handles the
    formatting and writing of that file.
################################################################################
'''
def file_output ():
    print "Outputting to file..."
    return

'''
################################################################################
DEFINE GLOBAL VARIABLES

    A few variables are used throughout this script, and they are defined here.
################################################################################
'''
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

    VERSION = "2.0.0"

'''
################################################################################
GET HOSTNAME

    Takes an IP address and attempts to find a valid hostname for that address.
    If none is found, False is stored in its place.
################################################################################
'''
def get_host (ip):
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        if dns_full:
            return host
        else:
            return host.split('.')[0]
    except Exception:
        return False

'''
################################################################################
RADMIND FILE

    Scans the Radmind config file (usually located at /var/radmind/config) and
    records all of the IP addresses that appear at the beginnings of lines, and
    then returns those as a list.
################################################################################
'''
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

'''
################################################################################
INTERMAPPER AUTHENTICATION

    If InterMapper denies whitelist authentication (say, because you aren't on
    the appropriate network), you may be able to attempt HTTPS authentication.
    This attempts that authentication, as per the method described in the Python
    documentation.
################################################################################
'''
def im_authenticate ():
    # Get username and password from the user.
    print "Please provide credentials."
    username = raw_input("  InterMapper Username: ")
    password= getpass.getpass("  InterMapper Password: ", stream=sys.stderr)
    prompt = "Attempting authentication..."
    pretty_print (prompt)

    # The following is the recommended method of authenticating to a secure
    # website, as per the Python documentation at the time of this writing.
    try:
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, im_address, username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        opener.open(im_address)
        urllib2.install_opener(opener)
        pretty_print(prompt, 1)
    except:
        pretty_print(prompt, 2)
        print "Something went wrong during authentication.  Quitting..."
        sys.exit(1)

'''
################################################################################
INTERMAPPER WEB

    InterMapper has a webpage with all of the IP addresses for its monitored
    devices.  Try to access that page and return a list containing all of those
    IP addresses
################################################################################
'''
def get_intermapper_web ():
    prompt = "Getting InterMapper list from [" + im_address + "]..."
    matches = []

    pretty_print (prompt)
    while True:
        try:
            page = urllib2.urlopen(im_address).read()
            pretty_print (prompt, 1)
            break;
        except urllib2.HTTPError as e:
            pretty_print (prompt, 2)
            print "HTTP Error", e.code
            message = "You are not authorized to access the addres: [" + im_address + "]"
            pretty_print (message)
            print
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

    matches = IP_PATTERN.findall(page)
    return matches

'''
################################################################################
INTERMAPPER FILE

    In the event that a file is specified which contains all of the IP addresses
    for InterMapper, this will try to record them all.
################################################################################
'''
def get_intermapper_file ():
    matches = []
    prompt = "Getting InterMapper list from [" + im_file + "]..."

    pretty_print (prompt)

    legit_file (im_file, "im", prompt)
    with open(im_file) as f:
        matches = IP_PATTERN.findall(f.read())
        pretty_print (prompt, 1)

    return matches

'''
################################################################################
FIND DISPARITY

    Takes in two dictionaries, which are assumed to be formatted as:
        {IP_Address, hostname}
    and finds out which items exist in the first list, but not the second.
################################################################################
'''
def differences (positive, negative):
    different = []
    for i in range (0, len(positive)):
        update_progress(i/float(len(positive)))
        if not (compare (positive[i][0], negative)):
            different.append(positive[i])
    update_progress()
    return different

def compare (value, list):
    for other in list:
        if value == other[0]:
            return True
    return False

'''
################################################################################
CHECK FILE LEGITIMACY

    To ensure that any of the specified files to be used are actually valid, we
    try to open them up.  If it works, return.  Otherwise, give the error
    message and quit.
################################################################################
'''
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

'''
################################################################################
PARSE FOR OPTIONS

    This takes in any command-line arguments and interprets them appropriately.
    Valid options include:
        -h, --help
        -v, --version
        -f, --full
        -q, --quiet
        -x, --explicit
        -d, --dns_full

        -r, --radmind_file 'file'
        -i, --intermapper_file 'file'
        -I, --intermapper_address 'address'
        -o, --output 'file'
################################################################################
'''
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
    parser.add_argument("-d", "--dns_full",
                        help="leave the full DNS names intact",
                        action="store_true")

    parser.add_argument("-r", "--radmind_file",
                        help="use 'file' as Radmind config file",
                        metavar='\'file\'',
                        dest='rm_file',
                        default=RADMIND_CONFIG)
    parser.add_argument("-i", "--intermapper_file",
                        help="use 'file' as InterMapper file",
                        metavar='\'file\'',
                        dest='im_file',
                        default=None)
    parser.add_argument("-I", "--intermapper_address",
                        help="use 'address' to get InterMapper list",
                        metavar='\'address\'',
                        dest='im_address',
                        default=INTERMAPPER_ADDRESS)
    parser.add_argument("-o", "--output",
                        help="use 'file' to record results",
                        metavar='\'file\'',
                        dest='out_file',
                        default=None)

    # Make all arguments globally accessible
    globals().update(vars(parser.parse_args()))

    # -v: Display version information and quit
    if version:
        print "{}".format(VERSION)
        sys.exit(0)

'''
################################################################################
PROPER SPACING FOR FORMATTING

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

'''
################################################################################
PROGRESS BAR

    A progress bar can be useful for a user.  This method was copied (with some
    slight alterations) from Brian Khuu's post here:
        http://stackoverflow.com/questions/3160699/python-progress-bar
################################################################################
'''
def update_progress(progress=1):
    # Modify this to change the length of the progress bar:
    barLength = 50
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "Error: progress var must be float.\r\n"
    if progress < 0:
        progress = 0
        status = "[failed]\r\n"
    if progress >= 1:
        progress = 1
        status = "  [done]\r\n"
    amount = math.ceil(progress*1000)/10
    block = int(round(barLength*progress))
    text = "\r    [{0}] {1:>5}%{2:>{3}}".format( "#"*block + "-"*(barLength-block),
                                            amount,
                                            status,
                                            24 - len(str(amount)) )
    sys.stdout.write(text)
    sys.stdout.flush()

'''
################################################################################
CALL TO MAIN()

    This is our entry point.  It's kind of a big deal.
################################################################################
'''
if __name__ == "__main__":
    main()
