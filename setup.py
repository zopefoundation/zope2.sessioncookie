from setuptools import find_packages
from setuptools import setup


with open('README.rst') as f:
    README = f.read()

with open('CHANGES.rst') as f:
    CHANGES = f.read()

setup(name='zope2.signedsessioncookie',
      version='0.4.dev0',
      description='Use Pyramid signed sessison cookie as Zope2 session manager',
      long_description='\n\n'.join([README, CHANGES]),
      url='https://github.com/zeomega/zope2.signedsessioncookie',
      license='Proprietary (copyright ZeOmega, all rights reserved)',
      packages=find_packages(),
      namespace_packages=['zope2',],
      include_package_data=True,
      install_requires=['pyramid>=1.5', 'Zope2>=2.13'],
      test_suite='zope2.signedsessioncookie.tests',
)
