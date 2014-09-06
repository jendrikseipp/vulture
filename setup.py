#! /usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

from vulture import __version__


setup(name='vulture',
      version=__version__,
      description="Find dead code",
      long_description='\n\n'.join([open('README.txt').read(),
                                    open('NEWS.txt').read()]),
      keywords='vulture',
      author='Jendrik Seipp',
      author_email='jendrikseipp@web.de',
      url='https://bitbucket.org/jendrikseipp/vulture',
      license='GPL3+',
      py_modules=['vulture'],
      classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Utilities",
        ],
      entry_points={
        'console_scripts': ['vulture = vulture:main'],
      },
      )
