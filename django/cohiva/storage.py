"""
Custom static file storage backends for cache busting.
"""

import os

from django.contrib.staticfiles.storage import StaticFilesStorage


class CacheBustingStaticFilesStorage(StaticFilesStorage):
    """
    Static files storage that appends file modification time as a query parameter.
    This ensures browsers reload static files when they change during development.
    """

    def url(self, name):
        url = super().url(name)

        # Get the file path
        try:
            # Try to get the actual file path
            file_path = self.path(name)
            if os.path.exists(file_path):
                # Get file modification time
                mtime = int(os.path.getmtime(file_path))
                # Append as query parameter
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}v={mtime}"
        except (NotImplementedError, AttributeError, OSError):
            # If we can't get the file path or mtime, just return the original URL
            pass

        return url
