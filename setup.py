from distutils.core import setup

setup(
    name='AdvancedStatsForBronyAtHome',
    version='0.0.1',
    packages=['modules', 'modules.core', 'modules.boinc', 'modules.utils', 'modules.network', 'modules.database',
              'core', 'boinc', 'utils', 'network', 'database'],
    package_dir={'': 'modules'},
    url='',
    license='',
    author='PXke',
    author_email='guillaume.lastecoueres@techie.com',
    description=''
)
