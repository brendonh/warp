from setuptools import setup, find_packages

setup(name="warp",
      version="0.0.1",
      packages = find_packages(),
      zip_safe = False,

      description="Easy-to-use layer over twisted.web",
      author="Brendon Hogger",
      author_email="brendonh@taizilla.com",
      url="http://wiki.github.com/brendonh/warp",
      long_description=open('README').read(),
)
