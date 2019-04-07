from __future__ import division, absolute_import
from __future__ import print_function

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from xtgeo.common import XTGeoDialog
from xtgeo.plot import _colortables as _ctable

xtg = XTGeoDialog()
logger = xtg.functionlogger(__name__)


class BasePlot(object):
    """Base class for plots, providing some functions to share"""

    def __init__(self):

        clsname = "{}.{}".format(type(self).__module__, type(self).__name__)
        logger.info(clsname)

        self._contourlevels = 3
        self._colormap = plt.cm.viridis
        self._tight = False
        self._showok = True
        self._fig = None

        logger.info("Ran __init__ ...")

    @property
    def contourlevels(self):
        """Get the number of contour levels"""
        return self._contourlevels

    @contourlevels.setter
    def contourlevels(self, num):
        self._contourlevels = num

    @property
    def colormap(self):
        """Get or set the color table as a matplot cmap object."""
        return self._colormap

    @colormap.setter
    def colormap(self, cmap):

        if isinstance(cmap, LinearSegmentedColormap):
            self._colormap = cmap
        elif isinstance(cmap, str):
            logger.info("Definition of a colormap from string name...")
            self.define_colormap(cmap)
        else:
            raise ValueError("Input incorrect")

        logger.info("Colormap: %s", self._colormap)

    @staticmethod
    def define_any_colormap(cfile, colorlist=None):
        """Defines any color map from file or a predefined name.

        This is a static method, which returns a matplotlib CM object.

        Args:
            cfile (str): File name (RMS format) or an alias for a predefined
                map name, e.g. 'xtgeo', or one of matplotlibs numerous tables.
            colorlist (list, int, optional): List of integers redefining
                color entries per zone and/or well, which starts
                from 0 index. Default is just keep the linear sequence as is.

        """
        valid_maps = sorted(m for m in plt.cm.datad)

        logger.info(valid_maps)

        colors = []

        cmap = plt.get_cmap("rainbow")

        if cfile is None:
            cfile = "rainbow"
            cmap = plt.get_cmap("rainbow")

        elif cfile == "xtgeo":
            colors = _ctable.xtgeocolors()
            cmap = LinearSegmentedColormap.from_list(cfile, colors, N=len(colors))
            cmap.name = "xtgeo"
        elif cfile == "random40":
            colors = _ctable.random40()
            cmap = LinearSegmentedColormap.from_list(cfile, colors, N=len(colors))
            cmap.name = "random40"

        elif cfile == "randomc":
            colors = _ctable.randomc(256)
            cmap = LinearSegmentedColormap.from_list(cfile, colors, N=len(colors))
            cmap.name = "randomc"

        elif isinstance(cfile, str) and "rms" in cfile:
            colors = _ctable.colorsfromfile(cfile)
            cmap = LinearSegmentedColormap.from_list("rms", colors, N=len(colors))
            cmap.name = cfile
        elif cfile in valid_maps:
            cmap = plt.get_cmap(cfile)
            logger.info(cmap.N)
            for i in range(cmap.N):
                colors.append(cmap(i))
        else:
            cmap = plt.get_cmap("rainbow")
            logger.info(cmap.N)
            for i in range(cmap.N):
                colors.append(cmap(i))

        ctable = []

        if colorlist:
            for entry in colorlist:
                if entry < len(colors):
                    ctable.append(colors[entry])
                else:
                    logger.warn("Color list out of range")
                    ctable.append(colors[0])

            cmap = LinearSegmentedColormap.from_list(ctable, colors, N=len(colors))
            cmap.name = "user"

        return cmap

    @staticmethod
    def get_any_colormap_as_table(cmap):
        """Returns the given color map cmap as a list of RGB tuples."""
        cmaplist = [cmap(i) for i in range(cmap.N)]
        return cmaplist

    def set_colortable(self, cname, colorlist=None):
        """This is actually deprecated..."""
        if colorlist is None:
            self.colormap = cname
        else:
            self.define_colormap(cname, colorlist=colorlist)

    def get_colormap_as_table(self):
        """Get the current color map as a list of RGB tuples."""
        return self.get_any_colormap_as_table(self._colormap)

    def define_colormap(self, cfile, colorlist=None):
        """Defines a color map from file or a predefined name.

        Args:
            cfile (str): File name (RMS format) or an alias for a predefined
                map name, e.g. 'xtgeo', or one of matplotlibs numerous tables.
            colorlist (list, int, optional): List of integers redefining
                color entries per zone and/or well, which starts
                from 0 index. Default is just keep the linear sequence as is.

        """
        logger.info("Defining colormap")

        cmap = self.define_any_colormap(cfile, colorlist=colorlist)

        self.contourlevels = cmap.N
        self._colormap = cmap

    def show(self):
        """Call to matplotlib.pyplot show().

        Returns:
            True of plotting is done; otherwise False
        """
        if self._tight:
            self._fig.tight_layout()

        if self._showok:
            logger.info("Calling plt show method...")
            plt.show()
            return True

        logger.warning("Nothing to plot (well outside Z range?)")
        return False

    def savefig(self, filename, fformat="png", last=True):
        """Call to matplotlib.pyplot savefig().

        Args:
            filename (str): File to plot to
            fformat (str): Plot format, e.g. png (default), jpg, svg
            last (bool): Default is true, meaning that memory will be cleared;
                however if several plot types for the same instance, let last
                be False fora all except the last plots.

        Returns:
            True of plotting is done; otherwise False

        Example::
            myplot.savefig('TMP/layerslice.svg', fformat='svg', last=False)
            myplot.savefig('TMP/layerslice.png')

        """
        if self._tight:
            self._fig.tight_layout()

        if self._showok:
            plt.savefig(filename, format=fformat)
            if last:
                plt.close(self._fig)
            return True

        logger.warning("Nothing to plot (well outside Z range?)")
        return False
