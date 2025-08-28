import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

original_image = os.path.join("input", "stage3_uv.png")
output_name = os.path.join("output", "stage3_uv_streched.png")

oriImg = np.array(Image.open(original_image)).astype(np.uint32)
shape = np.shape(oriImg)
shape = (shape[0], shape[1]*2, shape[2])
result = np.zeros(shape)
for x in range(shape[1]):
    if x % 2 == 0 or x == shape[1] - 1:
        result[:, x, :] = oriImg[:, x//2, :]
    else:
        result[:, x, :] = (oriImg[:, x//2, :] + oriImg[:, x//2 + 1, :])/2
plt.imsave(output_name, result.astype(np.uint8))