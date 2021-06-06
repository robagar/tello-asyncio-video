from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='tello_asyncio_video',
      version='1.0.0',
      description='Flying the Tello drone with video',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/robagar/tello-asyncio-video',
      project_urls={
            'Documentation': 'https://tello-asyncio-video.readthedocs.io/en/latest/'
      },
      author='Rob Agar',
      author_email='tello_asyncio@fastmail.net',
      license='LGPL',
      packages=['tello_asyncio_video'],
      zip_safe=False,
      python_requires=">=3.6",
      install_requires=[
        'tello-asyncio >= 2.0.0',
        'numpy >= 1.13.3',
      ])