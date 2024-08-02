from setuptools import setup

setup(
    name='gp-git',
    version='0.0.1',
    author='Tomasz Sadowy',
    author_email='tomaszsadowypriv@gmail.com',
    description='An alternative to your standard git, built using Python',
    packages=['gpgit'],
    entry_points = {
        'console_scripts':[
            'gpgit = gpgit.gpgit.main'
        ]
    }
)


