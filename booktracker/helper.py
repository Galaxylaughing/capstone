import os
from binascii import hexlify
                             
                             
def create_hash():
    """
    os.urandom(size) : Return a string of size random bytes suitable for cryptographic use,
    https://docs.python.org/3/library/os.html?highlight=urandom#os.urandom

    binascii is a module that converts between binary and ASCII,
    https://docs.python.org/2/library/binascii.html

    hexlify(data) : Return the hexadecimal representation of the binary data,
    https://docs.python.org/2/library/binascii.html#binascii.hexlify
    """
    return str(hexlify(os.urandom(16)), 'ascii')
