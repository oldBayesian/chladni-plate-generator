bl_info = {
    "name": "Chladni Plate Generator",
    "author": "Jason Rodriguez <jasoncrodriguez@gmail.com>",
    "version": (1, 1),
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
from mathutils import noise, Vector


class MESH_OT_chladni_plate(bpy.types.Operator):
    """Generate a random chladni plate"""
    bl_idname = "mesh.chladni_plate"
    bl_label = "Chladni Plate"
    bl_options = {'REGISTER', 'UNDO'}

    subdivisions_x: bpy.props.IntProperty(
        name="Subdivisions X",
        description="Subdivision in the X axis",
        default=20,
        min=10,
        soft_max=40,
    )
    subdivisions_y: bpy.props.IntProperty(
        name="Subdivisions Y",
        description="Subdivision in the Y axis",
        default=20,
        min=10,
        soft_max=40,
    )
    size: bpy.props.FloatProperty(
        name="Size",
        description="Size of mesh",
        default=1,
        min=0,
        soft_max=10,
    )
    length: bpy.props.FloatProperty(
        name="Length",
        description="Scale in Y of mesh",
        default=1,
        min=0,
        soft_max=10,
    )
    apply: bpy.props.BoolProperty(
        name="Apply Scaling",
        description="Apply scaling after creation",
        default=True,
    )
    frequency_a: bpy.props.FloatProperty(
        name="Frequency A",
        description="Frequency of component A",
        default=random.uniform(1.5, 4.5),
        min=0,
        soft_max=5,
    )
    frequency_b: bpy.props.FloatProperty(
        name="Frequency B",
        description="Frequency of component B",
        default=random.uniform(1.5, 4.5),
        min=0,
        soft_max=5,
    )
    amplitude_a: bpy.props.FloatProperty(
        name="Amplitude A",
        description="Amplitude of component A",
        default=0.1,
        min=0,
        soft_max=3,
    )
    amplitude_b: bpy.props.FloatProperty(
        name="Amplitude B",
        description="Amplitude of component B",
        default=0.1,
        min=0,
        soft_max=3,
    )
    anisotropy_x: bpy.props.FloatProperty(
        name="Anisotropy X",
        description="Stretch factor along X in the function space",
        default=1.0,
        min=0.1,
        soft_max=3.0,
    )
    anisotropy_y: bpy.props.FloatProperty(
        name="Anisotropy Y",
        description="Stretch factor along Y in the function space",
        default=1.0,
        min=0.1,
        soft_max=3.0,
    )
    frequency_variation: bpy.props.FloatProperty(
        name="Frequency Variation",
        description="How much the frequency varies across the plate",
        default=0.3,
        min=0.0,
        soft_max=2.0,
    )
    swirl_strength: bpy.props.FloatProperty(
        name="Swirl Strength",
        description="Amount of swirl distortion applied to the pattern",
        default=0.0,
        min=-5.0,
        max=5.0,
        soft_max=10.0,
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):

        if not context.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=self.subdivisions_x,
            y_subdivisions=self.subdivisions_y,
            size=self.size,
            enter_editmode=False,
            align='WORLD',
            location=(0, 0, 0),
            scale=(1, 1, 1)
        )

        bpy.context.object.scale[0] = self.length

        if self.apply:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        obj = bpy.context.active_object
        obj.name = f"chladni_plate_{self.frequency_a:.2f}_{self.frequency_b:.2f}"

        # Operate on all vertices
        verts = obj.data.vertices

        for vert in verts:
            x, y, z = vert.co

            # --- Swirl distortion ---
            r = math.sqrt(x * x + y * y)
            theta = math.atan2(y, x)
            # Smooth falloff: more swirl outward
            theta_swirl = theta + self.swirl_strength * (r ** 2)
            xw = r * math.cos(theta_swirl)
            yw = r * math.sin(theta_swirl)

            # --- Smooth frequency variation ---
            fx = self.frequency_a + self.frequency_variation * noise.noise(Vector((xw * 0.5, yw * 0.5, 0)))
            fy = self.frequency_b + self.frequency_variation * noise.noise(Vector((xw * 0.5 + 10.0, yw * 0.5 + 10.0, 0)))

            # --- Apply anisotropy and Chladni pattern ---
            vert.co.z += (
                self.amplitude_a * math.sin(fx * xw * self.anisotropy_x * math.pi) * math.sin(fy * yw * self.anisotropy_y * math.pi)
                + self.amplitude_b * math.sin(fy * xw * self.anisotropy_x * math.pi) * math.sin(fx * yw * self.anisotropy_y * math.pi)
            )

        bpy.ops.object.shade_smooth()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_chladni_plate)


def unregister():
    bpy.utils.unregister_class(MESH_OT_chladni_plate)