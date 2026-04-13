import numpy as np
from src.core.layer import LayerManager, Layer

w,h=200,150
lm=LayerManager()
lm.set_canvas_size(w,h)
# red opaque background
img1=np.zeros((h,w,4),dtype=np.uint8)
img1[:,:,2]=255
img1[:,:,3]=255
layer1=Layer(name='red', image=img1)
lm.add_layer(layer1)
# green semi-transparent overlay
img2=np.zeros((h,w,4),dtype=np.uint8)
img2[:,:,1]=255
img2[:,:,3]=128
layer2=Layer(name='green', image=img2, opacity=0.8)
lm.add_layer(layer2)
out=lm.flatten()
print('flatten ok', out.shape, out.dtype, 'max=', out.max())
