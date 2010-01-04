from setuptools import setup, find_packages

setup(name="warp",
      version="0.0.1",
      packages = find_packages(),
      zip_safe = False,
      include_package_data=True,

      description="Easy-to-use layer over twisted.web",
      author="Brendon Hogger",
      author_email="brendonh@taizilla.com",
      url="http://wiki.github.com/brendonh/warp",
      long_description=open('README').read(),

      download_url="http://github.com/brendonh/warp/tarball/master#egg=warp",

      install_requires = [
        "twisted >= 8.2",
        "storm >= 0.12",
        "Mako >= 0.2.5",
        "pytz",
        ],

      packages = find_packages('.') + ["twisted.plugins"],

      package_data = {
        "twisted": ['plugins/warp_plugin.py'],
        }

)
