bl_info = {
    "name": "Chladni Plate Generator",
    "author": "Jason Rodriguez <jasoncrodriguez@gmail.com>",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "category": "Mesh",
    "location": "Operator Search",
    "description": "Creates random chladni plates as a mesh",
    "warning": "",
    "doc_url": "",
    "tracking_url": "",
}

import bpy
import math
import random


class MESH_OT_chladni_plate(bpy.types.Operator):
    """Generate a random chladni plate"""
    bl_idname = "mesh.chladni_plate"
    bl_label = "Chladni Plate"
    bl_options = {'REGISTER', 'UNDO'}

    frequency_a: bpy.props.FloatProperty(
        name = "frequency_a",
        description = "Frequency of component A",
        default = random.uniform(1.5, 4.5),
        min = 0,
        soft_max = 5,
    )
    frequency_b: bpy.props.FloatProperty(
        name = "frequency_b",
        description = "Frequency of component B",
        default = random.uniform(1.5,4.5),
        min = 0,
        soft_max = 5,
    )
    amplitude_a: bpy.props.FloatProperty(
        name = "amplitude_a",
        description = "Amplitude of component A",
        default = 0.1,
        min = 0,
        soft_max = 3,
    )
    amplitude_b: bpy.props.FloatProperty(
        name = "amplitude_b",
        description = "Amplitude of component B",
        default = 0.1,
        min = 0,
        soft_max = 3,
    )
    
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.transform.resize(value=(1, 1, 1))
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subdivision"].subdivision_type = 'SIMPLE'
        bpy.context.object.modifiers["Subdivision"].levels = 6

        bpy.ops.object.modifier_apply(modifier="Subdivision")
      
        bpy.context.selected_objects[0].name = 'chladni_plate_{:.2f}_{:.2f}'.format(self.frequency_a, self.frequency_b)

        selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
        for v in selectedVerts:
            print(str(v) + " "  + str(v.co))

        for vert in selectedVerts:
            x, y, z = vert.co
            vert.co.z += self.amplitude_a * math.sin(self.frequency_a * x * math.pi) * math.sin(self.frequency_b * y * math.pi)\
                            + self.amplitude_b * math.sin(self.frequency_b * x * math.pi) * math.sin(self.frequency_a * y * math.pi)

        bpy.ops.object.shade_smooth()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_chladni_plate)

def unregister():
    bpy.utils.unregister_class(MESH_OT_chladni_plate)