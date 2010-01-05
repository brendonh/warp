from setuptools import setup, find_packages

setup(name="warp",
      version="0.0.1",
      zip_safe = False,
      include_package_data=True,

      description="Easy-to-use layer over twisted.web",
      author="Brendon Hogger",
      author_email="brendonh@taizilla.com",
      url="http://wiki.github.com/brendonh/warp",
      long_description=open('README').read(),

      download_url="http://github.com/brendonh/warp/tarball/master#egg=warp",

      packages = find_packages('.') + ["twisted.plugins"],

      install_requires = [
        "twisted >= 8.2",
        "storm >= 0.12",
        "Mako >= 0.2.5",
        "pytz",
        "simplejson",
        ],

      package_data = {
        "twisted": ['plugins/warp_plugin.py'],
        }

)

# Do not look beyond this point, unless you want to destroy your
# confidence in the software you are about to use.


def cleanupTwistedCache():
    from twisted.plugin import IPlugin, getPlugins

    print "~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Attempting to flush Twisted's plugin cache."

    list(getPlugins(IPlugin))

    print
    print "If you got a traceback there, it's fine, don't worry."
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~"


import sys
if 'bdist_egg' in sys.argv:
    import atexit
    atexit.register(cleanupTwistedCache)
