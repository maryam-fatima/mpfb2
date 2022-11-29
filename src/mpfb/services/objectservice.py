
import bpy, os, json, random, gzip, typing
from mpfb.services.logservice import LogService
from mpfb.services.locationservice import LocationService
from mpfb.entities.objectproperties import GeneralObjectProperties
from mpfb.entities.socketobject import BASEMESH_EXTRA_GROUPS

_LOG = LogService.get_logger("services.objectservice")

_BASEMESH_VERTEX_GROUPS_UNEXPANDED = None
_BASEMESH_VERTEX_GROUPS_EXPANDED = None

_BASEMESH_FACE_TO_VERTEX_TABLE = None
_BASEMESH_VERTEX_TO_FACE_TABLE = None

_BODY_PART_TYPES = ("Eyes", "Eyelashes", "Eyebrows", "Tongue", "Teeth", "Hair")
_MESH_ASSET_TYPES = ("Proxymeshes", "Clothes") + _BODY_PART_TYPES
_MESH_TYPES = ("Basemesh",) + _MESH_ASSET_TYPES
_ARMATURE_TYPES = ("Skeleton",)
_ALL_TYPES = _ARMATURE_TYPES + _MESH_TYPES

class ObjectService:

    def __init__(self):
        raise RuntimeError("You should not instance ObjectService. Use its static methods instead.")

    @staticmethod
    def object_name_exists(name):
        return name in bpy.data.objects

    @staticmethod
    def ensure_unique_name(desired_name):
        if not ObjectService.object_name_exists(desired_name):
            return desired_name
        for i in range(1, 100):
            ranged_name = desired_name + "." + str(i).zfill(3)
            if not ObjectService.object_name_exists(ranged_name):
                return ranged_name
        return desired_name + ".999"

    @staticmethod
    def deselect_and_deactivate_all():
        if bpy.context.object:
            try:
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.context.object.select_set(False)
            except:
                _LOG.debug("Tried mode_set / unselect on non-existing object")
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(False)
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None

    @staticmethod
    def has_vertex_group(blender_object, vertex_group_name):
        if not blender_object or not vertex_group_name:
            return False
        for group in blender_object.vertex_groups:
            if group.name == vertex_group_name:
                return True
        return False

    @staticmethod
    def get_vertex_indexes_for_vertex_group(blender_object, vertex_group_name):
        if not blender_object or not vertex_group_name:
            return []
        group_index = None
        for group in blender_object.vertex_groups:
            if group.name == vertex_group_name:
                group_index = group.index
        if group_index is None:
            return []
        relevant_vertices = []
        for vertex in blender_object.data.vertices:
            for group in vertex.groups:
                if group.group == group_index:
                    if not vertex.index in relevant_vertices:
                        relevant_vertices.append(vertex.index)
        return relevant_vertices

    @staticmethod
    def create_blender_object_with_mesh(name="NewObject"):
        mesh = bpy.data.meshes.new(name + "Mesh")
        obj = bpy.data.objects.new(name, mesh)
        return obj

    @staticmethod
    def create_empty(name, empty_type="SPHERE", parent=None):
        empty = bpy.data.objects.new(name=name, object_data=None)
        ObjectService.link_blender_object(empty, parent=parent)
        empty.empty_display_type = empty_type
        return empty

    @staticmethod
    def link_blender_object(object_to_link, collection=None, parent=None):
        if collection is None:
            collection = bpy.context.collection
        collection.objects.link(object_to_link)
        _LOG.debug("object_to_link", object_to_link)
        _LOG.debug("parent", parent)
        if parent:
            object_to_link.parent = parent

    @staticmethod
    def activate_blender_object(object_to_make_active):
        bpy.context.view_layer.objects.active = object_to_make_active

    @staticmethod
    def get_list_of_children(parent_object):
        children = []
        for potential_child in bpy.data.objects:
            if potential_child.parent == parent_object:
                children.append(potential_child)
        return children

    @staticmethod
    def get_object_type(blender_object) -> str:
        if not blender_object:
            return ""

        object_type = GeneralObjectProperties.get_value("object_type", entity_reference=blender_object)

        return str(object_type or "").strip()

    @staticmethod
    def object_is(blender_object, mpfb_type_name: str | typing.Sequence[str]):
        """
        Check if the given object is of the correct type(s).

        Args:
            blender_object: Object to test
            mpfb_type_name: Type name, or list/tuple of acceptable type names.
        """

        if not mpfb_type_name:
            return False

        mpfb_type = ObjectService.get_object_type(blender_object)

        if not mpfb_type:
            return False

        mpfb_type = mpfb_type.lower()

        if isinstance(mpfb_type_name, str):
            mpfb_type_name = [mpfb_type_name]

        for item in mpfb_type_name:
            stripped = str(item).lower().strip()
            if stripped and stripped in mpfb_type:
                return True

        if mpfb_type_name is _ALL_TYPES:
            # This is supposed to handle all possible types.
            _LOG.debug("Unexpected object type: " + mpfb_type)

        return False

    @staticmethod
    def object_is_basemesh(blender_object):
        return ObjectService.object_is(blender_object, "Basemesh")

    @staticmethod
    def object_is_skeleton(blender_object):
        return ObjectService.object_is(blender_object, "Skeleton")

    @staticmethod
    def object_is_body_proxy(blender_object):
        return ObjectService.object_is(blender_object, "Proxymesh")

    @staticmethod
    def object_is_eyes(blender_object):
        return ObjectService.object_is(blender_object, "Eyes")

    @staticmethod
    def object_is_basemesh_or_body_proxy(blender_object):
        return ObjectService.object_is(blender_object, "Basemesh") or ObjectService.object_is(blender_object, "Proxymesh")

    @staticmethod
    def object_is_any_mesh(blender_object):
        return blender_object and blender_object.type == "MESH"

    @staticmethod
    def object_is_any_makehuman_mesh(blender_object):
        return blender_object and blender_object.type == "MESH" and ObjectService.get_object_type(blender_object)

    @staticmethod
    def object_is_any_mesh_asset(blender_object):
        return blender_object and blender_object.type == "MESH" and\
            ObjectService.object_is(blender_object, _MESH_ASSET_TYPES)

    @staticmethod
    def object_is_any_makehuman_object(blender_object):
        return blender_object and ObjectService.get_object_type(blender_object)

    @staticmethod
    def find_object_of_type_amongst_nearest_relatives(
            blender_object: bpy.types.Object,
            mpfb_type_name: str | typing.Sequence[str] = "Basemesh", *,
            only_parents=False, strict_parent=False, only_children=False,
            ) -> typing.Optional[bpy.types.Object]:
        """
        Find one object of the given type(s) among the children, parents and siblings of the object.
        """
        relatives = ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, mpfb_type_name,
            only_parents=only_parents, strict_parent=strict_parent, only_children=only_children)

        return next(relatives, None)

    @staticmethod
    def find_all_objects_of_type_amongst_nearest_relatives(
            blender_object: bpy.types.Object,
            mpfb_type_name: str | typing.Sequence[str] = "Basemesh", *,
            only_parents=False, strict_parent=False, only_children=False,
            ) -> typing.Generator[bpy.types.Object, None, None]:
        """
        Find all objects of the given type(s) among the children, parents and siblings of the object.

        Args:
            blender_object: Object to start search from.
            mpfb_type_name: String or sequence of strings denoting valid types.
            only_parents: Only search among the object and its parents.
            strict_parent: Don't search immediate siblings if the parent isn't a MakeHuman object.
            only_children: Only search among the object and its children.
        """

        if not blender_object or not mpfb_type_name:
            return

        def rec_children(rec_parent, exclude=None):
            if only_parents:
                return

            for parents_child in ObjectService.get_list_of_children(rec_parent):
                if parents_child == exclude:
                    continue

                if ObjectService.object_is(parents_child, mpfb_type_name):
                    yield parents_child
                elif parents_child.type == "ARMATURE":
                    yield from rec_children(parents_child)

        if ObjectService.object_is(blender_object, mpfb_type_name):
            yield blender_object

        yield from rec_children(blender_object)

        if only_children:
            return

        parent_from = blender_object
        parent = blender_object.parent

        while parent:
            if strict_parent:
                if parent.type != 'ARMATURE' and not ObjectService.object_is_any_makehuman_object(parent):
                    break

            if ObjectService.object_is(parent, mpfb_type_name):
                yield parent

            yield from rec_children(parent, parent_from)

            parent_from = parent
            parent = parent.parent
            strict_parent = True

    @staticmethod
    def find_related_objects(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _ALL_TYPES, **kwargs)

    @staticmethod
    def find_related_mesh_base_or_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _MESH_TYPES, **kwargs)

    @staticmethod
    def find_related_mesh_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _MESH_ASSET_TYPES, **kwargs)

    @staticmethod
    def find_related_body_part_assets(blender_object, **kwargs):
        yield from ObjectService.find_all_objects_of_type_amongst_nearest_relatives(
            blender_object, _BODY_PART_TYPES, **kwargs)

    @staticmethod
    def load_wavefront_file(filepath, context=None):
        if context is None:
            context = bpy.context
        if filepath is None:
            raise ValueError('Cannot load None filepath')
        if not os.path.exists(filepath):
            raise IOError('File does not exist: ' + filepath)
        bpy.ops.import_scene.obj(filepath=filepath, use_split_objects=False, use_split_groups=False)

        # import_scene rotated object 90 degrees
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        loaded_object = bpy.context.selected_objects[0] # pylint: disable=E1136
        return loaded_object

    @staticmethod
    def load_base_mesh(context=None, scale_factor=1.0, load_vertex_groups=True, exclude_vertex_groups=None):
        objsdir = LocationService.get_mpfb_data("3dobjs")
        filepath = os.path.join(objsdir, "base.obj")
        basemesh = ObjectService.load_wavefront_file(filepath, context)
        basemesh.name = "Human"
        bpy.ops.object.shade_smooth()
        bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
        bpy.ops.object.transform_apply(scale=True)
        GeneralObjectProperties.set_value("object_type", "Basemesh", entity_reference=basemesh)
        GeneralObjectProperties.set_value("scale_factor", scale_factor, entity_reference=basemesh)
        if load_vertex_groups:
            groups = ObjectService.get_base_mesh_vertex_group_definition()
            ObjectService.assign_vertex_groups(basemesh, groups, exclude_vertex_groups)
        return basemesh

    @staticmethod
    def assign_vertex_groups(blender_object, vertex_group_definition, exclude_groups=None):
        if exclude_groups is None:
            exclude_groups = []
        for group_name in vertex_group_definition.keys():
            if group_name not in exclude_groups:
                vertex_group = blender_object.vertex_groups.new(name=group_name)
                vertex_group.add(vertex_group_definition[group_name], 1.0, 'ADD')

    @staticmethod
    def get_base_mesh_vertex_group_definition():
        global _BASEMESH_VERTEX_GROUPS_EXPANDED # pylint: disable=W0603
        global _BASEMESH_VERTEX_GROUPS_UNEXPANDED # pylint: disable=W0603
        if _BASEMESH_VERTEX_GROUPS_EXPANDED is None:
            meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
            definition_file = os.path.join(meta_data_dir, "basemesh_vertex_groups.json")
            with open(definition_file, "r") as json_file:
                _BASEMESH_VERTEX_GROUPS_UNEXPANDED = json.load(json_file)
            _BASEMESH_VERTEX_GROUPS_EXPANDED = dict()
            for group in _BASEMESH_VERTEX_GROUPS_UNEXPANDED.keys():
                group_name = str(group)
                _BASEMESH_VERTEX_GROUPS_EXPANDED[group_name] = []
                for start_stop in _BASEMESH_VERTEX_GROUPS_UNEXPANDED[group]:
                    _BASEMESH_VERTEX_GROUPS_EXPANDED[group_name].extend(range(start_stop[0], start_stop[1]+1))
            _BASEMESH_VERTEX_GROUPS_EXPANDED.update(BASEMESH_EXTRA_GROUPS)
        # Return a copy so it doesn't get accidentally modified
        return dict(_BASEMESH_VERTEX_GROUPS_EXPANDED)

    @staticmethod
    def get_lowest_point(basemesh, take_shape_keys_into_account=True):
        lowest_point = 1000.0
        vertex_data = basemesh.data.vertices
        shape_key = None
        key_name = None
        if take_shape_keys_into_account and basemesh.data.shape_keys and basemesh.data.shape_keys.key_blocks and len(basemesh.data.shape_keys.key_blocks) > 0:
            from .targetservice import TargetService
            key_name = "temporary_lowest_point_key." + str(random.randrange(1000, 9999))
            shape_key = TargetService.create_shape_key(basemesh, key_name, also_create_basis=True, create_from_mix=True)
            vertex_data = shape_key.data

        index = 0
        for vertex in vertex_data:
            if vertex.co[2] < lowest_point and index < 13380:
                lowest_point = vertex.co[2]
            index = index + 1

        if shape_key:
            basemesh.shape_key_remove(shape_key)

        return lowest_point

    @staticmethod
    def get_face_to_vertex_table():
        global _BASEMESH_FACE_TO_VERTEX_TABLE # pylint: disable=W0603

        meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
        definition_file = os.path.join(meta_data_dir, "basemesh_face_to_vertex_table.json.gz")

        if _BASEMESH_FACE_TO_VERTEX_TABLE is None:
            with gzip.open(definition_file, "rb") as json_file:
                _BASEMESH_FACE_TO_VERTEX_TABLE = json.load(json_file)

        return _BASEMESH_FACE_TO_VERTEX_TABLE

    @staticmethod
    def get_vertex_to_face_table():
        global _BASEMESH_VERTEX_TO_FACE_TABLE # pylint: disable=W0603

        meta_data_dir = LocationService.get_mpfb_data("mesh_metadata")
        definition_file = os.path.join(meta_data_dir, "basemesh_vertex_to_face_table.json.gz")

        if _BASEMESH_VERTEX_TO_FACE_TABLE is None:
            with gzip.open(definition_file, "rb") as json_file:
                _BASEMESH_VERTEX_TO_FACE_TABLE = json.load(json_file)

        return _BASEMESH_VERTEX_TO_FACE_TABLE

    @staticmethod
    def extract_vertex_group_to_new_object(existing_object, vertex_group_name):

        clothes_obj = existing_object.copy()
        clothes_obj.data = clothes_obj.data.copy()
        clothes_obj.parent = None
        clothes_obj.animation_data_clear()
        clothes_obj.name = "clothes"
        bpy.context.collection.objects.link(clothes_obj)

        for modifier in clothes_obj.modifiers:
            clothes_obj.modifiers.remove(modifier)

        for vgroup in clothes_obj.vertex_groups:
            if vertex_group_name != vgroup.name:
                clothes_obj.vertex_groups.remove(vgroup)

        existing_object.select_set(False)
        clothes_obj.select_set(True)
        bpy.context.view_layer.objects.active = clothes_obj

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        from mpfb.services.materialservice import MaterialService
        MaterialService.delete_all_materials(clothes_obj)

        GeneralObjectProperties.set_value("asset_source", "", entity_reference=clothes_obj)
        GeneralObjectProperties.set_value("object_type", "Clothes", entity_reference=clothes_obj)

        key_name = "temporary_fitting_key." + str(random.randrange(1000, 9999))
        clothes_obj.shape_key_add(name=key_name, from_mix=True)
        print(len(clothes_obj.data.shape_keys.key_blocks))

        for name in clothes_obj.data.shape_keys.key_blocks.keys():
            if name != key_name and name != "Basis":
                shape_key = clothes_obj.data.shape_keys.key_blocks[name]
                clothes_obj.shape_key_remove(shape_key)

        if "Basis" in clothes_obj.data.shape_keys.key_blocks.keys():
            shape_key = clothes_obj.data.shape_keys.key_blocks["Basis"]
            clothes_obj.shape_key_remove(shape_key)

        shape_key = clothes_obj.data.shape_keys.key_blocks[key_name]
        clothes_obj.shape_key_remove(shape_key)
