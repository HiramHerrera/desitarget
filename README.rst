
desitarget
=========

This package contains scripts and packages for selecting DESI targets
from photometric catalogs.


Installation
-------------

You can install these tools in a variety of ways.  Here are several that may be of interest:

1.  Manually running from the git checkout.  Add the "bin" directory to your $PATH environment variable and add the "py" directory to your $PYTHONPATH environment variable.

2.  Install (and uninstall) a symlink to your live git checkout::

	$>  python setup.py develop --prefix=/path/to/somewhere
	$>  python setup.py develop --prefix=/path/to/somewhere --uninstall

3.  Install a fixed version of the tools::

	$>  python setup.py install --prefix=/path/to/somewhere


Versioning
------------

If you have tagged a version and wish to set the package version based on your current git location::

	$>  python setup.py version

And then install as usual


