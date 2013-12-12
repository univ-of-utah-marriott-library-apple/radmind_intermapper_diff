#!/bin/bash

################################################################################
##                                                                            ##
## radmind_intermapper_diff.sh                                                ##
##                                                                            ##
## This script takes the Radmind configuration file (default is ./config) and ##
## generates a list of just the IP addresses.  Then it takes the latest       ##
## InterMapper full device list and generates a list of just those IP         ##
## addresses.  Lastly, it puts the lists against one another to determine the ##
## disparity and reports this back to the user in an easily-readable format.  ##
##                                                                            ##
################################################################################
## COPYRIGHT (c) 2013 Marriott Library IT Services.  All Rights Reserved.     ##
##                                                                            ##
## Author:          Pierce Darragh - pierce.darragh@utah.edu                  ##
## Creation Date:   November 18, 2013                                         ##
## Last Updated:    December 11, 2013                                         ##
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

## EXCLUSIONS
# Radmind Exclusions
# If you have an IP address in Radmind that you don't want to be monitored by
# InterMapper, then put it into this array.  We have none, so... it's empty.
declare -a rm_exclude=(
                        )

# InterMapper Exclusions
# If you have an IP address that InterMapper monitors that you don't have in
# Radmind and you never will, put it into this array.
declare -a im_exclude=(
                        )

## GLOBAL VARIABLE DECLARATION (CONFIGURATION)
RADMIND_CONFIG="/var/radmind/config"
INTERMAPPER_ADDRESS="https://intermapper.scl.utah.edu/~admin/full_screen.html"
INTERMAPPER_DEFAULT="./intermapper_list.html"

## OTHER VARIABLES (DON'T CHANGE)
VERSION="1.7.1"
OUTPUTTING=0

## COLORS
# These are used for more user-friendly output.
RS="\033[0m"
FBRED="\033[1;91m"
FBGRN="\033[1;92m"
FBYEL="\033[1;93m"
FBCYN="\033[1;96m"

## MISCELLANEOUS FUNCTIONS
# Prints specified number of dashes.
# If no argument supplied, calls line.
printd () {
    if [ -z "$1" ]; then
        echo
    else
        for (( i=0; i<$1; i++ )); do
            echo -en "-"
        done
    fi
}

# Checks to make sure the specified extra exclusions are valid; that is, the
# first part of the string is either 1 or 2 (Radmind or InterMapper,
# respectively), and then the rest are IP addresses [0-9]+.[0-9]+.[0-9].[0-9]+
check_exclusions () {
    echo "Checking exclusions..."
    echo "$1"
    IFS='~,/' read -ra arr <<< "$1"
    for item in ${arr[@]}; do
        echo "$item"
    done
    echo "Checking input: ${arr[0]}"
    if [[ "${arr[0]}" -ne 1 && "${arr[0]}" -ne 2 ]]; then
        echo "ERROR: Bad exclusion option."
        echo "       Please enter 1 (Radmind) or 2 (InterMapper) first."
        exit 1
    elif [[ "${arr[0]}" -eq 1 ]]; then
        echo "Radmind Exclusion"
        exit 0
    elif [[ "${arr[0]}" -eq 2 ]]; then
        echo "InterMapper Exclusion"
        exit 0
    else
        echo "Uh-oh..."
        exit 1
    fi
}

# Gets the username and password to retrieve information from the InterMapper
# server.
im_authenticate () {
    read -p "InterMapper Username: " im_user
    read -s -p "InterMapper Password: " im_pass
    echo

    curl --user "${im_user}":"${im_pass}" -so "${INTERMAPPER_DEFAULT}" \
         "${INTERMAPPER_ADDRESS}"

    if [[ `grep "The name/password pair you entered is incorrect." \
                 "${INTERMAPPER_DEFAULT}"` ]]; then
        echo "The name/password pair you entered is incorrect."
        rm "${INTERMAPPER_DEFAULT}"
        exit 1
    fi
}

## USAGE
# Remind the user how to use the script.
usage () {
    name=`basename $0 .sh`
    echo "${name}, version ${VERSION}"
    echo
    echo "usage: ${name} [-hvfgnq]"
    echo -en "        "
    for (( i=0; i<"${#name}"; i++ )); do
        echo -en " "
    done
    echo "[-c] radmind_file [-i] IM_file [-o] output_file"
    echo -en "        "
    for (( i=0; i<"${#name}"; i++ )); do
        echo -en " "
    done
    echo "[-s] (1|2)"
    for (( i=0; i<"${#name}"; i++ )); do
        echo -en " "
    done
    echo -en "        "
    echo "[-e] (1|2);address1;address2;..."
    echo
    echo "  h : display this help"
    echo "  v : display the current version"
    echo "  f : gives full output (lists all addresses found)"
    echo "  g : only get the input addresses"
    echo "  n : don't find the disparity between lists"
    echo "  q : quiet mode - don't display the lists"
    echo "  E : list all built-in exclusions and quit"
    echo
    echo "  c file : use 'file' as the Radmind config file"
    echo "  i file : use 'file' as the InterMapper file"
    echo "  o file : use 'file' as the output file"
    echo "           Note: there is still console output"
    echo
    echo "  s # : only print one set of results"
    echo "    1 : Radmind"
    echo "    2 : InterMapper"
    echo
    echo "  e #~address : add 'address' as an exclusion to the # list;"
    echo "                delimiters: ~ , /"
    echo "    1         : Radmind"
    echo "    2         : InterMapper"
}

