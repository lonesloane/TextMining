try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Semantic analysis tools',
    'author': 'Lone Sloane',
    'version': '0.1',
    'packages': ['analysis'],
    'scripts': [],
    'name': 'semantic analysis'
}

setup(**config)