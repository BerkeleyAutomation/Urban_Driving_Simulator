from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
 
ext_modules = [Extension("integrator_c",["integrator_c.pyx"],include_dirs=[numpy.get_include()],\
    libraries=["m"])]
 
setup(
    name= 'Generic model class',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    include_dirs= [numpy.get_include()]
)