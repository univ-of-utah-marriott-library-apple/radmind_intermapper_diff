radmind_intermapper_diff
========================

This script is designed for use in an environment where Radmind and InterMapper are used to manage the computers.  Its purpose is to report back to the user with a list of differences between the two systems.

Background
----------

Wikipedia has [this](http://en.wikipedia.org/wiki/Radmind) to say about Radmind:

> Radmind is a suite of Unix command-line tools and an application server designed to remotely administer the file systems of multiple client machines.

and [this](http://en.wikipedia.org/wiki/InterMapper) to say about InterMapper:

> InterMapper is a cross-platform network monitoring program and part of the Help/Systems cross-platform family.

In our environment, Radmind is used to administrate the file systems of our computers, and InterMapper is (primarily) used to check whether our computers are online and responding to ping requests.  However, each of these administrative system requires its own database or configuration file to know which computers it needs to check in with.  Over time, these files tend to become out of sync with one another, resulting in false outages or lack of maintenance.

In an effort to consolidate these separate files, I created this script.  Its purpose is to scan the databases and then report back with a list of positive disparities; that is, it tells you "Radmind had *these* entries that InterMapper didn't have, and InterMapper had *these* entries that Radmind didn't."  To further its usefulness, the script is also able to write that output to a file or email the results to a specified recipient.
