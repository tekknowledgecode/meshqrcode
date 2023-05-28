'''
Copyright (C) 2023 Tekknowledge.Net
http://www.tekknowledge.net
gjohnson@tekknowledge.net

Created by Greg Johnson

This file is part of Mesh QRCode.

    MeshQRCode is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org
/licenses>.
'''
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

