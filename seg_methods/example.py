'''
For adding segementation methods here, make sure to follow the format of the example below

The function name must be the same as the file name

Make sure to add the file to the __init__.py file
'''

from typing import Any,Dict
import numpy as np

def example(im2seg:np.ndarray) ->np.ndarray:
	"""[summary]

	Args:
		im2seg ([type]): [description]

	Returns:
		[type]: [description]
	"""
	return np.where(im2seg>100,100,0)


def readConfig(fn: str)->Dict[str,Any]:
	"""This will read a config json file and produce a parameter dictionary for your function, if you need to

	Args:
		fn (str): the filename of the configfile

	Returns:
		dict[str,Any]: the output parameters
	"""

	params = dict()

	return params