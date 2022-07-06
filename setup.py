from setuptools import setup

setup(name='Pythogen',
      version='0.6a',
      description='Library used for simulating cellular network diffusion',
      url='https://github.com/AoifeHuges/pythogen',
      author='Aoife Hughes',
      author_email='Aofie.hughes@jic.ac.uk',
      license='MIT',
      packages=['Pythogen'],
      install_requires=[
          'numpy', 'matplotlib', 'scipy', 'networkx', 'pandas', 'tqdm'
      ],
      zip_safe=True)
