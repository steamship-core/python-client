from __future__ import annotations

from steamship.invocable import Invocable

# Note!
# =====
#
# This the files in this package are for Package Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#


class PackageService(Invocable):
    """The Abstract Base Class of a Steamship Package.

    Packages may implement whatever methods they like.  To expose these methods as invocable HTTP routes,
    annotate the method with @get or @post and the route name.

    Package *implementations* are effectively stateless, though they will have stateful

    """
