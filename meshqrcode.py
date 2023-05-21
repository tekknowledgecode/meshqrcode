import qrcode
import bpy
import bmesh
from bpy.types import Panel
from bpy.types import Operator
from bpy_extras import object_utils
import numpy as np


PROPS = [
   ('qrcodeName', bpy.props.StringProperty(name='QRCode Name', default='qrcode')),
   ('qrcodeText', bpy.props.StringProperty(name='QRCode Text', default='My QRCode')),
   ('qrcodeInvert', bpy.props.BoolProperty(name='Invert Solid Area', default=False)),
   ('qrcodeScale', bpy.props.FloatProperty(name='QRCode Scale', default=.1)),
   ('qrcodeSolidify', bpy.props.FloatProperty(name='QRCode Solidify', default=0.0)),
   ('qrcodeZScale', bpy.props.IntProperty(name='QRCode Z-Scale', default=10)),
]

class QRCodeOperator(Operator):
    bl_idname = "opr.create_qrcode"
    bl_label = "Create QRCode Mesh"
    bl_options = {'REGISTER', 'UNDO'}
     
    def execute(self, context):
        params = (
            context.scene.qrcodeName,
            context.scene.qrcodeText,
            context.scene.qrcodeInvert,
            context.scene.qrcodeScale,
            context.scene.qrcodeSolidify,
            context.scene.qrcodeZScale,
        )

        self.makeQRCode(params)
        return {'FINISHED'}


    def makeQRCode(self, params):
        (qrcN, qrcT, qrcI, qrcS, qrcSolid, qrcZScale) = params
        qr = qrcode.QRCode(version=None,
                    box_size=10,
                    border=5)

        qr.add_data(qrcT)

        qr.make(fit=True)

        modules = qr.get_matrix()
        size = len(modules)

        bm = bmesh.new()
        x_scale = qrcS
        y_scale = qrcS
        qrc_type = "c"
        new_bm = bmesh.new()
        ztype = bpy.context.scene.qrcode_ztype
        if ztype == "1":
            zt = calculate_pyramid_z(size, size)
        if ztype == "2":
            zt = calculate_spiral_z(size, size)

        for y in range(size):
            for x in range(size):
                if modules[y][x] ^ qrcI:
                    if ztype == "0":
                        z = 0
                    else: 
                        z = zt[x,y] * qrcZScale
                    if bpy.context.scene.qrcode_type == "0":
                        verts = [
                        bm.verts.new((x_scale * x,     y_scale * y,     z*qrcS)),
                        bm.verts.new((x_scale * x,     y_scale * (y+1), z*qrcS)),
                        bm.verts.new((x_scale * (x+1), y_scale * (y+1), z*qrcS)),
                        bm.verts.new((x_scale * (x+1), y_scale * y,     z*qrcS))
                        ]
                        bm.faces.new(verts)
                    if  bpy.context.scene.qrcode_type == "1":
                        wrk_bm = bmesh.new()
                        bmesh.ops.create_circle(wrk_bm, radius=(qrcS/2), segments=16)

                        for v in wrk_bm.verts:
                            v.co.x = v.co.x + (x_scale * x)
                            v.co.y = v.co.y + (y_scale * y)
                            v.co.z = z*qrcS
                        bm = join_bmesh(bm, wrk_bm)
                        wrk_bm.free()
        
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        mesh = bpy.data.meshes.new("qrcode")
        bm.to_mesh(mesh)
        bm.free()

        obj = bpy.data.objects.new(qrcN, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        
        if qrcSolid > 0:
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].thickness = qrcSolid
            bpy.ops.object.modifier_apply(modifier="Solidify")
   
        bpy.context.active_object.select_set(True)
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        return {'FINISHED'}


class QRCodePanel(bpy.types.Panel):

    bl_idname = 'VIEW3D_PT_QRCode_panel'
    bl_label = 'Create QRCode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "QRCodes"
    enum_stype = (('0','Square',''),('1','Circle',''))
    bpy.types.Scene.qrcode_type = bpy.props.EnumProperty(items = enum_stype)
    
    enum_ztype = (('0','None',''),('1','Pyramid',''),('2','Swirl',''))
    bpy.types.Scene.qrcode_ztype = bpy.props.EnumProperty(items = enum_ztype)


    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
        row = col.row()
        row.label(text="Select QRCode Shape Type")
        row.prop(context.scene, 'qrcode_type', text='QRCode Shape', expand=True)
 
        row = col.row()
        row.label(text="Select QRCode Z-Axis Type")
        row.prop(context.scene, 'qrcode_ztype', text='QRCode Z-Axis Shape', expand=True)
       
        row = col.row()
        row.operator('opr.create_qrcode', text='Create')


#CLASSES = [
#   QRCodeOperator,
#   QRCodePanel,
#]

### Used to Join circles into one bmesh when user selects Circle for QRCode Shape.
def join_bmesh(target_bm, source_bm):

    source_bm.verts.layers.int.new('index')
    idx_layer = source_bm.verts.layers.int['index']

    new_verts = []
    for old_vert in source_bm.verts:
        if not old_vert.tag:
            new_vert = target_bm.verts.new(old_vert.co)
            target_bm.verts.index_update()
            old_vert[idx_layer] = new_vert.index
            old_vert.tag = True

        target_bm.verts.ensure_lookup_table()
        idx = old_vert[idx_layer]
        new_verts.append(target_bm.verts[idx])

    target_bm.faces.new(new_verts)
    return target_bm

def calculate_pyramid_z(x, y):
    # Create a square grid of coordinates
    X, Y = np.meshgrid(np.arange(x), np.arange(y))

    # Calculate the distance from the center of the grid
    center_x = (x - 1) / 2
    center_y = (y - 1) / 2
    distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)

    # Create the pyramid shape by assigning z-values based on the distance from the center
    z = np.where(distance <= center_x, (center_x - distance) / center_x, 0)

    return z

def calculate_spiral_z(x, y):
    # Create a square grid of coordinates
    X, Y = np.meshgrid(np.arange(x), np.arange(y))

    # Calculate the distance from each point to the bottom right corner
    distance = np.sqrt((X - (x-1))**2 + (Y - (y-1))**2)

    # Calculate the angle theta based on the distance
    theta = 2 * np.pi * distance / np.max(distance)

    # Calculate the z-values for the spiral shape
    z = theta / (2 * np.pi)

    return z