## OPTIONS
# Switch for possible specified options.
while getopts ":hvfnqc:i:o:s:e:" opt
do
    case $opt in
    ## Options
    h)  # Helpful information (sort of)
        usage
        exit 0
        ;;
    v)  # Get version information
        echo "`basename $0 .sh`, version ${VERSION}"
        exit 0
        ;;
    f)  # Print all addresses
        full=1
        ;;
    g)  # Only get the input addresses
        only_get=1
        ;;
    n)  # Don't actually find the disparities
        no_disp=1
        ;;
    q)  # Quiet mode - don't display lists
        quiet=1
        ;;
    c)  # Radmind config file location
        rm_file="$OPTARG"
        ;;
    i)  # Specifies the InterMapper input file
        im_file="$OPTARG"
        ;;
    o)  # Specifies an output file for the list of IPs
        output="$OPTARG"
        ;;
    s)  # Simple output (only one set of results)
        simple="$OPTARG"
        ;;
    e)  # Specify exclusions
        check_exclusions "${OPTARG}"
        ;;
    ## Catches
    :)  # Some options require arguments - don't let the user forget them!
        echo "ERROR: Option -$OPTARG requires an argument."
        usage
        exit 1
        ;;
    \?)  # Report non-working options
        echo "ERROR: Invalid option: -$OPTARG"
        usage
        exit 1
        ;;
    *)  # Default (no options specified)
        usage
        exit 0
        ;;
    esac
done

## PRELIMINARY CONFIGURATION
# Radmind config file
if [[ -z "${rm_file}" ]]; then
    if [[ -f "${RADMIND_CONFIG}" ]]; then
        rm_file=config
    else
        echo "ERROR: No Radmind config file specified or found."
        usage
        exit 1
    fi
fi
# InterMapper device list
if [[ -z "${im_file}" ]]; then
    if [[ -f "${INTERMAPPER_DEFAULT}" ]]; then
        if [[ `grep "is not authorized to access this document from" \
               "${INTERMAPPER_DEFAULT}"` ]]; then
            echo "Invalid InterMapper file: ${INTERMAPPER_DEFAULT}"
            echo "Deleting..."
            rm "${INTERMAPPER_DEFAULT}"
            exit 1
        elif [[ `grep "The name/password pair you entered is incorrect." \
                 "${INTERMAPPER_DEFAULT}"` ]]; then
            echo "Invalid InterMapper file: ${INTERMAPPER_DEFAULT}"
            echo "Deleting..."
            rm "${INTERMAPPER_DEFAULT}"
            exit 1
        else
            im_file="${INTERMAPPER_DEFAULT}"
        fi
    else
        echo "Attempting to download InterMapper list from:"
        echo -e "\t${INTERMAPPER_ADDRESS}"
        curl -so "${INTERMAPPER_DEFAULT}" "${INTERMAPPER_ADDRESS}"
        if [[ $? -ne 0 ]]; then
            echo "ERROR: Curl failed.  Error code $?."
            exit 1
        fi
        if [[ `grep "is not authorized to access this document from" \
               "${INTERMAPPER_DEFAULT}"` ]]; then
            echo "You need to be authorized to do that:"
            im_authenticate
        fi
        im_file="${INTERMAPPER_DEFAULT}"
    fi
fi
# Simple output
# Make sure the option is either 1 or 2.
if [[ -n "${simple}" ]]; then
    if [[ "${simple}" -ne 1 && "${simple}" -ne 2 ]]; then
        echo "ERROR: Invalid simple option: ${simple}"
        echo "Terminating..."
        exit 1
    fi
fi

## RADMIND ADDRESSES
# Take the input from the $rm_file and strip it down to just addresses.
IP3="[0-9]*\.[0-9]*\.[0-9]*\."
rm_list=$(egrep "^${IP3}" ${rm_file} | sed -E "s~(.*[0-9]|\>)[[:space:]].*~\1~")

