from setuptools import find_packages, setup

with open('luxinema/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

REQUIRES = ['pandas', 'requests', 'setuptools', 'beautifulsoup4']

setup(
    name='luxinema',
    version=version,
    description='Retrieve cinema information for the LUX Nijmegen',
    long_description=readme,
    author='Daniel Gomez',
    author_email='d.gomez@posteo.org',
    maintainer='Daniel Gomez',
    maintainer_email='d.gomez@posteo.org',
    url='https://github.com/dangom/luxinema',
    license='MIT/Apache-2.0',

    keywords=[
        'cinema',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
