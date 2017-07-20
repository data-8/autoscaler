"""
Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.
"""
from setuptools import find_packages, setup

dependencies = [
    'kubernetes==1.0.0b1',
    'google-api-python-client==1.6.2',
    'websocket==0.2.1',
    'requests'
]

setup(
    name='autoscaler',
    version='0.0.1',
    url='https://github.com/data-8/autoscaler',
    license='Apache',
    author='Tony Yang, Jeff Gong, Peter Veerman',
    author_email='',
    description='Autoscaler for the jupyterhub-k8s cluster.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'autoscaler = autoscaler.main:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
