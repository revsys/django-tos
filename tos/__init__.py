__version__ = "1.2.1"

# Kept for backwards compatibility with anything importing the tuple form.
VERSION = tuple(int(part) for part in __version__.split("."))
