# Enhanced bvh add-on (importer/exporter) for blender

- [Enhanced bvh add-on (importer/exporter) for blender](#enhanced-bvh-add-on-importerexporter-for-blender)
  - [Enhanced bvh importer](#enhanced-bvh-importer)
  - [Enhanced bvh exporter](#enhanced-bvh-exporter)
  - [How to](#how-to)
    - [Install](#install)
    - [Load .bvh data onto an existing armature](#load-bvh-data-onto-an-existing-armature)

**Author**: zhaoyafei0210@gmail.com

**github repo**: https://github.com/walkoncross/blender_bvh_addon_enhanced

Refer to for more information: 
https://docs.blender.org/manual/en/2.92/addons/import_export/anim_bvh.html

Enhanced version of blender's bvh add-on with more settings supported.

The bvh's rest pose should have the same handedness as the armature while could use a different up/forward definiton

## Enhanced bvh importer
New features:

- **Target**: support to load .bvh data onto an existing armature
- **Translation**: choose to load translation (a.k.a position) for all bones/only root bone/none from the MOTION part of .bvh file
- **Global Axis Conversion**: whether to convert from bvh axis orientions into Blender's default axis orientions(Z-up/Y forward)
- **Skip frames**: skip first #N frames inthe  the MOTION part of .bvh file
- **Add rest pose**: whether to add rest pose as the first frame in the animation curves.

![bvh_importer_new_features](/docs/bvh_importer_new_features.jpg)


## Enhanced bvh exporter

- **Forward and Up**: customerize the output axis orientations
- **Add rest pose**: whether to add rest pose as the first frame in the animation curves.

![bvh_exporter_new_features](/docs/bvh_exporter_new_features.jpg)

## How to

### Install

1. download a release version .zip from: https://github.com/walkoncross/blender_bvh_addon_enhanced/raw/main/io_anim_bvh_enhanced.zip; (OR: git clone this repo and make a zip file (io_anim_bvh_enhanced.zip) from ./io_anim_bvh_enhanced);

2. Blender -> Edit -> Perferences -> Add-ons -> Install, get the path of io_anim_bvh_enhanced.zip, install and **enable** the add-on

![install_addon_1](/docs/install_addon_1.jpg)

![install_addon_2](/docs/install_addon_2.jpg)

3. After Installation:

![enhanced_bvh_importer_menu](/docs/enhanced_bvh_importer_menu.jpg)

![enhanced_bvh_exporter_menu](/docs/enhanced_bvh_exporter_menu.jpg)

### Load .bvh data onto an existing armature
1. Select an existing armature object
2. File -> Import -> Motion Capture (.bvh), enhanced
3. Make settings
4. Import BVH

![load_onto_existing_armature](/docs/load_onto_existing_armature.jpg)