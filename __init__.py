bl_info = {
    "name": "Create QRCode Mesh",
    "author": "TekKnowledge",
    "version": (1, 0),
    "blender": (3, 5, 0),
    "location": "View3D",
    "description": "Adds a new QRCode Mesh Object",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
from .meshqrcode import QRCodeOperator
from .meshqrcode import QRCodePanel
from .meshqrcode import *

CLASSES = [
    QRCodeOperator,
    QRCodePanel,
]


def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in CLASSES:
        bpy.utils.register_class(cls)

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

