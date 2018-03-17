from setuptools import setup

setup(
      name='maninex',
      version='0.4',
      description="An extension manager to replace Google's WebStore",
      long_description=open('README.rst').read(),
      url='https://github.com/InspectorMustache/maninex',
      packages=['maninex'],
      author='Pu Anlai',
      license='MIT',
      classifiers=[
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: End Users/Desktop',
                   'Topic :: Internet :: WWW/HTTP :: Browsers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3 :: Only'
                  ],
      keywords='chromium extension webstore inox iridium',
      install_requires=['requests'],
      python_requires='>=3.5',
      entry_points={
                    'console_scripts': [
                                        'maninex = maninex:main'
                                       ]
                   }
     )
