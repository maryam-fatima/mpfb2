from mpfb.services.logservice import LogService
from .molecule import Molecule

import bpy

_LOG = LogService.get_logger("nodemodel.colorrouter5")
_GROUP_NAME = "MpfbColorRouter5"

class MpfbColorRouter5(Molecule):
    def __init__(self):
        _LOG.trace("Constructing Molecule for", _GROUP_NAME)
        Molecule.__init__(self, _GROUP_NAME)

    def create_group(self):
        _LOG.debug("Create group in " + _GROUP_NAME)

        nodes = dict()

        (nodes["Group Input"], nodes["Group Output"]) = self.create_input_and_output()
        nodes["Group Output"].location = [883.700927734375, -306.3296813964844]
        nodes["Group Input"].location = [-664.06982421875, -246.0766143798828]

        self.add_input_socket("Value", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold1", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold2", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold3", socket_type="NodeSocketFloat", default_value=0.500)
        self.add_input_socket("Threshold4", socket_type="NodeSocketFloat", default_value=0.800)
        self.add_input_socket("Section1Color", socket_type="NodeSocketColor", default_value=[1.0, 0.0, 0.0010608520824462175, 1.0])
        self.add_input_socket("Section2Color", socket_type="NodeSocketColor", default_value=[0.0, 1.0, 0.0012432460207492113, 1.0])
        self.add_input_socket("Section3Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0007007885142229497, 1.0, 1.0])
        self.add_input_socket("Section4Color", socket_type="NodeSocketColor", default_value=[0.5, 0.5, 0.5, 1.0])
        self.add_input_socket("Section5Color", socket_type="NodeSocketColor", default_value=[0.5, 0.5, 0.5, 1.0])

        self.add_output_socket("Color", socket_type="NodeSocketColor", default_value=[0.0, 0.0, 0.0, 0.0])

        nodes["Mix"] = self.createShaderNodeMixRGB(name="Mix", x=-175.986, y=62.706, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Math"] = self.createShaderNodeMath(name="Math", x=-371.966, y=119.555, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Math.001"] = self.createShaderNodeMath(name="Math.001", x=-171.558, y=-199.325, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix.001"] = self.createShaderNodeMixRGB(name="Mix.001", x=103.656, y=-19.317, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Math.002"] = self.createShaderNodeMath(name="Math.002", x=112.615, y=-358.588, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix.002"] = self.createShaderNodeMixRGB(name="Mix.002", x=331.398, y=-169.508, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)
        nodes["Math.003"] = self.createShaderNodeMath(name="Math.003", x=329.271, y=-568.252, Value=0.500, Value_001=0.500, Value_002=0.500, operation='GREATER_THAN', use_clamp=False)
        nodes["Mix.003"] = self.createShaderNodeMixRGB(name="Mix.003", x=570.224, y=-399.331, Fac=0.5, Color1=[0.5, 0.5, 0.5, 1.0], Color2=[0.5, 0.5, 0.5, 1.0], blend_type='MIX', use_alpha=False, use_clamp=False)

        self.add_link(nodes["Group Input"], "Value", nodes["Math"], "Value")
        self.add_link(nodes["Group Input"], "Threshold1", nodes["Math"], "Value_001")
        self.add_link(nodes["Math"], "Value", nodes["Mix"], "Fac")
        self.add_link(nodes["Group Input"], "Section1Color", nodes["Mix"], "Color1")
        self.add_link(nodes["Group Input"], "Section2Color", nodes["Mix"], "Color2")
        self.add_link(nodes["Mix"], "Color", nodes["Mix.001"], "Color1")
        self.add_link(nodes["Math.001"], "Value", nodes["Mix.001"], "Fac")
        self.add_link(nodes["Group Input"], "Section3Color", nodes["Mix.001"], "Color2")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.001"], "Value")
        self.add_link(nodes["Group Input"], "Threshold2", nodes["Math.001"], "Value_001")
        self.add_link(nodes["Mix.001"], "Color", nodes["Mix.002"], "Color1")
        self.add_link(nodes["Group Input"], "Section4Color", nodes["Mix.002"], "Color2")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.002"], "Value")
        self.add_link(nodes["Group Input"], "Threshold3", nodes["Math.002"], "Value_001")
        self.add_link(nodes["Math.002"], "Value", nodes["Mix.002"], "Fac")
        self.add_link(nodes["Mix.002"], "Color", nodes["Mix.003"], "Color1")
        self.add_link(nodes["Math.003"], "Value", nodes["Mix.003"], "Fac")
        self.add_link(nodes["Group Input"], "Value", nodes["Math.003"], "Value")
        self.add_link(nodes["Group Input"], "Threshold4", nodes["Math.003"], "Value_001")
        self.add_link(nodes["Group Input"], "Section5Color", nodes["Mix.003"], "Color2")
        self.add_link(nodes["Mix.003"], "Color", nodes["Group Output"], "Color")



# --- paste this in the MoleculeNodeManager class def
#
#     def createMpfbColorRouter5(self, x=0.0, y=0.0, name=None, label=None, Value=None, Threshold1=None, Threshold2=None, Threshold3=None, Threshold4=None, Section1Color=None, Section2Color=None, Section3Color=None, Section4Color=None, Section5Color=None):
#         return self._molecule_singletons["MpfbColorRouter5"].create_instance(self.node_tree, x=x, y=y, name=name, label=label, Value=Value, Threshold1=Threshold1, Threshold2=Threshold2, Threshold3=Threshold3, Threshold4=Threshold4, Section1Color=Section1Color, Section2Color=Section2Color, Section3Color=Section3Color, Section4Color=Section4Color, Section5Color=Section5Color)