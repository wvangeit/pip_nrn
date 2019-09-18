import os
import sys
import contextlib
import tarfile

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig

import versioneer

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

VERSION = '0.2.6'

NRN_SHORT_VERSION = '7.6'
NRN_LONG_VERSION = '7.6.7'

NRN_TARBALL_URL = \
    'https://neuron.yale.edu/ftp/neuron/versions/v%s/%s/nrn-%s.tar.gz' % (
        NRN_SHORT_VERSION, NRN_LONG_VERSION, NRN_LONG_VERSION)

NRN_TARBALL = 'nrn-%s.tar.gz' % NRN_LONG_VERSION


class NrnExtension(Extension, object):

    def __init__(self, name):
        super(NrnExtension, self).__init__(name, sources=[])


class build_ext(build_ext_orig, object):

    def run(self):
        for ext in self.extensions:
            self.build_nrn(ext)
        super(build_ext, self).run()

    def build_nrn(self, ext):
        os.makedirs(self.build_temp)

        configure_args = [
            '--without-x',
            '--prefix=%s' %
            sys.prefix,
            '--exec-prefix=%s' %
            sys.prefix,
            '--with-nrnpython=%s' % sys.executable,
            '--disable-pysetup',
            '--disable-rx3d']
        make_args = ['-j', 'install']
        setup_args = ['--prefix=%s' % sys.prefix]

        with cd(self.build_temp):
            urlretrieve(NRN_TARBALL_URL, NRN_TARBALL)
            tarfile.open(NRN_TARBALL, 'r:gz').extractall()
            configure_cmd = os.path.join(
                'nrn-%s' %
                NRN_SHORT_VERSION, 'configure')
            self.spawn([configure_cmd] + configure_args)
            make_cmd = os.path.join('make')
            self.spawn([make_cmd] + make_args)
            with cd(os.path.join('src', 'nrnpython')):
                self.spawn([sys.executable, 'setup.py',
                            'install'] + setup_args)


@contextlib.contextmanager
def cd(dir_name):
    """Change directory"""
    old_cwd = os.getcwd()
    os.chdir(dir_name)
    try:
        yield
    finally:
        os.chdir(old_cwd)


setup(
    name='nrn',
    version=versioneer.get_version(),
    packages=['nrn'],
    install_requires=[],
    ext_modules=[NrnExtension('nrn')],
    cmdclass={
        'build_ext': build_ext,
    }
)
