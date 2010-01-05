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


def cleanupTwistedCache():
    import exceptions
    from twisted.plugin import IPlugin, getPlugins

    try:
        list(getPlugins(IPlugin))
    except exceptions.IOError:
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "Unable to flush Twisted's plugin cache, because you don't have"
        print "write access to it. Before using warp, please run:"
        print
        print "sudo python -c \"from twisted.plugin import IPlugin, getPlugins; list(getPlugins(IPlugin))\""
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~"


import atexit
atexit.register(cleanupTwistedCache)
