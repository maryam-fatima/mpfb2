#!/usr/bin/python
# -*- coding: utf-8 -*-

from mpfb import CLASSMANAGER
from mpfb.services.logservice import LogService
from mpfb.services.uiservice import UiService
import bpy

_LOG = LogService.get_logger("ui.savenodespanel")

class MPFB_PT_Save_Nodes_Panel(bpy.types.Panel):
    bl_label = "Save nodes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = UiService.get_value("DEVELOPERCATEGORY")

    def draw(self, context):
        _LOG.enter()
        layout = self.layout
        scn = context.scene
        layout.operator("mpfb.save_nodes")

CLASSMANAGER.add_class(MPFB_PT_Save_Nodes_Panel)