from cellpose import models
import numpy as np
from typing import Any,Dict

def _cellpose(img,model_type):

    param = readConfig('./cellpose.json')

    model = models.Cellpose(gpu=False, model_type=model_type)

    masks, _,_,_ = model.eval(img, diameter=None,channels=[0,0])

    return masks

def cellpose_cyto(img):
    return _cellpose(img,'cyto')

def cellpose_nuc(img):
    return _cellpose(img,'nuclei')


def readConfig(fn: str)->Dict[str,Any]:
    """This will read a config json file and produce a parameter dictionary for your function, if you need to

    Args:
        fn (str): the filename of the configfile

    Returns:
        dict[str,Any]: the output parameters
    """

    params = dict()

    return params