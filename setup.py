from setuptools import setup

setup(
    name='gpgit',
    version='0.0.1',
    author='Tomasz Sadowy',
    author_email='tomaszsadowypriv@gmail.com',
    description='A local version control system, built for newbies.',
    packages=['gpgit'],
    entry_points={
        'console_scripts': [
            'gpgit = gpgit.gpgit:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)