import numpy as np

def iou(im_seg:np.ndarray,im_gt:np.ndarray)->float:
    """Calculates the intersection over union of the im_seg against im_gt.
    It is assumed that both are integer arrays with the background as 0 and the foreground being any value higher than zero.

    Args:
        im_seg (np.ndarray): [description]
        im_gt (np.ndarray): [description]

    Returns:
        float: [description]
    """
    im_seg = np.where(im_seg>1,1,0).astype(int)
    im_gt = np.where(im_gt>1,1,0).astype(int)
    
    _inters = np.logical_and(im_seg,im_gt).sum()
    _union = np.logical_or(im_seg,im_gt).sum()

    _iou = _inters/_union
    return _iou