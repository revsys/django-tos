import os
from setuptools import setup, find_packages

from tos import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-tos',
    version=".".join(map(str, VERSION)),
    description='django-tos is a reusable Django application for setting Terms of Service.',
    long_description=readme,
    author='Frank Wiles',
    author_email='frank@revsys.com',
    url='http://github.com/revsys/django-tos/tree/master',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
