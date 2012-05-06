import zlib


class DecodeNzbError(Exception):
    pass


def decode_nzb(content):
    # decompression used is slightly different
    # from the python implementation
    # after a long night, this finally worked...
    content = content.replace(chr(10), '')
    content = content.replace('=C', '\n')
    content = content.replace('=B', '\r')
    content = content.replace('=A', '\0')
    content = content.replace('=D', '=')
    try:
        decompressed = zlib.decompress(content, -zlib.MAX_WBITS)
    except zlib.error as e:
        raise DecodeNzbError(e)
    else:
        return decompressed

