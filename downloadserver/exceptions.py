




class DownloadError(Exception):
    def __init__(self):
        pass





class PermissionDeniedError(DownloadError):
    def __init__(self, msg=''):
        self.msg = msg

class UnauthenticatedError(PermissionDeniedError):
    def __init__(self):
        pass



class FileError(DownloadError):
    def __init__(self, msg=''):
        self.msg = msg

class DiskFullError(FileError):
    def __init__(self):
        pass



class InvalidNzbError(DownloadError):
    def __init__(self):
        pass



class UnhandledDownloadError(DownloadError):
    def __init__(self):
        pass



