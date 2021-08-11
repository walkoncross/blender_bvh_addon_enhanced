# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# By zhaoyafei0210@gmail.com (https://github.com/walkoncross)
# Modified on blender's bvh addon (import_bvh.py) by Campbell Barton

# <pep8-80 compliant>

bl_info = {
    "name": "BioVision Motion Capture (BVH) format, support more settings",
    "author": "Yafei Zhao",
    "version": (2, 0, 0),
    "blender": (2, 81, 6),
    "location": "File > Import-Export",
    "description": "Import-Export BVH from armature objects, support more settings",
    "warning": "",
    "doc_url": "https://github.com/walkoncross/blender_bvh_addon_enhanced/blob/main/README.md",
    "support": 'OFFICIAL',
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_bvh_enhanced" in locals():
        importlib.reload(import_bvh_enhanced)
    if "export_bvh_enhanced" in locals():
        importlib.reload(export_bvh_enhanced)

import bpy
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportBVHEnhanced(bpy.types.Operator, ImportHelper):
    """Load a BVH motion capture file"""
    bl_idname = "import_anim.bvh_enhanced"
    bl_label = "Import BVH"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".bvh"
    filter_glob: StringProperty(default="*.bvh", options={'HIDDEN'})

    # target: EnumProperty(
    #     items=(
    #         ('ARMATURE', "Armature", ""),
    #         ('OBJECT', "Object", ""),
    #     ),
    #     name="Target",
    #     description="Import target type",
    #     default='ARMATURE',
    # )

    items = (
        ('NEW_ARMATURE', "New Armature", "Load bvh data to create a new armature and "),
        ('NEW_PARENTED_OBJECTS', "New Parented Objects", "Load bvh data to creat Parented Objects, each bone as an object"),
        ('EXISTING_ARMATURE', "Existing Armature", "Load bvh data onto existing armature, select an armature object before loading"),
    )
    # for obj in bpy.context.scene.collection.all_objects:
    #     if obj.type is "ARMATURE":
    #         items += ((obj.name, obj.name, "Load bvh data onto existing armature"),)
            
    target: EnumProperty(
        items=items,
        name="Target",
        description="Import target type",
        default='NEW_ARMATURE',
    )
    armature: StringProperty(
        name="Armature",
        description="The selected existing armature to load bvh onto",
        default='None',
    )
    # target: StringProperty(
    #     name="Target",
    #     description="Import target type",
    #     default='NEW_ARMATURE',
    # )
    global_scale: FloatProperty(
        name="Scale",
        description="Scale the BVH by this value",
        min=0.0001, max=1000000.0,
        soft_min=0.001, soft_max=100.0,
        default=1.0,
    )
    skip_frames: IntProperty(
        name="Skip Frames",
        description="Skip first #skip_frames frames in the .bvh file, e.g. skip the first frame as it may be the rest pose",
        default=0,
    )
    frame_start: IntProperty(
        name="Start Frame",
        description="Starting frame for the animation curve",
        default=1,
    )
    use_fps_scale: BoolProperty(
        name="Scale FPS",
        description=(
            "Scale the framerate from the BVH to the current scenes, "
            "otherwise each BVH frame maps directly to a Blender frame"
        ),
        default=False,
    )
    update_scene_fps: BoolProperty(
        name="Update Scene FPS",
        description=(
            "Set the scene framerate to that of the BVH file (note that this "
            "nullifies the 'Scale FPS' option, as the scale will be 1:1)"
        ),
        default=False,
    )
    update_scene_duration: BoolProperty(
        name="Update Scene Duration",
        description="Extend the scene's duration to the BVH duration (never shortens the scene)",
        default=False,
    )
    use_cyclic: BoolProperty(
        name="Loop (Not Implemented)",
        description="Loop the animation playback",
        default=False,
    )
    rotate_mode: EnumProperty(
        name="Rotation",
        description="Rotation conversion",
        items=(
            ('QUATERNION', "Quaternion",
             "Convert rotations to quaternions"),
            ('NATIVE', "Euler (Native)",
             "Use the rotation order defined in the BVH file"),
            ('XYZ', "Euler (XYZ)", "Convert rotations to euler XYZ"),
            ('XZY', "Euler (XZY)", "Convert rotations to euler XZY"),
            ('YXZ', "Euler (YXZ)", "Convert rotations to euler YXZ"),
            ('YZX', "Euler (YZX)", "Convert rotations to euler YZX"),
            ('ZXY', "Euler (ZXY)", "Convert rotations to euler ZXY"),
            ('ZYX', "Euler (ZYX)", "Convert rotations to euler ZYX"),
        ),
        default='NATIVE',
    )
    translation_mode: EnumProperty(
        name="Translation",
        description="How to deal with translation",
        items=(
            ('TRANSLATION_FOR_ALL_BONES', "All bones", "Load translation for all bones"),
            ('TRANSLATION_FOR_ROOT_BONE', "Only root", "Only load translation for root bone"),
            ('TRANSLATION_FOR_NONE_BONE', "None", "Discard translation for all bones"),
        ),
        default='TRANSLATION_FOR_ALL_BONES',
    )
    apply_axis_conversion: BoolProperty(
        name="Global Axis Conversion",
        description="Make global transform from BVH file's coordinates system into Blender's coordinates system",
        default=False,
    )
    add_rest_pose_as_first_frame: BoolProperty(
        name="Add Rest Pose",
        description="Add rest pose as the first frame",
        default=False,
    )
    def execute(self, context):
        keywords = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "filter_glob",
            )
        )
        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4()

        keywords["global_matrix"] = global_matrix

        if keywords["target"] == "EXISTING_ARMATURE": 
            if keywords["armature"] in bpy.data.objects.keys():
                obj = bpy.data.objects[keywords["armature"]]

                if obj.type == 'ARMATURE':
                    keywords["target"] = keywords["armature"]
                else:
                    keywords["target"] = "NEW_ARMATURE"
            else:
                keywords["target"] = "NEW_ARMATURE"
                
        keywords.pop('armature', None)

        from . import import_bvh_enhanced
        return import_bvh_enhanced.load(context, report=self.report, **keywords)

    def draw(self, context):
        pass


