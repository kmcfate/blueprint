"""
Search for `rpm` packages to include in the blueprint.
"""

import logging
import re
import subprocess
import os.path

CACHE = '/tmp/blueprint-exclusions'


def rpm(b):
    if not os.path.exists('/bin/rpm'):
        logging.info('skipping rpm search')
        return
    logging.info('searching for rpm packages')

    p = subprocess.Popen(['rpm',
                          '--qf', '%{name} %{version}\n',
                          '-qa'],
                         close_fds=True, stdout=subprocess.PIPE)
    s = exclusions()
    for line in p.stdout:
        package, version = line.strip().split()
        if package in s:
            continue
        b.packages['rpm'][package].append(version)


def exclusions():
    """
    Return the set of packages that should never appear in a blueprint because
    they're already guaranteed (to some degree) to be there.
    """

    # Read from a cached copy.
    try:
        return set([line.rstrip() for line in open(CACHE)])
    except IOError:
        pass

    # Start with the root package for the various Ubuntu installations.
    s = set()

    pattern = re.compile(r'^   ([0-9a-zA-Z_]+)')

    # Find the essential and required packages.  Every server's got 'em, no
    # one wants to muddle their blueprint with 'em.
    p = subprocess.Popen(['yum', 'groupinfo',
                          'core','base', 'gnome-desktop'],
                         close_fds=True, stdout=subprocess.PIPE)
    for line in p.stdout:
        match = pattern.match(line)
        if match is None:
            continue
        s.add(match.group(1))

    # Walk the dependency tree all the way to the leaves.
    tmp_s = s
    pattern = re.compile(r'\s+provider:\s([0-9a-zA-Z_-]+)\..*')
    while 1:
        new_s = set()
        print '==========DEP CHECK=========='
        for package in tmp_s:
            p = subprocess.Popen(['yum', 'deplist', package],
                close_fds=True, stdout=subprocess.PIPE)
            for line in p.stdout:
                match = pattern.match(line)
                if match is None:
                    continue
                if match.group(1) not in new_s and match.group(1) not in s:
                    print 'Adding',match.group(1)
                    new_s.add(match.group(1))

        # If there is to be a next iteration, `new_s` must contain some
        # packages not yet in `s`.
        tmp_s = new_s - s
        if 0 == len(tmp_s):
            break
        s |= new_s

    # Write to a cache.
    f = open(CACHE, 'w')
    for package in sorted(s):
        f.write('%s\n' % (package))
    f.close()

    return s
