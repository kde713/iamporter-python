import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('iamporter/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='iamporter',
    version=version,

    description="An I'mport REST API Client for Human",
    long_description='아임포트에서 제공하는 REST API를 쉽게 활용하기 위해 작성된 Python 클라이언트입니다',

    url='https://github.com/kde713/iamporter-python',

    author='kde713',
    author_email='kde713@gmail.com',

    license='MIT',

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords=['iamport', 'import', 'payment', 'iamporter'],

    packages=find_packages(exclude=['test', 'tests', 'docs', 'examples']),

    install_requires=[
        'requests',
    ],

    python_requires='>=3',
)
