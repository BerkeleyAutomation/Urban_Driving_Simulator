from setuptools import setup

# This is super hack to keep version number in one spot
f = open("fluids/version.py")
exec(f.readlines()[0])


setup(name="fluids",
      version=__version__,
      install_requires=['pygame',
                        'numpy',
                        'scipy',
                        'shapely',
                        'ortools',
                        'pillow'])
