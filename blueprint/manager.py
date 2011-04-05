"""
"""

import re


class Manager(dict):
    """
    """

    def __init__(self, name, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)
        self.name = name

    def __call__(self, package, version):
        """
        """

        if 'apt' == self.name:
            return 'apt-get -y install %s=%s' % (package, version)
        if 'yum' == self.name:
            return 'yum -y install %s-%s' % (package, version)

        match = re.match(r'^ruby(?:gems)?(\d+\.\d+(?:\.\d+)?|)', self.name)
        if match is not None:
            # FIXME PATH might have a thing to say about this.
            return 'gem%s install %s -v%s' % (match.group(1),
                                                     package,
                                                     version)

        match = re.match(r'^python(\d+\.\d+)', self.name)
        if match is not None:
            return 'easy_install-%s %s' % (match.group(1), package)
        if 'pip' == self.name or 'python-pip' == self.name:
            return 'pip install %s==%s' % (package, version)

        if 'php-pear' == self.name:
            return 'pear install %s-%s' % (package, version)
        if 'php5-dev' == self.name:
            return 'pecl install %s-%s' % (package, version)
        if 'php-devel' == self.name:
            return 'pecl install %s-%s' % (package, version)

        return ': unknown manager %s for %s %s' % (self.name,
                                                          package,
                                                          version)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
