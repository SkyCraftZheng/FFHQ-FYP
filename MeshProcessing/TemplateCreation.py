import os
import sys
import bpy
import bmesh
import mathutils
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir )
    
import utils
from utils import getLandMarkCoords, alignLandMarks
import imp
imp.reload(utils)

file_path = os.path.join(dir, "input/stage3_mesh_id.obj")
object_name = "stage3_mesh_id"
UMA_head = bpy.data.objects['UMA_Face']
lm_labels = ["right tear duct", "top of head", "left tear duct", "tip of nose", "left mouth corner", "right mouth corner",
    "chin", "top lip", "bottom lip",
    "right top eyelid 1", "right top eyelid 2", "left top eyelid 1", "left top eyelid 2",
    "right bottom eyelid", "left bottom eyelid", "right ear", "left ear",
    "middle brow bridge", "right brow 1", "right brow 2", "left brow 1", "left brow 2",
    "right eye corner", "left eye corner"]
UMA_idx = [472, 682, 134, 709, 307, 646,
    713, 702, 696,
    478, 476, 138, 140,
    482, 144, 381, 43,
    717, 599, 559, 261, 221,
    475, 137]
FFHQ_idx = [4587, 10040, 2042, 703, 7771, 12908,
    676, 735, 706,
    18851, 3744, 1186, 1204,
    3759, 1214, 3039, 413,
    680, 11962, 3582, 6797, 6892,
    14123, 2099]
weights = [0.016, 0.4, 0.016, 0.1, 0.03, 0.03,
    0.13, 0.05, 0.05,
    0.02, 0.01, 0.02, 0.01,
    0.02, 0.02, 0.09, 0.09,
    0.2, 0.04, 0.031, 0.4, 0.031,
    0.021, 0.021]

def main():
    bpy.ops.wm.obj_import( filepath = file_path )

    # Transform the head mesh to the approriate scale, height and rotation
    shead = bpy.data.objects[object_name]
    resize_scale = 0.119
    bpy.ops.transform.resize(value=(resize_scale, resize_scale, resize_scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False)
    upTrans = 1.82346
    forwardTrans = -0.019
    bpy.ops.transform.translate(value=(0, forwardTrans, upTrans), orient_type='GLOBAL')
    shead.rotation_euler[0] = 1.6491138
    
    UMAlm = getLandMarkCoords(UMA_head, lm_labels, UMA_idx)
    alignLandMarks(UMAlm, lm_labels, FFHQ_idx, weights)

if __name__ == "__main__":
    main()