# Radmind uses a shorthand form of:
#    1.2.3.<4-7>
# This indicates that all the addresses 1.2.3.4 - 1.2.3.7 (inclusive) are all
# being used.  This loop expands those out into individual addresses.
get_radmind () {
    echo -e "Getting Radmind list...\t\t\t\t${FBCYN}[${rm_file}]${RS}"
    for address in ${rm_list}; do
        if [[ ${address} =~ (.*)\<([0-9]*)-([0-9]*)\>$ ]]; then
            base="${BASH_REMATCH[1]}"
            bottom="${BASH_REMATCH[2]}"
            top="${BASH_REMATCH[3]}"
            for ((i=${bottom}; i<=${top}; ++i)); do
                rm_result=("${rm_result[@]}" "${base}${i}")
            done
        else
            rm_result=("${rm_result[@]}" "${address}")
        fi
    done
}

## INTERMAPPER ADDRESSES
# InterMapper has a very poorly-designed HTMl page that bash hates dealing
# with.  So we'll just quickly pull out anything that looks like an IP.
get_intermapper () {
    echo -e "Getting InterMapper list...\t\t\t${FBCYN}[${im_file}]${RS}"
    for address in `cat ${im_file}`; do
        if [[ ${address} =~ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ ]]; then
            current="${BASH_REMATCH[0]}"
            if [ "${current}" != "${previous}" ]; then
                im_result=("${im_result[@]}" "${current}")
            fi
            previous=$current
        fi
    done
}

# RADMIND POSITIVE DISPARITY
# This will yield the addresses only in the Radmind config.
radmind_disp () {
    match=0
    for (( i=0; i<"${#rm_result[@]}"; i++ )); do
        match=0
        for (( j=0; j<"${#im_result[@]}"; j++ )) ; do
            if [ "${rm_result[$i]}" == "${im_result[$j]}" ]; then
                match=1
                break
            fi
        done
        if [ "${match}" -eq 0 ]; then
            rm_disp=("${rm_disp[@]}" "$i")
        fi
        echo -en "\rChecking Radmind positive disparity..."
        echo -en "\t\t${FBRED}($((100*(i+1)/${#rm_result[@]}))%)${RS}"
    done
    echo -en "\rChecking Radmind positive disparity..."
    echo -e "\t\t${FBGRN}[done]${RS}"
}

# INTERMAPPER POSITIVE DISPARITY
# This wil yield the addresses only in the InterMapper list.
intermapper_disp () {
    match=0
    for (( i=0; i<"${#im_result[@]}"; i++ )); do
        match=0
        for (( j=0; j<"${#rm_result[@]}"; j++ )); do
            if [ "${im_result[$i]}" == "${rm_result[$j]}" ]; then
                match=1
                break
            fi
        done
        if [ "${match}" -eq 0 ]; then
            im_disp=("${im_disp[@]}" "$i")
        fi
        echo -en "\rChecking InterMapper positive disparity..."
        echo -en "\t${FBRED}($((100*(i+1)/${#rm_result[@]}))%)${RS}"
    done
    echo -en "\rChecking InterMapper positive disparity..."
    echo -e "\t${FBGRN}[done]${RS}"
}

## HOSTNAMES
# Hostname-getting command
found_host=""
get_host () {
    if [[ "$1" =~ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ ]]; then
        found_host=$(host -W 2 "$1" | cut -d ' ' -f 5 | cut -d '.' -f 1)
    else
        echo "ERROR: Hostname formatting: \"$1\""
        exit 1
    fi
}

# Radmind hostnames
radmind_hostnames () {
    echo -en "Finding Radmind hostnames..."
    for (( i=0; i<"${#rm_result[@]}"; i++ )); do
        get_host ${rm_result[$i]}
        rm_hosts=("${rm_hosts[@]}" "${found_host}")
        echo -en "\rFinding Radmind hostnames..."
        echo -en "\t\t\t${FBRED}($((100*(i+1)/${#rm_result[@]}))%)${RS}"
    done
    echo -en "\rFinding Radmind hostnames..."
    echo -e "\t\t\t${FBGRN}[done]${RS}"
}

# InterMapper hostnames
intermapper_hostnames () {
    echo -en "Finding InterMapper hostnames..."
    for (( i=0; i<"${#im_result[@]}"; i++ )); do
        get_host ${im_result[$i]}
        im_hosts=("${im_hosts[@]}" "${found_host}")
        echo -en "\rFinding InterMapper hostnames..."
        echo -en "\t\t${FBRED}($((100*(i+1)/${#im_result[@]}))%)${RS}"
    done
    echo -en "\rFinding InterMapper hostnames..."
    echo -e "\t\t${FBGRN}[done]${RS}"
}

