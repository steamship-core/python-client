"""Core Steamship operations on Easy Mode.

Many packages have to carefully sequence creating and blockifying a variety of differnet file types.

This module contains a common set of "easy-mode" scripts that mostly work for prototypes and can
be replaced with more nuanced code as needs arise.
"""

from .blockify import blockify
from .index import index
from .scrape import scrape
