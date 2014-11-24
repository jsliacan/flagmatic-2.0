
Emil's flagmatic with changed setup.py and extra install-2-flagmatic file for simple repeated installation.


Flagmatic 2.0
=============

A package for the Sage system.

To install for the first time, type (this will remove other versions of flagmatic and install this one):

    $ cd pkg
    $ cp install-2-flagmatic /usr/local/bin/
    $ sudo chmod +x /usr/local/bin/install-2-flagmatic
    $ cd; install-2-flagmatic

To install again (e.g. after having installed another version of flagmatic in the meantime), type:

    $ install-2-flagmatic

Then, from the Sage prompt, type:

    sage: from flagmatic.all import *
