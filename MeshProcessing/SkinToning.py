import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

output = np.ones((2048, 2048, 3))

FFHQ_uv = np.array(Image.open("input/stage3_uv.png")).astype(np.uint64)
avgColour = np.sum(FFHQ_uv[-3:,:], (0, 1)) / (3 * np.shape(FFHQ_uv)[1])
output *= avgColour

plt.imsave("output/skin.png", output.astype(np.uint8))