class BVH_ENHANCED_PT_import_main(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = ""
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_ANIM_OT_bvh_enhanced"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        obj = context.object
        if obj and obj.type == 'ARMATURE':
            operator.armature = obj.name

        layout.prop(operator, "target")

        if operator.target == "EXISTING_ARMATURE":
            layout.prop(operator, "armature")


class BVH_ENHANCED_PT_import_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        # print('--> in BVH_ENHANCED_PT_import_transform.poll()')
        # print(operator)
        # print(operator.bl_idname)

        return operator.bl_idname == "IMPORT_ANIM_OT_bvh_enhanced"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "global_scale")
        layout.prop(operator, "rotate_mode")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")
        layout.prop(operator, "translation_mode")
        layout.prop(operator, "apply_axis_conversion")


class BVH_ENHANCED_PT_import_animation(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Animation"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        # print('--> in BVH_ENHANCED_PT_import_animation.poll()')
        # print(operator)
        # print(operator.bl_idname)

        return operator.bl_idname == "IMPORT_ANIM_OT_bvh_enhanced"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "skip_frames")
        layout.prop(operator, "frame_start")

        if operator.target != "NEW_PARENTED_OBJECTS":
            layout.prop(operator, "use_fps_scale")

        layout.prop(operator, "use_cyclic")
        layout.prop(operator, "add_rest_pose_as_first_frame")

        layout.prop(operator, "update_scene_fps")
        layout.prop(operator, "update_scene_duration")


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportBVHEnhanced(bpy.types.Operator, ExportHelper):
    """Save a BVH motion capture file from an armature"""
    bl_idname = "export_anim.bvh_enhanced"
    bl_label = "Export BVH"

    filename_ext = ".bvh"
    filter_glob: StringProperty(
        default="*.bvh",
        options={'HIDDEN'},
    )
    # target: EnumProperty(
    #     items=(
    #         ('ARMATURE', "Armature", ""),
    #         ('OBJECT', "Object", ""),
    #     ),
    #     name="Target",
    #     description="Import target type",
    #     default='ARMATURE',
    # )
    global_scale: FloatProperty(
        name="Scale",
        description="Scale the BVH by this value",
        min=0.0001, max=1000000.0,
        soft_min=0.001, soft_max=100.0,
        default=1.0,
    )
    frame_start: IntProperty(
        name="Start Frame",
        description="Starting frame to export",
        default=0,
    )
    frame_end: IntProperty(
        name="End Frame",
        description="End frame to export",
        default=0,
    )
    rotate_mode: EnumProperty(
        name="Rotation",
        description="Rotation conversion",
        items=(
            ('NATIVE', "Euler (Native)",
             "Use the rotation order defined in the armature object"),
            ('XYZ', "Euler (XYZ)", "Convert rotations to euler XYZ"),
            ('XZY', "Euler (XZY)", "Convert rotations to euler XZY"),
            ('YXZ', "Euler (YXZ)", "Convert rotations to euler YXZ"),
            ('YZX', "Euler (YZX)", "Convert rotations to euler YZX"),
            ('ZXY', "Euler (ZXY)", "Convert rotations to euler ZXY"),
            ('ZYX', "Euler (ZYX)", "Convert rotations to euler ZYX"),
        ),
        default='NATIVE',
    )
    root_transform_only: BoolProperty(
        name="Root Translation Only",
        description="Only write out translation channels for the root bone",
        default=True,
    )
    add_rest_pose_as_first_frame: BoolProperty(
        name="Add Rest Pose",
        description="Add rest pose as the first frame",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE'

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        return super().invoke(context, event)

    def execute(self, context):
        if self.frame_start == 0 and self.frame_end == 0:
            self.frame_start = context.scene.frame_start
            self.frame_end = context.scene.frame_end

        keywords = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "check_existing",
                "filter_glob",
            )
        )

        # global_matrix: from current Blender coordinates system to output coordinates system 
        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4().inverted()

        keywords["global_matrix"] = global_matrix

        from . import export_bvh_enhanced
        return export_bvh_enhanced.save(context, **keywords)

    def draw(self, context):
        pass


class BVH_ENHANCED_PT_export_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_ANIM_OT_bvh_enhanced"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "global_scale")
        layout.prop(operator, "rotate_mode")
        layout.prop(operator, "root_transform_only")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")


class BVH_ENHANCED_PT_export_animation(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Animation"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_ANIM_OT_bvh_enhanced"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(align=True)
        col.prop(operator, "frame_start", text="Frame Start")
        col.prop(operator, "frame_end", text="End")
        
        layout.prop(operator, "add_rest_pose_as_first_frame")


def menu_func_import(self, context):
    self.layout.operator(ImportBVHEnhanced.bl_idname,
                         text="Motion Capture (.bvh), enhanced")

def menu_func_export(self, context):
    self.layout.operator(ExportBVHEnhanced.bl_idname, text="Motion Capture (.bvh), enhanced")


classes = (
    ImportBVHEnhanced,
    BVH_ENHANCED_PT_import_main,
    BVH_ENHANCED_PT_import_transform,
    BVH_ENHANCED_PT_import_animation,
    ExportBVHEnhanced,
    BVH_ENHANCED_PT_export_transform,
    BVH_ENHANCED_PT_export_animation,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
