from setuptools import setup

setup(
      name='maninex',
      version='0.1',
      description="An extension manager to replace Google's WebStore API",
      long_description=open('README.md').read(),
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
      keywords='base16',
      install_requires=['requests'],
      python_requires='>=3.6',
      entry_points={
                    'console_scripts': [
                                        'maninex = maninex:main'
                                       ]
                   }
     )
