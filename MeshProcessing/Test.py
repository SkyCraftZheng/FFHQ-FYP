import os
import sys
import bpy
import bmesh
import mathutils
from mathutils import Vector
from collections import deque

folder_path = "C:/Users/Katherine/Downloads/1/"
dest_folder = "C:/Users/Katherine/Downloads/Blender Python/"
file_path2 = "C:/Users/Katherine/Downloads/UMA/stage3_mesh_id.obj"
inner_path = "Object"
head_name = "stage3_mesh_id"
right_eyeball_name = "R_ball"
left_eyeball_name = "L_ball"
collection_name = "Generated Head and Eyes"
UMA_inner_mouth = bpy.data.objects['UMA_Human_Female_InnerMouth']
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
cut_labels = ["neck right", "neck right back", "neck back", "neck left back", "neck left", "neck front"]
cut_UMA_idx = [468, 470, 689, 132, 130, 690] 
cut_idx = [4683, 4800, 2135, 9567, 2186, 2155]
neck_weights = [0.05, 0.04, 0.2, 0.04, 0.05, 0.1]
inner_labels = ["tooth"]
inner_UMA_idx = [338]
inner_idx = [708]
inner_weights = [1]

def getLandMarkCoords(obj, labels, vert_idx):
    # Deselect all objects then select obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Get verticies and world matrix
    verticies = [v for v in bm.verts]
    worldMTX = obj.matrix_world
    
    result = {}
    
    # Find the verticies and record coordinates
    for label, lm_vert in zip(labels, vert_idx):
        for vert in verticies:
            if vert.index == lm_vert:
                result[label] = worldMTX @ vert.co
                break
            
    bpy.ops.object.mode_set(mode='OBJECT')
    return result

def alignLandMarks(obj, targetLM, labels, idx, weights, connected=True):
    # Deselect all objects then select the object that will be deformed
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Get verticies and world matrix
    verticies = [v for v in bm.verts]
    worldMTX = obj.matrix_world
    
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
            value=(targetLM[label]-worldCoords),
            use_proportional_edit=True,
            proportional_edit_falloff='SMOOTH',
            use_proportional_connected=connected,
            proportional_size=weight)
        print(label)
        print(targetLM[label]-worldCoords)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return

def cutNeck(object_name, cut_idx):
    # Deselect all objects then select the imported head mesh
    shead = bpy.data.objects[object_name]
    bpy.ops.object.select_all(action='DESELECT')
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend = False, use_expand=False, type='VERT')
    bm = bmesh.from_edit_mesh(shead.data)
    bm.verts.ensure_lookup_table()
    
    verticies = bm.verts
    startingVert = cut_idx[0]
    
    # Selecting starting vertex
    for vert in verticies:
        if vert.index == startingVert:
            vert.select = True
        else:
            vert.select = False
    
    # Selecting the shortest path from each pair of verticies and storing them
    selected = set()
    cut_idx = deque(cut_idx)
    cut_idx.rotate(-1)
    for cut_vert in cut_idx:
        for vert in verticies:
            if vert.index == cut_vert:
                vert.select = True
                bpy.ops.mesh.shortest_path_select()
                updateSelection(bm, selected)
                if cut_vert != cut_idx[-1]:
                    vert.select = True
    
    for edge in selected:
        edge.select = True
    
    bmesh.ops.split_edges(bm, edges=list(selected), use_verts=False)
    selectLower(bm)
    bpy.ops.mesh.delete(type='VERT')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return
    
def selectLower(bm):
    lowest = sys.maxsize
    verticies = bm.verts
    verticies.ensure_lookup_table()
    lowest_vert = verticies[0]
    
    for vert in verticies:
        if vert.co[2] < lowest:
            lowest = vert.co[2]
            lowest_vert.select = False
            lowest_vert = vert
            vert.select = True
        else:
            vert.select = False
    
    bpy.ops.mesh.select_linked()

def updateSelection(bm, selected):
    edges = bm.edges
    for edge in edges:
        if edge.select == True:
             selected.add(edge)
             edge.select = False

def exportUV(obj, file_name, dest_folder):
    
    def uvFromVertexAverage(uv_layer, vert):
        uvAverage = Vector((0.0, 0.0))
        noOfCorners = 0
        for loop in vert.link_loops:
            uvAverage += loop[uv_layer].uv
            noOfCorners += 1
        
        if noOfCorners != 0:
            return uvAverage / noOfCorners
        else:
            return None
    
    # Deselect all objects then select obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Prepare mesh for accessing its verticies
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    # Get verticies
    verticies = [v for v in bm.verts]
    uvLayer = bm.loops.layers.uv.active
    
    with open(os.path.join(dest_folder, file_name), 'w') as f:
        for vert in verticies:
            uvVector = uvFromVertexAverage(uvLayer, vert)
            f.write(str(vert.index) + ' ' + str(uvVector.x) + ' ' + str(uvVector.y) + '\n')
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return

