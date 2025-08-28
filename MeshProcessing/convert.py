import os
import bpy

file_path = "C:/Users/Katherine/Downloads/1/1.blend"
inner_path = "Object"
object_name = "stage3_mesh_id"
rig = bpy.data.objects['UMA_Female_Rig']
 
def main():
    # append the head generated head 
    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, object_name),
        directory=os.path.join(file_path, inner_path),
        filename=object_name
        )
    
    # Transform the head mesh to the approriate scale, height and rotation
    shead = bpy.data.objects['stage3_mesh_id']
    resize_scale = 0.119
    bpy.ops.transform.resize(value=(resize_scale, resize_scale, resize_scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False)
    upTrans = 1.82346
    forwardTrans = -0.019
    bpy.ops.transform.translate(value=(0, forwardTrans, upTrans), orient_type='GLOBAL')
    shead.rotation_euler[0] = 1.6491138
    
    # Create a sphere to cut off the shoulders
    upTrans = 1.33746
    forwardTrans = 0.1671
    resize_scale = 0.394
    bpy.ops.mesh.primitive_uv_sphere_add(segments=45, ring_count=25, radius=0.394, enter_editmode=False, align='WORLD',
        location=(0, forwardTrans, upTrans), scale=(1, 1, 1))
    ssphere = bpy.data.objects['Sphere']
    
    # Cutting off the shoulders
    ssphere.select_set(False)
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    
    booleanMod = shead.modifiers.new('Boolean Mod', 'BOOLEAN')
    booleanMod.object = ssphere
    
    bpy.ops.object.modifier_apply(modifier=booleanMod.name)
    
    bpy.ops.object.select_all(action='DESELECT')
    ssphere.select_set(True)
    bpy.ops.object.delete()
    
    bpy.context.view_layer.objects.active = shead
    #verts=bpy.context.active_object.data.vertices
    #for v in verts:
    #   if v.co[3] > 10:
    #      v.select=True
    #   else:
    #      v.select=False
    
    # Prepare head for export
    shead.select_set(True)
    bpy.context.view_layer.objects.active = shead
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    armatureMod = shead.modifiers.new('Armeture Mod', 'ARMATURE')
    armatureMod.object = rig
    
    dataTransfer = shead.modifiers.new('Data Mod', 'DATA_TRANSFER')
    dataTransfer.object = bpy.data.objects['UMA_Human_Female']
    dataTransfer.use_vert_data = True
    dataTransfer.data_types_verts = {'VGROUP_WEIGHTS'}
    dataTransfer.vert_mapping = 'POLYINTERP_NEAREST'
    
    bpy.context.view_layer.objects.active = shead
    bpy.ops.object.datalayout_transfer(modifier=dataTransfer.name)
    bpy.ops.object.modifier_apply(modifier=dataTransfer.name)
    
    rig.select_set(True)
    
    bpy.ops.export_scene.fbx(filepath='C:/Users/Katherine/Downloads/Blender Python/test.fbx', check_existing=True,
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
        axis_forward='Z', axis_up='Y')

if __name__ == "__main__":
    main()