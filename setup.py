from setuptools import setup

setup(
    name='Batcher',
    url='https://github.com/tuikkuanttila/batcher',
    author='Tuikku Anttila',
    author_email='tuikku.anttila@gmail.com',
    packages=['batcher'],
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='A library for splitting arrays into optimally sized batches for Kinesis.',
    # long_description=open('README.txt').read(),
)