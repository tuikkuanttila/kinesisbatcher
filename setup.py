from setuptools import setup

setup(
    name='Kinesisbatcher',
    url='https://github.com/tuikkuanttila/kinesisbatcher',
    author='Tuikku Anttila',
    author_email='tuikku.anttila@gmail.com',
    packages=['kinesisbatcher'],
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='A library for splitting arrays into optimally sized batches for Kinesis.',
    # long_description=open('README.txt').read(),
)