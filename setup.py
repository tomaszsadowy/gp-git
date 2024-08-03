from setuptools import setup, find_packages

setup(
    name='gp-git',
    version='0.0.1',
    author='Tomasz Sadowy',
    author_email='tomaszsadowypriv@gmail.com',
    description='An alternative to your standard git, built using Python',
    packages=find_packages(),
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