import sys
import pickle
from hurry.filesize import size


def get_object_size(data):

    """
    # function to get size of object: 
    # 1. serialises the object using pickle
    # 2. gets size of pickle serialisation
    # 3. returns human readable format using size from hurry.filesize
    """
    return sys.getsizeof(pickle.dumps(data))