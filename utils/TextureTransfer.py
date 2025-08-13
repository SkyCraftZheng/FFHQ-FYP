import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from collections import deque 

def processContent(content):
    result = []
    for line in content:
        words = deque(line.split())
        result.append([])
        while words:
            result[-1].append(float(words.popleft()))
    result.sort(key=lambda line : line[0])
    return map(lambda line : [line[1], 1.0 - line[2]], result)

def calcCoords(uvCoord, width, height):
    return (int(uvCoord[1]*height), int(uvCoord[0]*width))

def calcColour(UMA_coord, UMA_to_FFHQ, FFHQ_uv):
    mapped = []
    for i in range(np.shape(UMA_to_FFHQ)[0]):
        for j in range(np.shape(UMA_to_FFHQ)[1]):
            if UMA_to_FFHQ[i, j].any():
                mapped.append([i, j])
    closest = []
    for coord in mapped:
        if len(closest) < 3:
            closest.append(coord)
            if len(closest) == 3:
                closest.sort(key=lambda x: np.linalg.norm(x - UMA_coord))
            continue
        if np.linalg.norm(coord-UMA_coord) < np.linalg.norm(closest[2]-UMA_coord):
            if np.linalg.norm(coord-UMA_coord) < np.linalg.norm(closest[1]-UMA_coord):
                if np.linalg.norm(coord-UMA_coord) < np.linalg.norm(closest[0]-UMA_coord):
                    closest.insert(0, coord)
                else:
                    closest.insert(1, coord)
            else:
                closest.insert(2, coord)
            closest.pop()
    colour = np.array([0, 0, 0, 0])
    for coord in closest:
        FFHQ_coord = UMA_to_FFHQ[coord[0], coord[1]]
        colour = colour + FFHQ_uv[int(FFHQ_coord[0]), int(FFHQ_coord[1])]
    return colour / 3
    
with open('dest_uv.txt', 'r') as destFile:
    destContent = destFile.read().splitlines()
with open('original_uv.txt', 'r') as originalFile:
    originalContent = originalFile.read().splitlines()

dest = processContent(destContent)
original = processContent(originalContent)

FFHQ_uv = np.array(Image.open('stage3_uv.png'))
UMA_uv = np.array(Image.open('UMA_uv.png'))

FFHQ_width = np.shape(FFHQ_uv)[1]
FFHQ_height = np.shape(FFHQ_uv)[0]

UMA_width = np.shape(UMA_uv)[1]
UMA_height = np.shape(UMA_uv)[0]

FFHQ_uv = np.append(FFHQ_uv, 255*np.ones((np.shape(FFHQ_uv)[0], np.shape(FFHQ_uv)[1], 1)), axis=2)

UMA_to_FFHQ = np.zeros((np.append(np.shape(UMA_uv)[:2], 2)))

for originalUV, destUV in zip(original, dest):
    UMACoords = calcCoords(destUV, UMA_width, UMA_height)
    FFHQCoords = calcCoords(originalUV, FFHQ_width, FFHQ_height)
    UMA_to_FFHQ[UMACoords] = FFHQCoords
for i in range(FFHQ_height):
    for j in range(FFHQ_width):
        UMA_uv[i, j] = calcColour(np.array([i, j]), UMA_to_FFHQ, FFHQ_uv)

plt.imsave('test.png', UMA_uv)