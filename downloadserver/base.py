




class DownloadServer(object):
    """Base class for all DownloadServers

    Don't use this class directly, subclass it!
    Implementing both the download methods is required.
    """

    def __init__(self):
        pass

    def download_spot(self, spot):
        """Get's a SpotnetPost instance and downloads it.
        Make sure this raises a subclass of DownloadError on failure.
        """
        raise NotImplementedError

    def download_nzb(self, nzb):
        """Get's an nzb as a file like object and downloads it.
        Make sure this raises a subclass of DownloadError on failure.
        """
        return NotImplementedError



