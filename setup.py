from distutils.core import setup

setup(
    name='AdvancedStatsForBronyAtHome',
    version='0.0.1',
    packages=['modules.core', 'modules.boinc', 'modules.utils',
              'modules.network', 'modules.database'],
    package_dir={'modules': 'modules'},
    url='',
    license='',
    author='PXke',
    author_email='guillaume.lastecoueres@techie.com',
    description=''
)


