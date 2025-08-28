import os
import sys
import bpy
import bmesh
from mathutils import Vector
from collections import deque

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
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return

def cutNeck(object_name, cut_idx):
    
    def updateSelection(bm, selected):
        edges = bm.edges
        for edge in edges:
            if edge.select == True:
                 selected.add(edge)
                 edge.select = False
    
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
    
    # Selecting the shortest path from each pair of verticies and storing the edges defined by them
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
    
    # Select all the stored edges
    for edge in selected:
        edge.select = True
    
    # Cut and delete shoulders 
    bmesh.ops.split_edges(bm, edges=list(selected), use_verts=False)
    selectLower(bm)
    bpy.ops.mesh.delete(type='VERT')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return

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
    
    # Transfer UV data
    with open(os.path.join(dest_folder, file_name), 'w') as f:
        for vert in verticies:
            uvVector = uvFromVertexAverage(uvLayer, vert)
            f.write(str(vert.index) + ' ' + str(uvVector.x) + ' ' + str(uvVector.y) + '\n')
        
    bpy.ops.object.mode_set(mode='OBJECT')
    return

def verifyContinuity(obj):
    
    def uvSame(uv_layer, vert):
        first = True
        for loop in vert.link_loops:
            if first:
                lastUV = loop[uv_layer].uv
            if lastUV != loop[uv_layer].uv:
                return False
        return True
    
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
    
    for vert in verticies:
        if not uvSame(uvLayer, vert):
            bpy.ops.object.mode_set(mode='OBJECT')
            return False
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return True

def exportFaces(obj, file_name, dest_folder):
    # Select the object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Prep mesh for editing
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    
    # Export face indices and associated vertex indices
    faces = [f for f in bm.faces]
    with open(os.path.join(dest_folder, file_name), 'w') as f:
        for face in faces:
            output = str(face.index)
            for vert in face.verts:
                output += ' ' + str(vert.index)
            f.write(output + '\n')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return
        

def export(obj, objName, dest_folder, rig):
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