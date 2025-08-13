import os
import bpy
import bmesh
import mathutils

file_path = "C:/Users/Katherine/Downloads/UMA/stage3_mesh_id.obj"
inner_path = "Object"
object_name = "stage3_mesh_id"
rig = bpy.data.objects['UMA_Female_Rig']
lm_labels = ["right tear duct", "top of head", "left tear duct", "tip of nose", "left mouth corner", "right mout corner",
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

def getLandMarkCoords(labels, vert_idx):
    # Deselect all objects then select UMA Head Mesh
    UMAMesh = bpy.data.objects['UMA_Human_Female_Face']
    bpy.ops.object.select_all(action='DESELECT')
    UMAMesh.select_set(True)
    bpy.context.view_layer.objects.active = UMAMesh
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(UMAMesh.data)
    
    # Get verticies and world matrix
    verticies = [v for v in bm.verts]
    worldMTX = UMAMesh.matrix_world
    
    result = {}
    
    # Find the verticies and record coordinates
    for label, lm_vert in zip(labels, vert_idx):
        for vert in verticies:
            if vert.index == lm_vert:
                result[label] = worldMTX @ vert.co
                break
            
    bpy.ops.object.mode_set(mode='OBJECT')
    return result

def alignLandMarks(UMAlm, labels, idx, weights):
    # Deselect all objects then select the imported head mesh
    shead = bpy.data.objects[object_name]
    bpy.ops.object.select_all(action='DESELECT')
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(shead.data)
    
    # Get verticies and world matrix
    verticies = [v for v in bm.verts]
    worldMTX = shead.matrix_world
    
    # Sort landmarks by weight, so that the finer details are adjusted last and so they can be accurate
    landMarks = list(zip(labels, idx, weights))
    landMarks.sort(reverse=True, key=lambda item: item[2])
    
    # Align the verticies
    for label, lm_vert, weight in landMarks:
        for vert in verticies:
            if vert.index == lm_vert:
                worldCoords = worldMTX @ vert.co
                vert.select = True
            else:
                vert.select = False
        bpy.ops.transform.translate(
            value=(UMAlm[label]-worldCoords),
            use_proportional_edit=True,
            proportional_edit_falloff='SMOOTH',
            use_proportional_connected=True,
            proportional_size=weight)
        print(label)
        print(UMAlm[label]-worldCoords)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return

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
    
    UMAlm = getLandMarkCoords(lm_labels, UMA_idx)
    alignLandMarks(UMAlm, lm_labels, FFHQ_idx, weights)

if __name__ == "__main__":
    main()