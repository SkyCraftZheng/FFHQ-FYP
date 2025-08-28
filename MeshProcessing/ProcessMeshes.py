import os
import sys
import bpy

dir = os.path.dirname(bpy.data.filepath)
print(dir)
if not dir in sys.path:
    sys.path.append(dir )
    
import utils
import imp
imp.reload(utils)
from utils import *

input_path = os.path.join(dir, "input/")
output_folder = os.path.join(dir, "output/")
head_name = "stage3_mesh_id"
right_eyeball_name = "R_ball"
left_eyeball_name = "L_ball"
eyes_name = "eyes"
UMA_inner_mouth = bpy.data.objects['UMA_InnerMouth']
rig = bpy.data.objects['UMA_Rig']
UMA_head = bpy.data.objects['UMA_Face']
cut_labels = ["neck right", "neck right back", "neck back", "neck left back", "neck left", "neck front"]
cut_UMA_idx = [468, 470, 689, 132, 130, 690] 
cut_idx = [4683, 4800, 2135, 9567, 2186, 2155]
neck_weights = [0.05, 0.04, 0.2, 0.04, 0.05, 0.2]
inner_labels = ["tooth"]
inner_UMA_idx = [338]
inner_idx = [708]
inner_weights = [1]

def main():
    # Import generated head
    objNames = [head_name, right_eyeball_name, left_eyeball_name]
    for name in objNames:
        bpy.ops.wm.obj_import( filepath = os.path.join(input_path, name + ".obj"))
    
    bpy.ops.object.select_all(action='DESELECT')
    
    shead = bpy.data.objects[head_name]
    sReye = bpy.data.objects[right_eyeball_name]
    sLeye = bpy.data.objects[left_eyeball_name]
    objs = [shead, sReye, sLeye]
    for obj in objs:
        obj.select_set(True)
        for poly in obj.data.polygons:
            poly.use_smooth = True

    # Transform the head mesh to the approriate scale, height and rotation
    resize_scale = 0.119
    bpy.ops.transform.resize(value=(resize_scale, resize_scale, resize_scale), orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')
    upTrans = 1.82346
    forwardTrans = -0.019
    bpy.ops.transform.translate(value=(0, forwardTrans, upTrans), orient_type='GLOBAL')
    for obj in objs:
        obj.rotation_euler[0] = 1.6491138

    # Export the original and template UV data of FFHQ-UV mesh
    # exportUV(shead, 'M_original_uv.txt', output_folder)
    # templateHead = bpy.data.objects['Template_stage3_mesh_id']
    # exportUV(templateHead, 'M_dest_uv.txt', output_folder)
    # print(verifyContinuity(templateHead))
    # exportFaces(shead, 'M_face_topology.txt', output_folder)
    
    # Skinning the meshes from templates
    templateNames = ['Template_' + name for name in objNames]
    
    for obj, templateName in zip(objs, templateNames):
        # Select object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Add armarue modifier
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        armatureMod = obj.modifiers.new('Armeture Mod', 'ARMATURE')
        armatureMod.object = rig
        
        # Transfer vertex group data
        dataTransfer = obj.modifiers.new('Data Mod', 'DATA_TRANSFER')
        dataTransfer.object = bpy.data.objects[templateName]
        dataTransfer.use_vert_data = True
        dataTransfer.data_types_verts = {'VGROUP_WEIGHTS'}
        dataTransfer.vert_mapping = 'TOPOLOGY'
        
        bpy.ops.object.datalayout_transfer(modifier=dataTransfer.name)
        bpy.ops.object.modifier_apply(modifier=dataTransfer.name)
        
        if obj != shead:
            # Transfer UV data
            dataTransfer = obj.modifiers.new('Data Mod', 'DATA_TRANSFER')
            dataTransfer.object = bpy.data.objects[templateName]
            dataTransfer.use_loop_data = True
            dataTransfer.data_types_loops = {'UV'}
            dataTransfer.loop_mapping = 'TOPOLOGY'
            bpy.ops.object.datalayout_transfer(modifier=dataTransfer.name)
            bpy.ops.object.modifier_apply(modifier=dataTransfer.name)
    
    # Align and cut neck
    UMANeckLM = getLandMarkCoords(UMA_head, cut_labels, cut_UMA_idx)
    for key, value in UMANeckLM.items():
        value.z -= 0.001
        UMANeckLM[key] = value 
    alignLandMarks(shead, UMANeckLM, cut_labels, cut_idx, neck_weights)
    cutNeck(head_name, cut_idx)
    
    # Apply shrink wrap to 'Shrink' to align neck seam
    bpy.ops.object.select_all(action='DESELECT')
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    
    shrinkWrap = shead.modifiers.new('Shrink Wrap', 'SHRINKWRAP')
    shrinkWrap.target = UMA_head
    shrinkWrap.vertex_group = "Shrink"
    
    bpy.ops.object.modifier_apply(modifier=shrinkWrap.name)
    
    shead.vertex_groups.remove(shead.vertex_groups['Shrink'])
    
    # Join the eyes into a single object
    bpy.ops.object.select_all(action='DESELECT')
    sReye.select_set(True)
    sLeye.select_set(True)
    bpy.context.view_layer.objects.active = sReye
    bpy.ops.object.join()
    seye = bpy.context.view_layer.objects.active
    seye.name = eyes_name
    
    # Copy UMA inner mouth and align it
    bpy.ops.object.select_all(action='DESELECT')
    UMA_inner_mouth.select_set(True)
    bpy.context.view_layer.objects.active = UMA_inner_mouth
    
    innerMouth = duplicate(obj=bpy.context.active_object, data=True, actions=True)
    innerMouth.name = "inner_mouth"
    
    innerPos = getLandMarkCoords(shead, inner_labels, inner_idx)
    alignLandMarks(innerMouth, innerPos, inner_labels, inner_UMA_idx, inner_weights, connected=False)
    
    objs = [shead, seye, innerMouth]
    objNames = [head_name, eyes_name, innerMouth.name]
    
    # Export processed objects
    for obj, objName in zip(objs, objNames):
        export(obj, objName, output_folder, rig)
    
    for obj in objs:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()
    
    
if __name__ == "__main__":
    main()