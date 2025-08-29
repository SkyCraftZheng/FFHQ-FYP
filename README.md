# Customisable 3D Avatar Platform
This project's technical report can be found [here](https://drive.google.com/file/d/1Wo68VDdgVpRwTQSnCpJw2oN-_OsH2O6G/view?usp=sharing). The aim of this project is to integrate the output of [FFHQ-UV](https://github.com/RaymondGuo2/FFHQ-UV-RGB/tree/b0627f10423925203ed3606506bd3b8e497a7cc1) to [UMA](https://assetstore.unity.com/packages/3d/characters/uma-2-35611).
This is persued for the purposes of enhancing [SAT](https://ieeexplore.ieee.org/abstract/document/7280780) interventions, in providing a more realistic and accurate representation of the patient.

Template creation, mesh processing and UV remapping is implemented in Python, as that is the supported scripting language for [Blender](https://www.blender.org/), for the template creation and mesh processing, Blender is used. To load the Python dependencies, MeshProcessing.yml loaded in conda-forge will install them.

```
cd MeshProcessing/
conda env create -f MeshProcessing.yml
conda activate MeshProcessing
```

All of the Blender scripts assume the naming convention for objects within `MeshProcessing/UMA Blender Female Unified.blend` and `MeshProcessing/UMA Blender Female Unified.blend`.

## Template, Metallic Nap and Normal Map Creation
For template creation, the `MeshProcessing/TemplateCreation.py` script was used for importing the template head model the initial alignment of the template. This script does not save or export the result, meaning that it has to be run inside Blender for its results to be observed and tweaked. This script assumes the `.obj` file that is used to create a template is located at `./input/stage3_mesh_id.obj` relative to the open Blender file. 

For remapping normal and metallic maps is implemented in the `MeshProcessing/TextureTransfer.py` script, which assumes that the original UMA maps are located relative to its position at `./UMA_maps/metallic.png` and `./UMA_maps/normal.png`. It also assumes the uv information is in `./uv_data/` with `original_uv.txt` containing the original uv data, `dest_uv.txt` the remapped uv data and `face_topology.txt` the face indices and the corresponding vertices' indices. It also assumes that it is in the same folder as `utils.py`, which contains the implementation for retrieving landmark coordinates and aligning landmarks. The remapped images are outputted at `./output/metallic.png` and `./output/normal.png`.

## Processing a Newly Generated Mesh
The 2d image is processed by [FFHQ-UV](https://github.com/RaymondGuo2/FFHQ-UV-RGB/tree/b0627f10423925203ed3606506bd3b8e497a7cc1). Then the following files are transferred by hand to `MeshProcessing/input/`: `L_ball.obj`, `R_ball.obj`, `stage3_mesh_id.obj`, `stage3_mesh.mtl`, `eye_ball_tex.mtl` and `stage3_uv.png`.

Then the generated mesh can be processed and prepared for slot conversion with:

```
{Blender} {UMA Blender file} -b --python ./ProcessMeshes.py
```

Where \{Blender\} is the location of the Blender executable file and \{UMA Blender file\} is the Blender file for the appropriate gender: `MeshProcessing/UMA Blender Female Unified.blend` or `MeshProcessing/UMA Blender Male Unified.blend`. The script, `ProcessMeshes.py`, assumes the file structure relative to the Blender file and script is the output of the FFHQ-UV is in `./input/`. It also assumes it is in the same folder as `utils.py` which contains the implementation for aligning landmarks and cutting the neck. It then outputs the processed meshes in `./output/`

The FFHQ-UV generated texture can be stretched with

```
python ./Stretch.py
```

With the assumption that, relative to the script, the input image is at `/input/stage3_uv.png` and outputs at `output/stage3_uv_stretched.png`. Note that the image is opened and its type is changed to 32 bit unsigned integer to prevent integer overflow when calculating averages, then it is converted back to 8 bit unsigned integer for exporting to png.

## Applying the Processed Mesh
Open this project in [Unity](https://unity.com/) (this project was done in version 6000.1.1f1). To do so, install Unity, clone this repository into an empty folder, then in Unity Hub in the `Projects` tab click `Add` > `Add project from disk`, select the folder this repository was cloned into. It then should show up under projects, you can open it by clicking on it.

Import the processed .fbx files and the stretched texture into Unity. Update `Assets/FFHQ/FFHQ Overlay.asset` to use the imported stretched texture by dragging and dropping, and similarly update the `Assets/FFHQ/Slots/eyes/eyes_slot`, `Assets/FFHQ/Slots/inner_mouth/inner_mouth_slot` and `Assets/FFHQ/Slots/stage3_mesh_id/stage3_mesh_id_slot` for the female model. For the male model update the slots with the same names but with `Male_` in front of them.

## UI and customisation
Buttons were set up to change the hairstyle of the avatar along with changing in between the original UMA head, the processed FFHQ-UV head on the other hand and DNA\&Overlay method.

Buttons in Unity call a function within an attached script when pressed, the script `Assets/Buttons.cs` houses these functions. For changing recipes, UMA provides a simple way of doing so, the `DynamicCharacterAvatar` has a method `.ClearSlot(slot)` which clears all recipes that occupies the specified slot. It also has a method `.SetSlot(recipe)` which applies the specified recipe to the avatar. For these changes to take effect the avatar needs to be rebuilt, which is done with `.BuildCharacter()` method.

## A compiled demo
A compiled demo can be found in `WindowsBuild/`. Either clone this repository or download only `WindowsBuild/` folder, the demo can be run by running `FFHQ.exe`
