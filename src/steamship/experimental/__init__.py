"""Experimental Steamship Packages

This module contains experimental Steamship code. It's intended to serve as a place to store fast-moving
experiments that aren't yet ready for the core Steamship library.

In general, try to avoid introducing new dependencies to requirements.txt, but otherwise use this as a place
to try out new metaphors and helper classes!
"""

from .easy import blockify, scrape

__all__ = ["scrape", "blockify"]
