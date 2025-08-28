import os
import matplotlib.pyplot as plt
import numpy as np
import math
from PIL import Image

file_names = ["normal.png", "metallic.png"]
UMA_files = map(lambda file: os.path.join("UMA_maps", file), file_names)
output_files = map(lambda file: os.path.join("output", file), file_names)
topology_file = os.path.join("uv_data", "face_topology.txt")
dest_uv = os.path.join("uv_data", "dest_uv.txt")
original_uv = os.path.join("uv_data", "original_uv.txt")

def processContent(content):
    result = list(map(lambda line: list(map(lambda word: float(word), line.split())), content))
    result.sort(key=lambda line : line[0])
    return list(map(lambda line : [line[1], 1.0 - line[2]], result))

def calcCoords(uvCoord, width, height):
    return (int(uvCoord[1]*height), int(uvCoord[0]*width))

def colourFace(vertCoords, FFHQ_uv, UMA_uv, FFHQ_to_UMA, avg_flag=False):
    def det(coord1, coord2):
        return coord1[1]*coord2[0] - coord1[0]*coord2[1]
    def sub(coord1, coord2):
        return [coord1[0] - coord2[0], coord1[1] - coord2[1]]
    def dist(coord1, coord2):
        diff = sub(coord1, coord2)
        return math.sqrt(diff[0]**2 + diff[1]**2)
    
    xs = list(map(lambda coord: coord[1], vertCoords))
    ys = list(map(lambda coord: coord[0], vertCoords))
    v0 = vertCoords[0]
    v1 = sub(vertCoords[1], v0)
    v2 = sub(vertCoords[2], v0)
    xs.sort()
    ys.sort()

    det12 = det(v1, v2)
    if dist(v1, [0, 0]) > 200 or dist(v2, [0, 0]) > 200 or dist(v1, v2) > 200 or det12 == 0:
        return FFHQ_uv

    for x in range(xs[0], xs[-1]+1):
        for y in range(ys[0], ys[-1]+1):
            v = sub([y,x], v0)
            a = (det(v, v2)) / det12
            b = -(det(v, v1)) / det12
            if a > -0.01 and b > -0.01 and a + b < 1:
                if not avg_flag:
                    UMA_v0 = FFHQ_to_UMA[vertCoords[0]]
                    UMA_v1 = sub(FFHQ_to_UMA[vertCoords[1]], UMA_v0)
                    UMA_v2 = sub(FFHQ_to_UMA[vertCoords[2]], UMA_v0)
                    x_uv = int(UMA_v0[1] + a*UMA_v1[1] + b*UMA_v2[1])
                    y_uv = int(UMA_v0[0] + a*UMA_v1[0] + b*UMA_v2[0])
                    #if FFHQ_to_UMA[y, x].any():
                    #    continue
                    FFHQ_to_UMA[y, x] = [y_uv, x_uv]
                    FFHQ_uv[y, x] = UMA_uv[y_uv, x_uv]
                else:
                    weight0 = dist(v0, v)
                    weight1 = dist(vertCoords[1], v)
                    weight2 = dist(vertCoords[2], v)
                    FFHQ_uv[y, x] = (FFHQ_uv[vertCoords[0]]*weight0 \
                        + FFHQ_uv[vertCoords[1]]*weight1 \
                        + FFHQ_uv[vertCoords[2]]*weight2) / (weight0 + weight1 + weight2)
    return FFHQ_uv

# Open and read the exported data
with open(dest_uv, 'r') as destFile:
    destContent = destFile.read().splitlines()
with open(original_uv, 'r') as originalFile:
    originalContent = originalFile.read().splitlines()
with open(topology_file, 'r') as topoFile:
    faces = topoFile.read().splitlines()
    faces = map(lambda line: list(map(lambda word: int(word), line.split())), faces)
    faces = list(map(lambda line: line[1:], faces))

dest = processContent(destContent)
original = processContent(originalContent)

for UMA_file, output_file in zip(UMA_files, output_files):
    # Read UMA maps
    UMA_uv = np.array(Image.open(UMA_file)).astype(np.uint32)
    FFHQ_uv = np.copy(UMA_uv)#np.zeros(np.shape(UMA_uv)).astype(np.uint32) #np.array(Image.open('stage3_uv.png'))

    FFHQ_width = np.shape(FFHQ_uv)[1]
    FFHQ_height = np.shape(FFHQ_uv)[0]

    UMA_width = np.shape(UMA_uv)[1]
    UMA_height = np.shape(UMA_uv)[0]

    # FFHQ_uv = np.append(FFHQ_uv, 255*np.ones((np.shape(FFHQ_uv)[0], np.shape(FFHQ_uv)[1], 1)), axis=2)

    # Create a map from FFHQ unwrapping to UMA unwrapping
    FFHQ_to_UMA = np.zeros((np.append(np.shape(FFHQ_uv)[:2], 2)))

    for originalUV, destUV in zip(original, dest):
        UMACoords = calcCoords(destUV, UMA_width, UMA_height)
        FFHQCoords = calcCoords(originalUV, FFHQ_width, FFHQ_height)
        FFHQ_uv[FFHQCoords] = UMA_uv[UMACoords] # Transfer UMA map colour to FFHQ unwrapping on vertices
        FFHQ_to_UMA[FFHQCoords] = UMACoords

    # Fill out the faces
    for face in faces:
        vertCoords = []
        for vert in face:
            vertCoords.append(calcCoords(original[vert], FFHQ_width, FFHQ_height))
        FFHQ_uv = colourFace(vertCoords, FFHQ_uv, UMA_uv, FFHQ_to_UMA)
        
    # Save the result
    plt.imsave(output_file, FFHQ_uv.astype(np.uint8))