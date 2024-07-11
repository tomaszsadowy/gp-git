from setuptools import setup

setup(
    name='zgit',
    version='0.0.1',
    author='Tomasz Sadowy',
    author_email='tomaszsadowypriv@gmail.com',
    description='An alternative to your standard git, built using Python',
    packages=['zgit'],
    entry_points = {
        'console_scripts':[
            'zgit = zgit.cli.main'
        ]
    }
)