def export(obj, objName, dest_folder):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    rig.select_set(True)
    
    bpy.ops.export_scene.fbx(
        filepath=dest_folder+objName+'.fbx', check_existing=True,
        use_selection=True, use_visible=False, use_active_collection=False, collection='',
        global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
        use_space_transform=True, bake_space_transform=False,
        object_types={'ARMATURE', 'EMPTY', 'MESH', 'OTHER'},
        use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF',
        colors_type='SRGB', prioritize_active_color=False, use_subsurf=False, use_mesh_edges=False,
        use_tspace=False, use_triangles=False, use_custom_props=False,
        add_leaf_bones=False, primary_bone_axis='X', secondary_bone_axis='-Y', use_armature_deform_only=False, armature_nodetype='NULL',
        bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0,
        path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True,
        axis_forward='Z', axis_up='Y'
    )

def duplicate(obj, data=True, actions=True):
    obj_copy = obj.copy()
    bpy.context.collection.objects.link(obj_copy)
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    return obj_copy

def main():
    # append the head generated head 
    """
    bpy.ops.wm.append(
        filepath=os.path.join(file_path + "1.blend", inner_path, head_name),
        directory=os.path.join(file_path, inner_path),
        filename=head_name
        )
    """
    
    objNames = [head_name, right_eyeball_name, left_eyeball_name]
    
    for name in objNames:
        bpy.ops.wm.obj_import( filepath = folder_path + name + ".obj")
    
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

    exportUV(shead, 'original_uv.txt', dest_folder)
    
    templateNames = ['Template_' + name for name in objNames]
    
    for obj, templateName in zip(objs, templateNames):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        armatureMod = obj.modifiers.new('Armeture Mod', 'ARMATURE')
        armatureMod.object = rig
        
        dataTransfer = obj.modifiers.new('Data Mod', 'DATA_TRANSFER')
        dataTransfer.object = bpy.data.objects[templateName]
        dataTransfer.use_vert_data = True
        dataTransfer.data_types_verts = {'VGROUP_WEIGHTS'}
        dataTransfer.vert_mapping = 'TOPOLOGY'
        
        bpy.ops.object.datalayout_transfer(modifier=dataTransfer.name)
        bpy.ops.object.modifier_apply(modifier=dataTransfer.name)
        
        dataTransfer = obj.modifiers.new('Data Mod', 'DATA_TRANSFER')
        dataTransfer.object = bpy.data.objects[templateName]
        dataTransfer.use_loop_data = True
        dataTransfer.data_types_loops = {'UV'}
        dataTransfer.loop_mapping = 'TOPOLOGY'
        
        bpy.ops.object.datalayout_transfer(modifier=dataTransfer.name)
        bpy.ops.object.modifier_apply(modifier=dataTransfer.name)
    
    exportUV(shead, 'dest_uv.txt', dest_folder)
    
    UMANeckLM = getLandMarkCoords(bpy.data.objects['UMA_Human_Female_Face'], cut_labels, cut_UMA_idx)
    alignLandMarks(shead, UMANeckLM, cut_labels, cut_idx, neck_weights)
    cutNeck(head_name, cut_idx)
    
    bpy.ops.object.select_all(action='DESELECT')
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    
    shrinkWrap = shead.modifiers.new('Shrink Wrap', 'SHRINKWRAP')
    shrinkWrap.target = bpy.data.objects["UMA_Human_Female_Face"]
    shrinkWrap.vertex_group = "Shrink"
    
    bpy.ops.object.modifier_apply(modifier=shrinkWrap.name)
    
    shead.vertex_groups.remove(shead.vertex_groups['Shrink'])
    
    # -------------------------
    bpy.ops.object.select_all(action='DESELECT')
    UMA_inner_mouth.select_set(True)
    bpy.context.view_layer.objects.active = UMA_inner_mouth
    
    innerMouth = duplicate(obj=bpy.context.active_object, data=True, actions=True)
    innerMouth.name = "inner_mouth"
    
    innerPos = getLandMarkCoords(shead, inner_labels, inner_idx)
    alignLandMarks(innerMouth, innerPos, inner_labels, inner_UMA_idx, inner_weights, connected=False)
    
    objs.append(innerMouth)
    objNames.append(innerMouth.name)
    
    for obj, objName in zip(objs, objNames):
        export(obj, objName, dest_folder)
    
    for obj in objs:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.delete()
    
if __name__ == "__main__":
    main()