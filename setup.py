
from setuptools import setup

def readme():
    with open('README.rst', encoding='utf8') as f:
        return f.read()

setup(name='burst_detection',
      version='0.1',
      description='Detect bursts in batched data using Kleinberg''s (2002) algorithm.',
      long_description=readme(),
      classifiers=[
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='bursts burst bursty time series fads trends kleinberg streams timecourse',
      url='http://github.com/nmarinsek/burst_detection',
      author='Nikki Marinsek',
      author_email='nikki.marinsek@gmail.com',
      license='',
      packages=['burst_detection'],
      install_requires=[
        'pandas',
        'numpy',
        'sympy'
      ],
      zip_safe=False)