## FILE OUTPUT
file_out () {
    echo -en "Outputting results to ${FBCYN}[${output}]${RS}..."
    if [[ -f "${output}" ]]; then
        output > "${output}"
    else
        touch "${output}"
        output > "${output}"
    fi
    echo -en "\rOutputting results to ${FBCYN}[${output}]${RS}"
    echo -e "...\t\t${FBGRN}[done]${RS}"
}

## OUTPUT
# Regular output (only shows the differences)
output () {
    if [[ -z "${simple}" ]]; then
        out_radmind
        echo
        out_intermapper
    else
        if [[ "${simple}" -eq 1 ]]; then
            out_radmind
        else
            out_intermapper
        fi
    fi
}

## CONSOLE OUTPUT
# Regular Radmind output (only shows Radmind positive disparity)
out_radmind () {
    # Format output header
    rm_string="Radmind (${#rm_result[@]} total)"

    # Output header
    echo -e "\t${rm_string}"
    echo -e "\t\t(${#rm_disp[@]} extra)"
    echo -en "\t"
    printd ${#rm_string}
    echo

    # Either print the limited disparity list or the full one
    if [[ -z "${full}" ]]; then
        for (( i=0; i<"${#rm_disp[@]}"; i++ )); do
            if [ "${rm_hosts[${rm_disp[$i]}]}" == "3(NXDOMAIN)" ]; then
                if [[ "${OUTPUTTING}" -eq 0 ]]; then
                    echo -en "${FBYEL}"
                fi
            fi
            echo -en "\t  ${rm_result[${rm_disp[$i]}]}"
            echo -e "    \t(${rm_hosts[${rm_disp[$i]}]})"
            if [[ "${OUTPUTTING}" -eq 0 ]]; then
                echo -en "${RS}"
            fi
        done
    else
        count=0
        for (( i=0; i<"${#rm_result[@]}"; i++ )); do
            if [ "${rm_disp[$count]}" == "$i" ]; then
                echo -en "\t  ${rm_result[$i]}    \t(*)"
                (( count++ ))
            else
                echo -en "\t  ${rm_result[$i]}    \t   "
            fi
            echo -e "\t(${rm_hosts[$i]})"
        done
    fi
}

# Regular InterMapper output (only shows InterMapper positive disparity)
out_intermapper () {
    # Format output header
    im_string="InterMapper (${#im_result[@]} total)"

    # Output header
    echo -e "\t${im_string}"
    echo -e "\t\t(${#im_disp[@]} extra)"
    echo -en "\t"
    printd ${#im_string}
    echo

    # Either print the limited disparity list or the full one
    if [[ -z "${full}" ]]; then
        for (( i=0; i<"${#im_disp[@]}"; i++ )); do
            if [ "${im_hosts[${im_disp[$i]}]}" == "3(NXDOMAIN)" ]; then
                if [[ "${OUTPUTTING}" -eq 0 ]]; then
                    echo -en "${FBYEL}"
                fi
            fi
            echo -en "\t  ${im_result[${im_disp[$i]}]}"
            echo -e "    \t(${im_hosts[${im_disp[$i]}]})"
            if [[ "${OUTPUTTING}" -eq 0 ]]; then
                echo -en "${RS}"
            fi
        done
    else
        count=0
        for (( i=0; i<"${#im_result[@]}"; i++ )); do
            if [ "${im_disp[$count]}" == "$i" ]; then
                echo -en "\t  ${im_result[$i]}    \t(*)"
                (( count++ ))
            else
                echo -en "\t  ${im_result[$i]}    \t   "
            fi
            echo -e "\t(${im_hosts[$i]})"
        done
    fi
}

## MAIN
main () {
    # Declare the arrays to be used.
    declare -a rm_result
    declare -a im_result
    declare -a rm_disp
    declare -a im_disp
    declare -a rm_hosts
    declare -a im_hosts

    # Run the program's parts
#     if [[ -z "${simple}" || "${simple}" -eq 1 ]]; then
#         get_radmind
#         radmind_hostnames
#     fi
#     if [[ -z "${simple}" || "${simple}" -eq 2 ]]; then
#         get_intermapper
#         intermapper_hostnames
#     fi
#     if [[ -z "${no_disp}" ]]; then
#         if [[ -z "${simple}" ]]; then
#             radmind_disp
#             intermapper_disp
#         else
#             if [[ "${simple}" -eq 1 ]]; then
#                 radmind_disp
#             else
#                 intermapper_disp
#             fi
#         fi
#     fi
#
#     # File output (implement this)
#     if [[ -n "${output}" ]]; then
#         OUTPUTTING=1
#         file_out
#     fi
#
#     # Determine whether to output things
#     if [[ -z "${quiet}" ]]; then
#         OUTPUTTING=0
#         echo
#         output
#     fi
#
#     # Looks like we've made it out alive!
#     exit 0
}

## EXECUTION
main
