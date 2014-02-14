radmind_intermapper_diff
========================

This script is designed for use in an environment where Radmind and InterMapper are used to manage the computers.  Its purpose is to report back to the user with a list of differences between the two systems.

Contents
--------

* [Background](#background)
* [Usage](#usage)
  * [Optional Arguments](#optional-arguments)
    * [Boolean Switches](#boolean-switches)
    * [Positional Parameters](#positional-parameters)
  * [Examples](#examples)

Background
----------

Wikipedia has [this](http://en.wikipedia.org/wiki/Radmind) to say about Radmind:

> Radmind is a suite of Unix command-line tools and an application server designed to remotely administer the file systems of multiple client machines.

and [this](http://en.wikipedia.org/wiki/InterMapper) to say about InterMapper:

> InterMapper is a cross-platform network monitoring program and part of the Help/Systems cross-platform family.

In our environment, Radmind is used to administrate the file systems of our computers, and InterMapper is (primarily) used to check whether our computers are online and responding to ping requests.  However, each of these administrative system requires its own database or configuration file to know which computers it needs to check in with.  Over time, these files tend to become out of sync with one another, resulting in false outages or lack of maintenance.

In an effort to consolidate these separate files, I created this script.  Its purpose is to scan the databases and then report back with a list of positive disparities; that is, it tells you "Radmind had *these* entries that InterMapper didn't have, and InterMapper had *these* entries that Radmind didn't."  To further its usefulness, the script is also able to write that output to a file or email the results to a specified recipient.

Usage
-----

`$ ./radmind_intermapper_diff.py -[options]`

#### Optional Arguments

Ideally, you should be able to set all of the necessary values within the script itself so you don't have to use so many options at runtime.  However, sometimes it's unavoidable, so here is an explanation of all the options available to you.

##### Boolean Switches

These options are all boolean values - they're either true or false (on or off).  False is the default value, so passing any of these changes that to true.  `--version` will override any other option except `--help` and `--explicit`, and `--help` overrides every other option except `--explicit`.

| Short name | Long name | Description |
|------------|-----------|-------------|
| `-h` | `--help` | show helpful usage information and quit |
| `-v` | `--version` | show the current version information and quit |
| `-f` | `--full` | give the full list of items (differences are unmarked) |
| `-q` | `--quiet` | suppress output to the console (unless used with `-x`, which will still display variable information) |
| `-x` | `--explicit` | show the current variable values at the beginning of runtime |
| `-d` | `--dns-full` | show the full DNS names without truncating them (`computer.tech.domain.com` vs `computer`) |
| `-e` | `--email` | attempt to send the output via email using the default (built-in) values |

##### Positional Parameters

All of these options require an additional parameter to be passed after them to change the corresponding value.  If no parameter is supplied, the program will throw an error and terminate.

| Short name | Long name | Parameter | Description |
|------------|-----------|-----------|-------------|
| `-r` | `--radmind-file` | `file` | use `file` as the Radmind configuration file |
| `-i` | `--intermapper-file` | `file` | use `file` as the InterMapper list of device addresses |
| `-I` | `--intermapper-address` | `address` | use `address` as the InterMapper website to get the addresses fresh (recommended over `-i`) |
| `-o` | `--output` | `file` | use `file` as a destination for all the output. |
|      | `--smtp-server` | `address` | use `address` as the SMTP server for sending mail. |
|      | `--email-address` | `address` | use `address` as the recipient email address. |
|      | `--source-email` | `address` | use `address` as the sending email address. |

#### Examples

* `$ ./radmind_intermapper_diff.py -r config.txt -I "https://intermapper.domain.com"`

   Fetches the Radmind config from `config.txt` and the InterMapper list from `https://intermapper.domain.com`.  This will output the list of differences to the console and then quit.
   
* `$ ./radmind_intermapper_diff.py -i intermapper.txt -o output.txt`

   Gets the InterMapper list from `intermapper.txt` instead of online.  The list of differences is then outputted to `output.txt` as well as to the console.
   
* `$ ./radmind_intermapper_diff.py -qe`

   Gets the lists from the default locations (specified in the script).  Console output is suppressed, so the user will receive no feedback.  The list that would regularly be outputted is sent via email using the default specifications.
   
* `$ ./radmind_intermapper_diff.py --smtp-server "smtp.domain.com" --email-address "recipient@domain.com" --source-email "PROG@domain.com" -qdx`

   First finds the differences from the default locations.  The console output is suppressed, except for listing the variables and values that are being used at runtime.  The output is sent via email using the SMTP server `smtp.domain.com` to `recipient@domain.com` from `PROG@domain.com`.
