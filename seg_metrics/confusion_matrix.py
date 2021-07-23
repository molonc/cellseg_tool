import numpy as np

def tn(im_seg,im_gt):
    _tp = np.logical_and(im_seg,im_gt)
    return np.logical_not(_tp).sum()

def tp(im_seg,im_gt):
	return np.logical_and(im_seg,im_gt).sum()

def fn(im_seg,im_gt):
	return np.multiply(im_gt,np.logical_xor(im_seg,im_gt)).sum()

def fp(im_seg,im_gt):
	return np.multiply(im_seg,np.logical_xor(im_seg,im_gt)).sum()