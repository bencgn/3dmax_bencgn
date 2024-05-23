# BEGIN LICENSE & COPYRIGHT BLOCK.
#
# Copyright (C) 2022-2024 Kiril Strezikozin
# BakeMaster Blender Add-on (version 2_6_0)
#
# This file is a part of BakeMaster Blender Add-on, a plugin for texture
# baking in open-source Blender 3d modelling software.
# The author can be contacted at <kirilstrezikozin@gmail.com>.
#
# Redistribution and use for any purpose including personal, educational, and
# commercial, with or without modification, are permitted provided
# that the following conditions are met:
#
# 1. The current acquired License allows copies/redistributions of this
#    software be made to 1 END USER SEAT (SOLO LICENSE).
# 2. Redistributions of this source code or partial usage of this source code
#    must follow the terms of this license and retain the above copyright
#    notice, and the following disclaimer.
# 3. The name of the author may be used to endorse or promote products derived
#    from this software. In such a case, a prior written permission from the
#    author is required.
#
# This program is free software and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# You should have received a copy of the GNU General Public License in the
# GNU.txt file along with this program. If not,
# see <http://www.gnu.org/licenses/>.
#
# END LICENSE & COPYRIGHT BLOCK.

import bpy
import os
import time
import math
import traceback
import colorsys
import tempfile
import re

from .decal import BM_LOT_DECAL_View

from .labels import BM_Labels
from .utils import *


class BM_OT_ITEM_Bake(bpy.types.Operator):
    bl_idname = 'bakemaster.item_bake'
    bl_label = "BakeMaster Bake Operator"
    bl_description = BM_Labels.OPERATOR_ITEM_BAKE_DESCRIPTION
    bl_options = {'UNDO'}

    wait_delay = 0.1  # Time Step interval in seconds between timer events
    report_delay = 1.0  # delay between each status report, seconds
    _version_current = bpy.app.version  # Blender version for compatibility checks
    _handler = None
    _timer = None

    # render_op_type = 'INVOKE_DEFAULT'
    render_op_type = 'EXEC_DEFAULT'

    control: bpy.props.EnumProperty(
        items=[('BAKE_ALL', "Bake All", "Bake maps for all objects added"),
               ('BAKE_THIS', "Bake This", "Bake maps only for the current object or container")])

    @classmethod
    def is_running(cls):
        return cls._handler is not None

    def report_msg(self, type: str, msg: str, infobar=True):
        print(f"BakeMaster {type.capitalize()}: {msg}")
        if not infobar:
            return

        if type not in {'INFO', 'WARNING', 'ERROR'}:
            type = 'INFO'
        self.report({type}, msg)
        self.last_report_time = time.time()

    def bake_poll(self, context):
        # abort if instance is running
        cls = self.__class__
        if cls._handler is not None:
            return "Another BakeMaster Bake is running"

        scene = context.scene
        if scene.render.engine != 'CYCLES':
            return BM_Labels.ERROR_BAKE_NOTINCYLES

        if len(scene.bm_table_of_objects) == 0:
            return BM_Labels.ERROR_BAKE_ITEMQUEUEEMPTY

        if self.control == 'BAKE_THIS':
            try:
                scene.bm_table_of_objects[scene.bm_props.global_active_index]
            except IndexError:
                return "Cannot resolve current Object, make sure the proper one is selected"
            else:
                object_full = BM_Object_Get(None, context)
                object = object_full[0]
                if object.nm_is_local_container:
                    return "Cannot bake Lowpoly/Highpoly/Cage Containers"
                if object_full[1] is False and object.nm_is_universal_container is False:
                    return "Object not found in the Scene"
                if object.hl_is_highpoly:
                    return "Cannot bake Highpoly, please select Lowpoly instead"
                if object.hl_is_cage:
                    return "Cannot bake Cage, please select Lowpoly instead"
                if object.global_use_bake is False:
                    return "Object is not enabled for baking"

        len_of_objects = 0
        len_of_maps = 0
        for object in scene.bm_table_of_objects:
            if self.object_get(context, object.global_object_name) is None:
                if any([object.nm_is_universal_container, object.nm_is_local_container]):
                    len_of_maps += len(
                        list(filter(lambda map: map.global_use_bake, object.global_maps)))
            else:
                len_of_objects += 1
                len_of_maps += len(
                    list(filter(lambda map: map.global_use_bake, object.global_maps)))

        if len_of_objects == 0:
            return BM_Labels.ERROR_BAKE_ITEMQUEUEEMPTY

        if len_of_maps == 0:
            return BM_Labels.ERROR_BAKE_MAPQUEUEEMPTY

        return None

    def get_time_diff(self, map=False) -> str:
        # returns how much time the whole bake or map bake took

        if map:
            start_time = self.last_map_start_time
        else:
            start_time = self.start_time

        timediff = round(time.time() - start_time)

        days = int(timediff / 86400)
        timediff -= (days * 86400)

        hours = int(timediff / 3600)
        timediff -= (hours * 3600)

        minutes = int(timediff / 60)
        timediff -= (minutes * 60)

        seconds = timediff

        res_time = ""

        if days > 0:
            res_time += "%dd " % days

        if hours > 0:
            res_time += "%dh " % hours

        if minutes > 0:
            res_time += "%dm " % minutes

        if seconds > 0:
            res_time += "%ds" % seconds

        if not res_time:
            res_time = "0s"

        return res_time

    def report_bake_progress(self):
        try:
            item_name = self.bake_current_source_object.name

            map_index = 0
            maps_length = 0
            for map in self.bake_current_container.global_maps:
                if not map.global_use_bake:
                    continue

                maps_length += 1
                if map.global_map_index <= self.bake_object_map_index:
                    map_index += 1

            if maps_length > 0:
                map_index += 1

            map_name = getattr(
                self.bake_current_map,
                "map_%s_prefix" % self.bake_current_map.global_map_type)

            time_elapsed = self.get_time_diff(map=True)

            msg = (f"Baking {item_name}: {map_name}, map {map_index} of "
                   + f"{maps_length}. Time elapsed: {time_elapsed}")
            self.report_msg('PROGRESS', msg)

        except (IndexError, AttributeError, KeyError, UnboundLocalError):
            pass

    def exit_common(self, context):
        try:
            if not self.bake_cancel:
                self.bake_process_exit_handle_channel_pack(context)
                self.bake_process_exit_pack_images()
            self.bake_process_exit_remove_unused_images()

            bake_time = self.get_time_diff()
            msg = f"BakeMaster Info: Bake completed in {bake_time}"
            self.report_msg('INFO', msg)

            # unhide hidden in the scene
            self.bake_scene_objects_hide(context, 'UNHIDE')
            self.bake_scene_objects_hide(context, 'CUSTOM_UNHIDE')

        except Exception as error:
            msg = (f"Code Execution Error: {error}.\nPlease, contact support: "
                   + "click 'Support' in the Help panel (below Bake buttons).")
            self.report_msg('ERROR', msg)

            print(("\nBakeMaster Code Error Traceback:\n "
                   + "%s\n\n" % traceback.format_exc()))

        finally:
            # restore scene settings
            self.bake_scene_settings(context, 'RESTORE')
            self.bake_scene_output_settings(context, 'RESTORE')
            # unblock bake_ot call in the ui
            # context.scene.bm_props.global_bake_available = True

        # remove handler and timer
        cls = self.__class__
        wm = context.window_manager
        if cls._timer is not None:
            wm.event_timer_remove(cls._timer)
        cls._timer = None
        cls._handler = None

    def bake_process_exit_pack_images(self):
        for key in self.bake_images_ad_data:
            try:
                image = bpy.data.images[key]
            except KeyError:
                continue

            if not self.bake_images_ad_data[key][8]:
                continue

            # pack into blend file - internal save

            if image.source == 'TILED' and self._version_current < (3, 3, 0):
                msg = (f"Cannot pack tiled image {image.name} into blend file."
                       + " Don't forget to save the image")
                self.report_msg('WARNING', msg)
                continue

            temp_filepath = bpy.path.abspath(image.filepath)
            image_colorspace = image.colorspace_settings.name

            try:
                image.pack()
            except RuntimeError as error:
                msg = (f"Cannot pack tiled image {image.name} into blend file"
                       + f" due to {error}. Don't forget to save the image")
                self.report_msg('WARNING', msg)
                continue
            else:
                image.filepath_raw = image.name

            try:
                image.colorspace_settings.name = image_colorspace
            except TypeError:
                msg = (f"Cannot set '{image_colorspace}' "
                       + f"color space for {image.name} - unsupported")
                self.report_msg('WARNING', msg, infobar=False)

            error_msg = r"Cannot remove temporary file: %s"

            # remove temporary files
            if image.source != 'TILED':
                try:
                    os.remove(temp_filepath)
                except (RuntimeError, OSError):
                    self.report_msg('WARNING', error_msg % temp_filepath,
                                    infobar=False)
                continue

            for tile in image.tiles:
                tile_temp_filepath = temp_filepath.replace(
                    "<UDIM>", str(tile.number))
                try:
                    os.remove(tile_temp_filepath)
                except (RuntimeError, OSError):
                    self.report_msg('WARNING', error_msg % tile_temp_filepath,
                                    infobar=False)

    def bake_process_exit_remove_unused_images(self):
        # remove unused image data blocks
        for key in self.bake_images_ad_data:
            try:
                image = bpy.data.images[key]
            except KeyError:
                continue

            if not any([(self.bake_images_ad_data[key][3] is False
                         and self.bake_images_ad_data[key][4] is False),
                        self.bake_cancel]):
                continue

            filepath = bpy.path.abspath(image.filepath)

            error_msg = r"Cannot remove file: %s: %s"

            # remove ubaked files (or all if cancelled baking)
            if image.source != 'TILED':
                try:
                    os.remove(filepath)
                except (RuntimeError, OSError) as error:
                    self.report_msg('WARNING', error_msg % (filepath, error),
                                    infobar=False)
                bpy.data.images.remove(image, do_unlink=True)
                continue

            for tile in image.tiles:
                tile_filepath = filepath.replace("<UDIM>", str(tile.number))
                try:
                    os.remove(tile_filepath)
                except (RuntimeError, OSError) as error:
                    self.report_msg('WARNING',
                                    error_msg % (tile_filepath, error),
                                    infobar=False)

            bpy.data.images.remove(image, do_unlink=True)

    def bake_process_finish(self, context):
        self.exit_common(context)

        # reset bakemaster
        if context.scene.bm_props.global_use_bakemaster_reset is False:
            return

        # remove objects that were baked
        to_remove = []
        for index, object_shell in enumerate(self.bake_images):
            was_baked = False
            was_baked = len(object_shell[0])
            if was_baked:
                to_remove.append(index)
                continue
            was_baked = len(object_shell[1])
            if was_baked:
                to_remove.append(index)
                continue

        # for BAKE_ALL, trash all objects
        if self.control == 'BAKE_ALL':
            bpy.ops.bakemaster.table_of_objects_trash()
            return

        # add objs highpolies and cages to remove[] too
        for index in to_remove:
            object = context.scene.bm_table_of_objects[index]
            if object.hl_use_unique_per_map:
                for map in object.global_maps:
                    for highpoly in map.hl_highpoly_table:
                        h_index = highpoly.global_highpoly_object_index
                        if h_index != -1 and h_index not in to_remove:
                            to_remove.append(h_index)
                    h_index = map.hl_cage_object_index
                    if h_index != -1 and h_index not in to_remove:
                        to_remove.append(h_index)
            else:
                for highpoly in object.hl_highpoly_table:
                    h_index = highpoly.global_highpoly_object_index
                    if h_index != -1 and h_index not in to_remove:
                        to_remove.append(h_index)
                h_index = object.hl_cage_object_index
                if h_index != -1 and h_index not in to_remove:
                    to_remove.append(h_index)

        # remove objs, using bm_table remove ot
        for index in sorted(to_remove, reverse=True):
            context.scene.bm_props.global_active_index = index
            bpy.ops.bakemaster.table_of_objects_remove()
        context.scene.bm_props.global_active_index = 0

    def handle_bake_invalid(self, report_type=None, report_message=None, skip_type=None):
        if all([report_type is not None, report_message is not None]):
            self.report_msg(report_type, report_message)
        if skip_type == 'OBJECT':
            self.baking_now = False
            self.bake_object_index += 1
            self.bake_object_map_index = 0
            self.bake_object_map_highpoly_index = 0
        elif skip_type == 'MAP':
            self.baking_now = False
            self.bake_object_map_index += 1
            self.bake_object_map_highpoly_index = 0

    def handle_bake_prepare_multires_bake(self, context, multires_mod, type):
        # prepare for multires baking
        context.scene.render.use_bake_multires = True
        context.scene.render.bake_type = type

        if type == 'DISPLACEMENT':
            context.scene.render.use_bake_lores_mesh = self.bake_current_map.map_displacement_use_lowres_mesh
        else:
            context.scene.render.use_bake_lores_mesh = False

        for index, mod in enumerate(self.bake_current_source_object.modifiers):
            self.bake_object_mods_show[index] = mod.show_viewport

            if index == 0 and mod.type == 'MULTIRES':
                mod.show_viewport = True

                map_type = self.bake_current_map.global_map_type.lower()
                if getattr(self.bake_current_map, f'map_{map_type}_data') == 'MULTIRES':
                    self.bake_object_disp_multires_levels = multires_mod.levels
                    multires_mod.levels = getattr(
                        self.bake_current_map, f'map_{map_type}_multires_subdiv_levels')

                continue

            else:
                mod.show_viewport = False

    def handle_bake(self, context):
        # handle bake ot call result
        # bake_result = blender bake ot call
        # can return all default statuses
        # our is ERROR
        # any other except CANCELLED indicates successful start of the bake
        # CANCELLED is returned when other bake is currently running,
        # in that case we still wait for bake in self.modal()

        # get args
        args = self.bake_arguments
        if args is None:
            return {'CANCELLED'}

        try:
            # set OBJECT mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # bake from multires
            obj_multires = [
                mod for mod in self.bake_current_source_object.modifiers if mod.type == 'MULTIRES']
            if args[0].find('MULTIRES') != -1 and len(obj_multires) == 0:
                raise RuntimeError(
                    "map data is Mutlires but %s has no Mutlires Modifiers" % self.bake_current_source_object.name)

            if args[0] == 'MULTIRES_NORMAL':
                self.handle_bake_prepare_multires_bake(
                    context, obj_multires[0], 'NORMALS')
                bake_result = bpy.ops.object.bake_image('INVOKE_DEFAULT')
            elif args[0] == 'MULTIRES_DISPLACEMENT':
                self.handle_bake_prepare_multires_bake(
                    context, obj_multires[0], 'DISPLACEMENT')
                bake_result = bpy.ops.object.bake_image('INVOKE_DEFAULT')

            # render decal map
            # (clean render without compositor)
            elif args[0] == 'RENDER':
                # get data
                map = self.bake_current_map
                container = self.bake_current_container
                out_container = container
                if container.out_use_unique_per_map:
                    out_container = self.bake_current_map
                image = self.bake_image

                tex_type, colorspace, *_ = map_image_getDefaults(
                    context, map, out_container)
                is_data = tex_type in {'DATA', 'LINEAR'}

                self.bake_scene_settings(context, action='SET',
                                         data_bake=is_data)

                # decal render is without compositor, don't have to add nodes
                # context.scene.use_nodes = True
                # nodes = context.scene.node_tree.nodes
                # links = context.scene.node_tree.links

                # mute Render Layers nodes to not trigger render from camera
                # muted_nodes = []
                # for node in nodes:
                #     if node.type in {'R_LAYERS', 'COMPOSITE', 'OUTPUT_FILE'}:
                #         node.mute = True
                #         muted_nodes.append(node)

                # rl_node = nodes.new("CompositorNodeRLayers")
                # comp_node = nodes.new("CompositorNodeComposite")
                # links.new(rl_node.outputs[0], comp_node.inputs[0])
                # links.new(rl_node.outputs[1], comp_node.inputs[1])
                # comp_node.use_alpha = (out_container.out_use_alpha
                #                        and out_alpha_isAllowed(out_container)
                #                        )
                # nodes.active = comp_node

                self.bake_scene_output_settings(context, 'SET', image,
                                                out_container,
                                                render_filepath=image.filepath)

                # update decal view after all render settings were set
                status = self.dv_lot.modal(context)
                if status[0] != {'PASS_THROUGH'} and status[1]:
                    self.report_msg(
                        status[1][0].pop(),
                        "Cannot update Decal Render Frame: %s" % status[1][1])

                msg = f"Baking decal {image.name}..."
                self.report_msg('INFO', msg)

                bpy.ops.render.render(self.render_op_type, animation=False,
                                      write_still=True, use_viewport=False)

                self.image_reload(image, colorspace)

                # # remove created nodes
                # nodes.remove(comp_node)
                # nodes.remove(rl_node)
                # # restore Render Layers nodes
                # for node in muted_nodes:
                #     node.mute = False

                self.bake_scene_settings(context, action='RESTORE')
                self.bake_scene_output_settings(context, 'RESTORE')

                # there is no check for handle_image is_dirty
                self.rendering_decal = True
                return {'FINISHED'}

            # default bake
            else:
                if self._version_current >= (3, 1, 0):
                    bake_result = bpy.ops.object.bake(
                        'INVOKE_DEFAULT',
                        type=args[0],
                        pass_filter=args[1],
                        filepath=args[2],
                        width=args[3],
                        height=args[4],
                        margin=args[5],
                        margin_type=args[6],
                        use_selected_to_active=args[7],
                        max_ray_distance=args[8],
                        cage_extrusion=args[9],
                        cage_object=args[10],
                        normal_space=args[11],
                        normal_r=args[12],
                        normal_g=args[13],
                        normal_b=args[14],
                        target=args[15],
                        save_mode=args[16],
                        use_clear=args[17],
                        use_cage=args[18],
                        use_split_materials=args[19],
                        use_automatic_name=args[20],
                        uv_layer=args[21])

                elif self._version_current >= (2, 92, 0):
                    bake_result = bpy.ops.object.bake(
                        'INVOKE_DEFAULT',
                        type=args[0],
                        pass_filter=args[1],
                        filepath=args[2],
                        width=args[3],
                        height=args[4],
                        margin=args[5],
                        # margin_type=args[6],
                        use_selected_to_active=args[7],
                        max_ray_distance=args[8],
                        cage_extrusion=args[9],
                        cage_object=args[10],
                        normal_space=args[11],
                        normal_r=args[12],
                        normal_g=args[13],
                        normal_b=args[14],
                        target=args[15],
                        save_mode=args[16],
                        use_clear=args[17],
                        use_cage=args[18],
                        use_split_materials=args[19],
                        use_automatic_name=args[20],
                        uv_layer=args[21])

                elif self._version_current >= (2, 90, 0):
                    bake_result = bpy.ops.object.bake(
                        'INVOKE_DEFAULT',
                        type=args[0],
                        pass_filter=args[1],
                        filepath=args[2],
                        width=args[3],
                        height=args[4],
                        margin=args[5],
                        # margin_type=args[6],
                        use_selected_to_active=args[7],
                        max_ray_distance=args[8],
                        cage_extrusion=args[9],
                        cage_object=args[10],
                        normal_space=args[11],
                        normal_r=args[12],
                        normal_g=args[13],
                        normal_b=args[14],
                        # target=args[15],
                        save_mode=args[16],
                        use_clear=args[17],
                        use_cage=args[18],
                        use_split_materials=args[19],
                        use_automatic_name=args[20],
                        uv_layer=args[21])

                else:
                    bake_result = bpy.ops.object.bake(
                        'INVOKE_DEFAULT',
                        type=args[0],
                        pass_filter=args[1],
                        filepath=args[2],
                        width=args[3],
                        height=args[4],
                        margin=args[5],
                        # margin_type=args[6],
                        use_selected_to_active=args[7],
                        # max_ray_distance=args[8],
                        cage_extrusion=args[9],
                        cage_object=args[10],
                        normal_space=args[11],
                        normal_r=args[12],
                        normal_g=args[13],
                        normal_b=args[14],
                        # target=args[15],
                        save_mode=args[16],
                        use_clear=args[17],
                        use_cage=args[18],
                        use_split_materials=args[19],
                        use_automatic_name=args[20],
                        uv_layer=args[21])

        # caught bake error
        except (Exception, RuntimeError) as error:
            # get object data
            # source_object = self.bake_current_source_object

            # report that bake is not valid
            msg = f"Bake Error: {error}"
            self.report_msg('ERROR', msg)

            # switch to the next map
            self.bake_object_map_index += 1
            self.bake_object_map_highpoly_index = 0

            # get, set map data,
            # also run restore_mats and unset_previews in bake_map_get_data
            bake_map_data = self.bake_map_get_data(context)
            status, map, source_cage, source_highpolies = bake_map_data
            # no more maps for the current object
            if status == {'DONE'}:
                # get, set next object data
                # and return ERROR to restart handle_object
                status = self.bake_operate_next_object(
                    context, source_highpolies)
                if status == {'CONTINUE'}:
                    return {'ERROR'}
                return status

            self.baking_now = False
            self.bake_current_map = map
            self.bake_current_source_cage = source_cage
            self.bake_current_source_highpolies = source_highpolies

            # restart handle_object
            return {'ERROR'}

        return bake_result

    def image_scaling(self, image, out_container):
        # WARNING: only the first image's tile gets scaled

        ssaa_scale_factor = int(out_container.out_super_sampling_aa)
        upscale_factor = int(out_container.out_upscaling)

        # get output width, height
        res_enum = out_container.out_res
        if res_enum == 'CUSTOM':
            ssaa_width = out_container.out_res_width
            ssaa_height = out_container.out_res_height
            out_width = out_container.out_res_width * upscale_factor
            out_height = out_container.out_res_height * upscale_factor
        else:
            ssaa_width = int(res_enum)
            ssaa_height = int(res_enum)
            out_width = int(res_enum) * upscale_factor
            out_height = int(res_enum) * upscale_factor

        # scaling down - SSAA
        if ssaa_scale_factor != 1:
            msg = (f"Scaling down {image.name} image "
                   + f"{ssaa_scale_factor} times - applying SSAA")
            self.report_msg('INFO', msg)

            image.scale(ssaa_width, ssaa_height)

        # scaling up
        if upscale_factor != 1:
            msg = (f"Scaling up {image.name} image "
                   + f"{upscale_factor} times - applying Upscaling")
            self.report_msg('INFO', msg)

            image.scale(out_width, out_height)

    def image_reload(self, image, colorspace, tiles_size=0):
        # ensure_colorspace is set to False when baking from multiple
        # highpolies to avoid redundant gamma correction being applied.

        # tiles_size is how many tiles (e.g. 1, 4, 10, or 100)
        if tiles_size == 0:
            tiles_size = len(image.tiles)

        if tiles_size > 1:
            image.source = 'TILED'
        else:
            image.source = 'FILE'

        for i in range(tiles_size):
            image.tiles.new(1001 + i)

        image.reload()

        try:
            image.colorspace_settings.name = colorspace
        except TypeError:
            msg = (f"Cannot set '{colorspace}' "
                   + f"color space for {image.name} - unsupported")
            self.report_msg('WARNING', msg, infobar=False)

    def tiled_image_save_render_and_sssaa(self, image, filepath, out_container,
                                          scene=None, is_last=True):
        tiles_size = len(image.tiles)

        for _ in range(tiles_size):
            tile = image.tiles[0]

            if self._version_current < (3, 3, 0):
                tile_filepath = filepath.replace('<UDIM>', str(tile.number))
            else:
                tile_filepath = filepath

            if is_last:
                self.image_scaling(image, out_container)

            image.save_render(tile_filepath, scene=scene)

            image.tiles.remove(tile)

        # add blank tiles back - thet aren't added on image.reload()
        for i in range(tiles_size):
            image.tiles.new(1001 + i)

    def image_save(self, context, image, out_container, map, is_last=True):
        # Parameters:
        # if is_last is True, cm_use_apply_scene can affect
        bm_props = context.scene.bm_props
        apply_scene = bm_props.cm_use_apply_scene
        color_manage = apply_scene and is_last

        # get colorspace and is_data
        tex_type, colorspace, *_ = map_image_getDefaults(
            context, map, out_container)
        is_data = tex_type in {'DATA', 'LINEAR'}

        if tex_type == 'TEXTURE_LINEAR':
            _, colorspace, *_ = map_image_getDefaults(
                context, map, out_container, tex_type='texture')

        # set scene and render output settings
        self.bake_scene_settings(context, 'SET', data_bake=is_data,
                                 color_manage=color_manage, compositor=False)

        self.bake_scene_output_settings(context, 'SET', image, out_container,
                                        ssaa_downscaled=True)

        # saving
        filepath = image.filepath
        ssaa_scale_factor = int(out_container.out_super_sampling_aa)

        if image.source == 'TILED':
            # image scaling is performed for the first tile only,
            # will need to loop, scale, and remove the tiles one by one
            if self._version_current < (3, 3, 0) or ssaa_scale_factor > 1:
                self.tiled_image_save_render_and_sssaa(
                    image, filepath, out_container, scene=context.scene,
                    is_last=is_last)
            # if no ssaa and Blender >= 3.3, use save_render for tiled image
            else:
                image.save_render(filepath, scene=context.scene)
        else:
            if is_last:
                self.image_scaling(image, out_container)

            image.save_render(filepath, scene=context.scene)

        # image.filepath_raw = filepath
        self.image_reload(image, colorspace)

        if color_manage:
            image.use_view_as_render = True

    def is_v_bake_ready(self, l_name: str) -> bool:
        obj = self.bake_current_source_object

        if self._version_current >= (3, 2, 0):
            vdata = obj.data.color_attributes
        else:
            vdata = obj.data.vertex_colors

        if vdata.find(l_name) == -1:
            print("BakeMaster Error: %s vertex color layer not found. "
                  + "Skipping bake.")
            return True

        # At vertex color layer creation, the last color in its data is filled
        # with transparency. When the last color gets written, it is no longer
        # transparent, thus signifying that the bake has finished.

        layer = vdata[l_name]
        return layer.data[-1].color[3] != 0

    def handle_image(self, context):
        image = self.bake_image
        type = self.bake_image_type

        # if baking to vertex colors,
        # there is no way to check is_dirty
        # so once that bake has started, mark it as ready,
        # go try to prepare and start the next bake
        if type == 'VERTEX_COLORS':
            if self.is_v_bake_ready(image.name):
                self.bake_images_ad_data[image.name][4] = True
                return {'FINISHED'}
            else:
                return {'CONTINUE'}

        # # decal is already rendered
        # if self.rendering_decal:
        #     self.rendering_decal = False
        #     self.bake_images_ad_data[image.name][3] = True
        #     return {'FINISHED'}

        # # is image baked?
        # if image.is_dirty is False:
        #     return {'CONTINUE'}

        # elif not self.bake_images_ad_data[image.name][3]:
            # mark image as ready
            # self.bake_images_ad_data[image.name][3] = True

            # XXX:
            # TEXSETS ONLY! (yet idk exactly why):
            # recently, all images in Blender >= 3.4.1 (I may be wrong about
            # the version here) get True is_dirty slightly before the bake
            # finishes. The only dirty solution (kinda solution) I've come up
            # with is requery this function once again.
            # Before, no return was here:
            # return {'CONTINUE'}

        image_baked = image.is_dirty or self.rendering_decal
        if not image_baked:
            self.bake_images_ad_data[image.name][3] = False
            return {'CONTINUE'}
        elif not self.bake_images_ad_data[image.name][3]:
            # self.handle_image_wait_delay = time.time()
            self.bake_images_ad_data[image.name][3] = True
            return {'CONTINUE'}

        # if time.time() - self.handle_image_wait_delay < self.wait_delay * 10:
        #    return {'CONTINUE'}
        self.bake_images_ad_data[image.name][3] = False

        is_last = self.bake_images_ad_data[image.name][5] <= 1
        len_of_highpolies = len(self.bake_current_source_highpolies)
        is_last_highpoly = (len_of_highpolies == 0
                            or self.bake_object_map_highpoly_index + 1
                            >= len_of_highpolies)

        container = self.bake_current_container
        map = self.bake_current_map
        source_object = self.bake_current_source_object

        out_container = container
        if container.out_use_unique_per_map:
            out_container = map

        if not is_last_highpoly:
            self.image_save(context, image, out_container, map, is_last)
            return {'FINISHED'}

        if not is_last:
            self.bake_images_ad_data[image.name][5] -= 1
            self.image_save(context, image, out_container, map, is_last)
            return {'FINISHED'}

        # mark image as ready
        self.bake_images_ad_data[image.name][3] = True

        # saving

        # image is on the last iteration => do post-processing and apply SSAA
        bm_props = context.scene.bm_props
        use_denoise = out_container.out_use_denoise
        use_compositor = bm_props.cm_use_compositor

        if any([use_denoise, use_compositor]):
            msg = ("Post-Processing (Denoising, Applying "
                   + f"Compositor) image {image.name}...")
            self.report_msg('INFO', msg, infobar=False)

            msg = f"Baking {source_object.name}: Post-Processing {image.name}"
            self.report_msg('PROGRESS', msg)

        # denoising & applying compositor
        # color_manage is False because image is resaved after
        self.handle_image_post_process(
            context, image, map, out_container,
            use_denoise, use_compositor,
            color_manage=False)

        self.image_save(context, image, out_container, map, is_last)

        # image is ready
        return {'FINISHED'}

    def handle_object_finish(self, context):
        # get object data
        container = self.bake_current_container
        object = self.bake_current_object
        source_object = self.bake_current_source_object
        # set source_object as active
        source_object = self.bake_scene_object_get_and_setactive(
            context, source_object.name)

        # finish object
        self.bake_finish_object(context, container, object, source_object)

        # restore after decal bake
        if object.decal_is_decal:
            self.dv_lot.cancel(context)
            del self.dv_lot

        # remove multires added for highpoly
        self.bake_map_remove_highpoly_multires(source_object)
        self.bake_map_restore_object_multires(source_object)

    def handle_object(self, context):
        # check if there was an unhandled error
        if self.bake_error:
            self.bake_error = False
            return {'ERROR'}

        # handle_image
        if self.baking_now and self.bake_image is not None:
            # check if image has been baked
            if self.handle_image(context) == {'FINISHED'}:
                self.baking_now = False

                map_bake_time = self.get_time_diff(map=True)
                msg = "%s baked in %s" % (self.bake_image.name, map_bake_time)
                self.report_msg('PROGRESS', msg, infobar=False)
                self.last_map_start_time = time.time()

                # get object data
                container = self.bake_current_container
                object = self.bake_current_object
                source_object = self.bake_current_source_object
                # get map data
                map = self.bake_current_map
                source_highpolies = self.bake_current_source_highpolies

                # switch to the next map
                # if baked all highpolies or there were no highpolies
                self.bake_object_map_highpoly_index += 1
                len_of_highpolies = len(source_highpolies)
                if (len_of_highpolies == 0
                    or self.bake_object_map_highpoly_index
                        == len_of_highpolies):

                    # finish map
                    # there is no check if self.bake_image is vrtxcolorlayer
                    self.bake_finish_map(container, object, source_object, map,
                                         self.bake_image)

                    self.bake_object_map_index += 1
                    self.bake_object_map_highpoly_index = 0

                    # get, set map data
                    bake_map_data = self.bake_map_get_data(context)
                    status, map, source_cage, source_highpolies = bake_map_data
                    # no more maps for the current object
                    if status == {'DONE'}:
                        # get, set next object data and CONTINUE
                        status = self.bake_operate_next_object(
                            context, source_highpolies)
                        return status
                    self.bake_current_map = map
                    self.bake_current_source_cage = source_cage
                    self.bake_current_source_highpolies = source_highpolies

                if self.bake_cancel:
                    return {'DONE'}

            else:
                return {'CONTINUE'}

        # move to the next object if all maps for the current are already baked
        object_len_of_maps = len(self.bake_images[self.bake_object_index][0])
        if (self.bake_object_map_index == object_len_of_maps
                and object_len_of_maps != 0):
            # get, set next object data and CONTINUE
            status = self.bake_operate_next_object(context)
            return status

        # proceed to BAKE-READY status
        elif self.baking_now is False:
            self.baking_now = True

            # check that render engine is CYCLES
            if context.scene.render.engine != 'CYCLES':
                report_msg = "Current render engine does not support baking"
                self.handle_bake_invalid('ERROR', report_msg, 'OBJECT')
                return {'CONTINUE'}

            # set object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # get, set current object data
            # only for the first object, for the first map
            if (self.bake_object_index == -1
                    and self.bake_object_map_index == 0):
                # get, set next object data and CONTINUE
                status = self.bake_operate_next_object(context)
                # no more objects
                if status == {'DONE'}:
                    return status
                self.baking_now = True

            # set object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # get, set map data
            # only for the first map
            if self.bake_object_map_index == 0:
                bake_map_data = self.bake_map_get_data(context)
                status, map, source_cage, source_highpolies = bake_map_data
                # no more maps for the current object
                if status == {'DONE'}:
                    # get, set next object data and CONTINUE
                    status = self.bake_operate_next_object(
                        context, source_highpolies)
                    return status
                self.bake_current_map = map
                self.bake_current_source_cage = source_cage
                self.bake_current_source_highpolies = source_highpolies

            # get object data
            container = self.bake_current_container
            object = self.bake_current_object
            source_object = self.bake_current_source_object
            # get map data
            map = self.bake_current_map
            source_cage = self.bake_current_source_cage
            source_highpolies = self.bake_current_source_highpolies or []

            # disable 3d viewport local view
            context_override = context.copy()

            for area in context.screen.areas:
                if area is None or area.ui_type != 'VIEW_3D':
                    continue

                view_3d = area.spaces.active
                if view_3d.local_view is None:
                    continue

                view_3d_region = None
                for region in area.regions:
                    if region is None or region.type != 'WINDOW':
                        continue
                    view_3d_region = region
                    break

                context_override['area'] = area
                context_override['region'] = view_3d_region

                if self._version_current >= (3, 2, 0):
                    with context.temp_override(**context_override):
                        bpy.ops.view3d.localview()
                else:
                    bpy.ops.view3d.localview(context_override)

            # make source_object, source_cage visible in the scene
            if source_object.visible_get() is False:
                source_object.hide_viewport = False
                source_object.hide_set(False)
            if source_cage is not None:  # if no cage chosen, it's NoneType
                if source_cage.visible_get() is False:
                    source_cage.hide_viewport = False
                    source_cage.hide_set(False)

            # set object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # remove multires added for highpoly
            self.bake_map_remove_highpoly_multires(source_object)
            self.bake_map_restore_object_multires(source_object)

            # add camera object if no
            objs = context.scene.objects
            if len([obj for obj in objs if obj.type == 'CAMERA']) == 0:
                bpy.ops.object.camera_add()

            # manage highpoly selection
            select_highpoly = False
            prep_multires = False
            if len(source_highpolies) != 0:
                select_highpoly = True
            if map.global_map_type == 'DISPLACEMENT':
                if map.map_displacement_data == 'HIGHPOLY':
                    select_highpoly = False
                    prep_multires = True
                elif map.map_displacement_data == 'MULTIRES':
                    select_highpoly = False
                elif len(source_highpolies) != 0:
                    select_highpoly = True
            if map.global_map_type == 'NORMAL':
                if map.map_normal_data == 'MULTIRES':
                    select_highpoly = False
                elif map.map_normal_data == 'MATERIAL':
                    select_highpoly = False
                elif len(source_highpolies) != 0:
                    select_highpoly = True

            # set object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            if select_highpoly:
                source_highpoly = source_highpolies[
                    self.bake_object_map_highpoly_index]
                if source_highpoly.visible_get() is False:
                    source_highpoly.hide_viewport = False
                source_highpoly = self.bake_scene_object_get_and_setactive(
                    context, source_highpoly.name)

                # hide_render true for all highpolies except the current one
                for source_highpoly1_index, source_highpoly1 in enumerate(
                        source_highpolies):
                    source_highpoly1.hide_render = True
                    if (source_highpoly1_index
                            == self.bake_object_map_highpoly_index):
                        source_highpoly1.hide_render = False
                    source_highpoly1.hide_set(False)

                # set source_object as active in the scene
                source_object.select_set(True)
                context.view_layer.objects.active = source_object

                highpoly = None
                if object.hl_use_unique_per_map:
                    for map in object.global_maps:
                        for highpoly_object in map.hl_highpoly_table:
                            if (highpoly_object.global_object_name
                                    != source_highpoly.name):
                                continue
                            highpoly = context.scene.bm_table_of_objects[
                                highpoly_object.global_highpoly_object_index]
                            break
                else:
                    for highpoly_object in object.hl_highpoly_table:
                        if (highpoly_object.global_object_name
                                != source_highpoly.name):
                            continue
                        highpoly = context.scene.bm_table_of_objects[
                            highpoly_object.global_highpoly_object_index]
                        break
                if highpoly is None:
                    shell_index = 0
                elif highpoly.hl_is_decal and container.hl_decals_use_separate_texset:
                    shell_index = 1
                else:
                    shell_index = 0

            else:
                # disable highpolies affect
                for source_highpoly1 in source_highpolies:
                    source_highpoly1.hide_render = True
                # set source_object as active in the scene
                source_object = self.bake_scene_object_get_and_setactive(
                    context, source_object.name)

                # prepare multires modifiers for displacement highpoly bake
                if prep_multires:
                    if len(source_highpolies) != 0:
                        source_highpoly = source_highpolies[
                            self.bake_object_map_highpoly_index]
                    else:
                        source_highpoly = None
                    self.bake_map_prepare_highpoly_multires(
                        map, source_object, source_highpoly)

                source_highpoly = None
                shell_index = 0

            # get bake_arguments
            image_name = self.bake_images[self.bake_object_index][shell_index][
                self.bake_object_map_index]
            bake_args, report_data = self.bake_get_arguments(
                context, container, object, source_object, source_cage,
                source_highpoly, map, image_name)

            # bake_arguments are invalid, skip map, CONTINUE
            if len(bake_args) == 0:
                self.handle_bake_invalid(report_data[0], report_data[1], 'MAP')
                # get, set map data
                bake_map_data = self.bake_map_get_data(context)
                status, map, source_cage, source_highpolies = bake_map_data
                # no more maps for the current object
                if status == {'DONE'}:
                    # get, set next object data and CONTINUE
                    status = self.bake_operate_next_object(
                        context, source_highpolies)
                    return status
                self.baking_now = False
                self.bake_current_map = map
                self.bake_current_source_cage = source_cage
                self.bake_current_source_highpolies = source_highpolies
                return {'CONTINUE'}

            # set bake_arguments
            self.bake_arguments = bake_args

            # set bake_image
            self.bake_image_type = bake_args[15]
            self.bake_image = self.bake_image_get_or_create(
                context, image_name, container, object, source_object, map,
                shell_index)

            # prepare image
            self.bake_image_prepare(context, source_object, container, map,
                                    self.bake_image, self.bake_image_type)

            return {'BAKE-READY'}

        # waiting bake to finish
        return {'CONTINUE'}

    def modal(self, context, event):
        try:
            now = time.time()

            # cancelling bake queue
            if self.bake_cancel is False:
                if event.type == 'BACK_SPACE':
                    msg = "Cancelled all next bakes in the queue"
                    self.report_msg('INFO', msg)
                    # self.last_report_time = now + 0.5

                    self.bake_cancel = True
                    self.exit_common(context)
                    return {'FINISHED'}

            # bake done
            if self.bake_done:
                if now - self.last_report_time > self.report_delay:
                    self.bake_process_finish(context)
                    return {'FINISHED'}
                else:
                    return {'PASS_THROUGH'}

            if event.type == 'TIMER':
                # starting bake
                if self.waiting_start_bake and self.baking_now:
                    res = self.handle_bake(context)

                    # CANCELLED is returned when other bake is running.
                    # In that case, wait for the bake to start
                    if res != {'CANCELLED'}:
                        self.waiting_start_bake = False
                        self.last_map_start_time = now

                    if res == {'DONE'}:
                        self.bake_done = True

                # handling object
                # done baking is also checked in handle_object,
                # because in that method image.is_dirty is being checked
                elif not self.wait_handle_object:
                    self.wait_handle_object = True
                    res = self.handle_object(context)
                    self.wait_handle_object = False

                    # done baking
                    if res == {'DONE'}:
                        self.bake_done = True

                    # caught error or cancelled, exiting bake and finishing
                    elif res == {'ERROR'} or res == {'CANCELLED'}:
                        self.exit_common(context)
                        return {'FINISHED'}

                    # when object is ready to start baking,
                    # waiting_start_bake is set to True
                    elif res == {'BAKE-READY'}:
                        self.waiting_start_bake = True

                    # res can also be CONTINUE,
                    # which means that the bake should have been started,
                    # and handle_object is checking for image.is_dirty
                    # to report that bake has been finished

                if now - self.last_report_time > self.report_delay:
                    self.last_report_time = now
                    self.report_bake_progress()

            return {'PASS_THROUGH'}

        except KeyboardInterrupt:
            msg = "Bake Process Interrupted by user - execution aborted"
            self.report_msg('ERROR', msg)

            self.exit_common(context)
            return {'FINISHED'}

        except Exception as error:
            msg = (f"Code Execution Error: {error}.\nPlease, contact support: "
                   + "click 'Support' in the Help panel (below Bake buttons).")
            self.report_msg('ERROR', msg)

            print(("\nBakeMaster Code Error Traceback:\n "
                   + "%s\n\n" % traceback.format_exc()))

            self.exit_common(context)
            return {'FINISHED'}

    def bake_get_arguments(self, _, container, object, source_object,
                           source_cage, source_highpoly, map, image_name):
        # get bake arguments for the current map

        report_type = None
        report_message = None
        # returns bake_arguments[]:
        # 0 - type
        # 1 - pass_filter
        # 2 - filepath
        # 3 - width
        # 4 - height
        # 5 - margin
        # 6 - margin_type
        # 7 - use_selected_to_active
        # 8 - max_ray_distance
        # 9 - cage_extrusion
        # 10 - cage_object
        # 11 - normal_space
        # 12 - normal_r
        # 13 - normal_g
        # 14 - normal_b
        # 15 - target
        # 16 - save_mode
        # 17 - use_clear
        # 18 - use_cage
        # 19 - use_split_materials
        # 20 - use_automatic_name
        # 21 - uv_layer

        # type
        types = {
            'COMBINED': ['C_COMBINED'],
            'AO': ['C_AO'],
            'SHADOW': ['C_SHADOW'],
            'NORMAL': ['C_NORMAL', 'NORMAL'],
            'UV': ['C_UV'],
            'ROUGHNESS': ['C_ROUGHNESS', 'ROUGHNESS'],
            'EMIT': [
                'METALNESS',
                'DIFFUSE',
                'SPECULAR',
                'GLOSSINESS',
                'OPACITY',
                'EMISSION',
                'NORMAL',
                'DISPLACEMENT',
                'VECTOR_DISPLACEMENT',
                'POSITION',
                'DECAL',
                'AO',
                'CAVITY',
                'CURVATURE',
                'THICKNESS',
                'ID',
                'MASK',
                'XYZMASK',
                'GRADIENT',
                'EDGE',
                'WIREFRAME',
                'PASS',
                'VERTEX_COLOR_LAYER',
                'C_EMIT',
            ],
            'ENVIRONMENT': ['C_ENVIRONMENT'],
            'DIFFUSE': ['ALBEDO', 'C_DIFFUSE'],
            'GLOSSY': ['C_GLOSSY'],
            'TRANSMISSION': ['C_TRANSMISSION'],
            'POSITION': ['C_POSITION'],
        }
        map_type = map.global_map_type
        types_available = [key for key in types if map_type in types[key]]
        try:
            types_available[0]
        except IndexError:
            report_type = 'ERROR'
            report_message = "%s Error: Invalid Map Type" % source_object.name
            return [], [report_type, report_message]
        type = types_available[0]
        # change type for Normal, Displacement maps
        # (they can have different bake type for different map data)
        if map.global_map_type == 'NORMAL':
            if map.map_normal_data == 'HIGHPOLY':
                type = 'NORMAL'
            elif map.map_normal_data == 'MULTIRES':
                type = 'MULTIRES_NORMAL'
            elif map.map_normal_data == 'MATERIAL':
                # type = 'EMIT'
                type = 'NORMAL'
        elif map.global_map_type == 'DISPLACEMENT':
            if map.map_displacement_data == 'HIGHPOLY':
                type = 'MULTIRES_DISPLACEMENT'
            elif map.map_displacement_data == 'MULTIRES':
                type = 'MULTIRES_DISPLACEMENT'
            elif map.map_displacement_data == 'MATERIAL':
                type = 'EMIT'

        # decal object is not baked but rendered
        if object.decal_is_decal:
            type = 'RENDER'

        # pass_filter
        pass_filter = set()
        if type in ['COMBINED', 'DIFFUSE', 'GLOSSY', 'TRANSMISSION']:
            pass_filter_init = {
                'DIRECT': map.map_cycles_use_pass_direct,
                'INDIRECT': map.map_cycles_use_pass_indirect,
                'COLOR': map.map_cycles_use_pass_color,
            }
            if map.global_map_type == 'C_COMBINED':
                pass_filter_init = {
                    'DIRECT': map.map_cycles_use_pass_direct,
                    'INDIRECT': map.map_cycles_use_pass_indirect,
                    'DIFFUSE': map.map_cycles_use_pass_diffuse,
                    'GLOSSY': map.map_cycles_use_pass_glossy,
                    'TRANSMISSION': map.map_cycles_use_pass_transmission,
                    'AO': map.map_cycles_use_pass_ambient_occlusion if self._version_current < (3, 0, 0) else False,
                    'EMIT': map.map_cycles_use_pass_emit,
                }
                # not enough passes
                if not any([map.map_cycles_use_pass_direct, map.map_cycles_use_pass_indirect, map.map_cycles_use_pass_emit]):
                    report_type = 'ERROR'
                    report_message = "%s Error: Not enought passes to bake Cycles Map" % source_object.name
                    return [], [report_type, report_message]
            pass_filter = set(
                key for key in pass_filter_init if pass_filter_init[key])
            # only COLOR for albedo
            if map.global_map_type == 'ALBEDO':
                pass_filter = {'COLOR'}

        # out_container
        if container.out_use_unique_per_map:
            out_container = map
        else:
            out_container = container

        # filepath, save_mode
        # INTERNAL + valid filepath = broken baked image data
        # EXTERNAL = Blender reports "Baking map saved to internal bla bla bla"
        # => we do INTERNAL + empty filepath
        save_mode = 'EXTERNAL'
        # try:
        #     filepath = bpy.data.images[image_name].filepath
        # except KeyError:
        #     filepath = image_name
        filepath = ""

        ssaa_scale_factor = int(out_container.out_super_sampling_aa)

        # width, height
        res_enum = out_container.out_res
        if res_enum == 'CUSTOM':
            width = out_container.out_res_width
            height = out_container.out_res_height
        else:
            width = int(res_enum)
            height = int(res_enum)
        # bake at a higher res based of ssaa value
        width *= ssaa_scale_factor
        height *= ssaa_scale_factor

        # margin
        margin = out_container.out_margin * ssaa_scale_factor
        # margin_type
        margin_type = out_container.out_margin_type

        # use_cage and hl_container
        if object.hl_use_unique_per_map:
            hl_container = map
            use_cage = map.hl_use_cage
        else:
            hl_container = object
            use_cage = object.hl_use_cage

        # use_selected_to_active
        use_selected_to_active = (source_highpoly is not None)
        # max_ray_distance
        max_ray_distance = hl_container.hl_max_ray_distance
        # cage_extrusion
        cage_extrusion = hl_container.hl_cage_extrusion
        # cage_object
        if source_cage is None or use_selected_to_active is False:
            use_cage = False
            cage_object = ""
        else:
            cage_object = source_cage.name

        # normal_space
        normal_space = map.map_normal_space
        # normal r, g, b
        if '_OPENGL' in map.map_normal_preset or map.map_normal_custom_preset == 'OPEN_GL':
            normal_r = 'POS_X'
            normal_g = 'POS_Y'
            normal_b = 'POS_Z'

        elif '_DIRECTX' in map.map_normal_preset or map.map_normal_custom_preset == 'DIRECTX':
            normal_r = 'POS_X'
            normal_g = 'NEG_Y'
            normal_b = 'POS_Z'
        else:
            normal_r = map.normal_r
            normal_g = map.normal_g
            normal_b = map.normal_b

        # uv_container
        if container.uv_use_unique_per_map:
            uv_container = map
        else:
            uv_container = container

        # target
        target = uv_container.uv_bake_target
        # uv_layer
        if container.nm_uni_container_is_global:
            uv_layer = object.uv_active_layer
        else:
            uv_layer = uv_container.uv_active_layer

        # use_clear
        # True when image is baked for the first time
        use_clear = self.bake_images_ad_data[image_name][7]
        self.bake_images_ad_data[image_name][7] = False

        # use_split_materials
        use_split_materials = False
        # use_automatic_name
        use_automatic_name = False

        return [
            type,
            pass_filter,
            filepath,
            width,
            height,
            margin,
            margin_type,
            use_selected_to_active,
            max_ray_distance,
            cage_extrusion,
            cage_object,
            normal_space,
            normal_r,
            normal_g,
            normal_b,
            target,
            save_mode,
            use_clear,
            use_cage,
            use_split_materials,
            use_automatic_name,
            uv_layer,
        ], [report_type, report_message]

    def bm_map_has_color(self, bm_map):
        maps_with_rgb_color = [
            'ALBEDO',
            # 'METALNESS',
            # 'ROUGHNESS',
            'DIFFUSE',
            'SPECULAR',
            # 'GLOSSINESS',
            # 'OPACITY',
            'EMISSION',

            'NORMAL',
            # 'DISPLACEMENT',
            'VECTOR_DISPLACEMENT',
            'POSITION',
            'DECAL',
            # 'AO',
            # 'CAVITY',
            # 'CURVATURE',
            # 'THICKNESS',
            'ID',
            'MASK',
            # 'XYZMASK',
            # 'GRADIENT',
            # 'EDGE',
            # 'WIREFRAME',

            'PASS',
            'VERTEX_COLOR_LAYER',
            'C_COMBINED',
            # 'C_AO',
            'C_SHADOW',
            'C_POSITION',
            'C_NORMAL',
            'C_UV',
            # 'C_ROUGHNESS',
            'C_EMIT',
            'C_ENVIRONMENT',
            'C_DIFFUSE',
            # 'C_GLOSSY',
            # 'C_TRANSMISSION'
        ]

        return bm_map.global_map_type in maps_with_rgb_color

    def v_channel_pack_proceed(self, raw_layers):
        layers = []
        k_packable = 0
        channels = len(raw_layers)

        h_layer = raw_layers[0][1]

        for rl in raw_layers:
            if not rl[0]:
                layers.append([None, rl[2]])
                continue

            k_packable += 1
            if rl[1] is None or not self.bake_images_ad_data[rl[1].name][4]:
                layers.append([None, rl[2]])
                continue

            layers.append([rl[1], rl[2]])
            if h_layer is None:
                h_layer = rl[1]

        if k_packable == 0 or h_layer is None:
            return

        mesh = h_layer.id_data
        vdata = self.mesh_get_vdata(mesh)

        channel_i = -1
        for layer, bm_map in layers:
            channel_i += 1

            if layer is None or layer.name == h_layer.name:
                if channels == 2 and channel_i == 0:
                    channel_i = 2
                continue

            msg = f"Channel Packing {layer.name} vertex color layer..."
            self.report_msg('INFO', msg)

            for i in range(len(layer.data)):
                color = layer.data[i].color
                h_color = h_layer.data[i].color

                if channels == 2 and channel_i == 0:  # rgb -> rgb for rgb+a
                    a = color[3]
                    color.foreach_get(h_color)
                    h_color[3] = a
                    channel_i = 2
                    continue

                if self.bm_map_has_color(bm_map):
                    luminosity = colorsys.rgb_to_hls(*color[:-1])
                else:
                    luminosity = color[0]

                h_color[channel_i] = luminosity

        for layer, _ in reversed(layers):
            if layer is None or layer.name == h_layer.name:
                continue
            vdata.remove(layer)

    def img_channel_pack_proceed(self, context, images_raw, _, out_container):
        if len(images_raw) not in {2, 3, 4}:
            msg = (f"Received only {len(images_raw)} images for Channel Pack -"
                   + "others weren't baked or added. Skippping.")
            self.report_msg('WARNING', msg)
            return

        # reconstruct images based on whether they are enabled
        # in the channel pack
        images = []
        k_packable = 0

        for image_shell in images_raw:
            if not image_shell[0]:
                images.append(None)
                continue

            k_packable += 1
            if image_shell[1] is None or self.bake_images_ad_data[
                    image_shell[1].name][4]:
                images.append(None)
            else:
                images.append(image_shell[1])

        # report invalid images
        if k_packable == 0:
            # msg = "Channel Pack received 0 valid images. Skipping."
            # self.report_msg('WARNING', msg)
            return

        self.bake_scene_settings(context, action='SET', data_bake=True,
                                 compositor=True)

        # adding compos nodes in Compositor
        context.scene.use_nodes = True
        nodes = context.scene.node_tree.nodes
        links = context.scene.node_tree.links

        if len(images) == 2:
            nodes_types = ["CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeComposite"]
        elif len(images) == 3:
            nodes_types = ["CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeCombRGBA",
                           "CompositorNodeComposite"]
        else:
            nodes_types = ["CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeImage",
                           "CompositorNodeCombRGBA",
                           "CompositorNodeComposite"]

        # mute Render Layers nodes to not trigger render from camera
        muted_nodes = []
        for node in nodes:
            if node.type in {'R_LAYERS', 'COMPOSITE', 'OUTPUT_FILE'}:
                node.mute = True
                muted_nodes.append(node)

        compos_nodes = []
        for node_type in nodes_types:
            new_node = nodes.new(node_type)
            compos_nodes.append(new_node)

        # set active node to be the last composite node
        nodes.active = compos_nodes[-1]

        # get max tiles size for tiled images
        max_tiles = 1
        max_image_index = 0
        reset_image_index = 0
        # filepath to reopen channel packed image later
        for image_index, image in enumerate(images):
            if image is None:
                continue
            # filepath_init = image.filepath.replace("<UDIM>", "1001")
            image_name = image.name
            # colorspace = image.colorspace_settings.name
            reset_image_index = image_index
            break
        for image_index, image in enumerate(images):
            if image is None:
                continue
            if image.source != 'TILED':
                continue
            if len(image.tiles) > max_tiles:
                max_tiles = len(image.tiles)
                max_image_index = image_index

        if images[max_image_index] is None:
            max_image_index = reset_image_index
        # filepath_init = bpy.path.abspath(
        #     images[max_image_index].filepath.replace("<UDIM>", "1001"))
        image_name = images[max_image_index].name
        load_filepath = bpy.path.abspath(images[max_image_index].filepath)
        # colorspace = images[max_image_index].colorspace_settings.name

        # set render output settings to match image format settings
        color_mode = 'RGBA' if len(images) in [2, 4] else 'RGB'

        self.bake_scene_output_settings(
            context, 'SET', images[max_image_index], out_container,
            color_mode=color_mode,
            ssaa_downscaled=True)  # filepath=filepath_init)

        # copy filepaths
        images_init = []
        images_remove = []
        for image_index, image in enumerate(images):
            if image is None:
                continue
            images_remove.append(image.name)
            remove = True
            if image_index == max_image_index:
                remove = False
            tiles = 1
            if image.source == 'TILED':
                tiles = len(image.tiles)
            images_init.append([tiles, bpy.path.abspath(image.filepath),
                                remove])

        # operate channel pack
        # old_tile_index = "1001"
        for tile_index in range(max_tiles):
            new_tile_index = str(1001 + tile_index)
            # set image nodes' images
            # or set image to None if all its tiles have been channel packed
            for image_index, image in enumerate(images):
                if image is None:
                    continue
                if image.source == 'SINGLE' and tile_index == 1:
                    images[image_index] = None
                elif (image.source == 'TILED'
                        and len(image.tiles) == tile_index):
                    images[image_index] = None

                if image is not None:
                    compos_nodes[image_index].image = image

            # info prints
            msg = (f"Channel Packing image {image_name}, "
                   + f"tile {tile_index + 1}...")
            self.report_msg('INFO', msg)

            # link compos nodes
            # unlink if NoneType image
            if len(images) == 2:
                links.new(compos_nodes[0].outputs[0],
                          compos_nodes[2].inputs[0])
                links.new(compos_nodes[1].outputs[0],
                          compos_nodes[2].inputs[1])
                compos_nodes[2].use_alpha = True
                if images[0] is None:
                    links.remove(compos_nodes[2].inputs[0].links[0])
                if images[1] is None:
                    links.remove(compos_nodes[2].inputs[1].links[0])
                    compos_nodes[2].use_alpha = False
            elif len(images) == 3:
                links.new(compos_nodes[0].outputs[0],
                          compos_nodes[3].inputs[0])
                links.new(compos_nodes[1].outputs[0],
                          compos_nodes[3].inputs[1])
                links.new(compos_nodes[2].outputs[0],
                          compos_nodes[3].inputs[2])
                links.new(compos_nodes[3].outputs[0],
                          compos_nodes[4].inputs[0])
                if images[0] is None:
                    links.remove(compos_nodes[3].inputs[0].links[0])
                if images[1] is None:
                    links.remove(compos_nodes[3].inputs[1].links[0])
                if images[2] is None:
                    links.remove(compos_nodes[3].inputs[2].links[0])
                compos_nodes[4].use_alpha = False
            else:
                links.new(compos_nodes[0].outputs[0],
                          compos_nodes[4].inputs[0])
                links.new(compos_nodes[1].outputs[0],
                          compos_nodes[4].inputs[1])
                links.new(compos_nodes[2].outputs[0],
                          compos_nodes[4].inputs[2])
                links.new(compos_nodes[3].outputs[0],
                          compos_nodes[5].inputs[1])
                links.new(compos_nodes[4].outputs[0],
                          compos_nodes[5].inputs[0])
                compos_nodes[5].use_alpha = True
                if images[0] is None:
                    links.remove(compos_nodes[4].inputs[0].links[0])
                if images[1] is None:
                    links.remove(compos_nodes[4].inputs[1].links[0])
                if images[2] is None:
                    links.remove(compos_nodes[4].inputs[2].links[0])
                if images[3] is None:
                    links.remove(compos_nodes[5].inputs[1].links[0])
                    compos_nodes[5].use_alpha = False

            # old_tile_index = new_tile_index

            # render and save channel packed image
            # write still - will save to the disk automatically
            # if we set render.filepath
            render_filepath = images[max_image_index].filepath.replace(
                "<UDIM>", new_tile_index)
            context.scene.render.filepath = render_filepath
            bpy.ops.render.render(self.render_op_type, animation=False,
                                  write_still=True, use_viewport=False)

            # remove tiles
            for image_index, image in enumerate(images):
                if image is None:
                    continue
                if image.source != 'TILED':
                    continue
                tile = image.tiles[0]
                image.tiles.remove(tile)

        # delete images from disk
        for image_f in images_init:
            if image_f[2] is False:
                continue
            for tile_index in range(image_f[0]):
                f = image_f[1].replace("<UDIM>", str(1001 + tile_index))
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                except (RuntimeError, OSError):
                    pass

        # mark channel packed images so that they won't be packed again
        # (happens with texsets)
        for image_to_remove in images_remove:
            self.bake_images_ad_data[image_to_remove][6] = False
            bpy.data.images.remove(bpy.data.images[image_to_remove],
                                   do_unlink=True)  # XXX

        # load first channel packed image
        colorspace = self.bake_image_get_colorspace(context, tex_type='data')
        channel_packed_image = bpy.data.images.load(load_filepath)

        self.image_reload(channel_packed_image, colorspace,
                          tiles_size=max_tiles)

        # remove created compos nodes
        for node in compos_nodes:
            nodes.remove(node)
        # restore Render layers nodes
        for node in muted_nodes:
            node.mute = False

        self.bake_scene_settings(context, action='RESTORE')
        self.bake_scene_output_settings(context, 'RESTORE')

    def bake_process_exit_handle_channel_pack(self, context):
        # handle maps channel pack
        for data_index, chnlp_data in enumerate(self.bake_channel_pack_data):
            for data in chnlp_data:
                if len(data[1]) == 0 or data[0] == '':
                    continue

                container = context.scene.bm_table_of_objects[
                    self.bake_objects_indexes[data_index]]

                # get out_container
                out_container = container
                if container.out_use_unique_per_map:
                    for map_index in data[1]:
                        try:
                            container.global_maps[map_index[1]]
                        except (KeyError, IndexError):
                            out_container = container
                        else:
                            out_container = container.global_maps[map_index[1]]
                            break

                for shell_index in range(2):
                    images = []

                    has_v_bake = False
                    has_img_bake = False

                    for image_index in data[1]:
                        if image_index[1] == 'NONE':
                            images.append([False, None, None])
                            continue

                        bm_map = container.global_maps[image_index[1]]
                        image_name = self.bake_images[data_index][shell_index][
                            image_index[1]]

                        # check if baked and wasn't channel packed previously
                        if not ((self.bake_images_ad_data[image_name][3]
                                 or self.bake_images_ad_data[image_name][4])
                                and self.bake_images_ad_data[image_name][6]):
                            images.append([False, None, bm_map])
                            continue

                        if self.bake_images_ad_data[image_name][4]:
                            try:
                                source_object = context.scene.objects[
                                    self.bake_images_ad_data[image_name][2]]
                            except KeyError:
                                images.append([False, None, bm_map])
                                msg = (f"Cannot channel pack {image_name} "
                                       + "vertex colors layer, "
                                       + "corresponding Object not found")
                                self.report_msg('WARNING', msg)
                                continue

                            vdata = self.obj_get_vdata(source_object)
                            layer = self.vdata_get_layer(vdata, image_name)

                            if layer is None:
                                images.append([False, None, bm_map])
                                msg = (f"Cannot channel pack {image_name} "
                                       + "vertex colors layer for "
                                       + f"{source_object.name}, layer not"
                                       + " found")
                                continue

                            images.append([image_index[0], layer, bm_map])
                            has_v_bake = True
                            continue

                        try:
                            image = bpy.data.images[image_name]
                        except KeyError:
                            images.append([False, None, bm_map])
                            msg = (f"Cannot channel pack {image_name} "
                                   + "image, image not found")
                            self.report_msg('WARNING', msg)
                            continue

                        images.append([image_index[0], image, bm_map])
                        has_img_bake = True

                    # proceed channel pack
                    if has_img_bake:
                        if has_v_bake:
                            msg = ("Cannot channel pack images and vertex "
                                   + "color layers together. Vertex color "
                                   + "layers will be skipped")
                            self.report_msg('WARNING', msg)

                        self.img_channel_pack_proceed(
                            context, images, container, out_container)

                    elif has_v_bake:
                        self.v_channel_pack_proceed(images)

    def handle_image_post_process(self, context, image, map, out_container,
                                  use_denoise: bool, use_compositor: bool,
                                  color_manage: bool):
        if not any([use_denoise, use_compositor]):
            return

        # ommitting linear srgb because image is resaved after post-processing
        tex_type, colorspace, *_ = map_image_getDefaults(
            context, map, out_container)
        is_data = tex_type in {'DATA', 'LINEAR'}

        self.bake_scene_settings(context, action='SET', data_bake=is_data,
                                 color_manage=color_manage, compositor=True)

        # adding compos nodes in Compositor
        context.scene.use_nodes = True
        nodes = context.scene.node_tree.nodes
        links = context.scene.node_tree.links

        # mute Render Layers nodes to not trigger render from camera
        muted_nodes = []
        # r_layers links to restore
        r_layers_links = []
        # where to link image node (for use_compositor).
        # where image goes
        image_node_image_link_to = []
        # where image alpha goes
        image_node_alpha_link_to = []
        # composite node to set active if use_compositor
        composite_node = None
        for node in nodes:
            if node.type == 'OUTPUT_FILE':
                node.mute = True
                muted_nodes.append(node)

            elif node.type == 'R_LAYERS':
                if use_compositor:
                    for output in node.outputs:
                        if output.name not in {"Image", "Alpha"}:
                            continue

                        for link in output.links:
                            if output.name == "Image":
                                r_layers_links.append([output, link.to_socket])
                                image_node_image_link_to.append(link.to_socket)
                            elif output.name == "Alpha":
                                r_layers_links.append([output, link.to_socket])
                                image_node_alpha_link_to.append(link.to_socket)

                node.mute = True
                muted_nodes.append(node)

            elif node.type == 'COMPOSITE' and not use_compositor:
                if composite_node is None:
                    composite_node = node
                node.mute = True
                muted_nodes.append(node)

        # add image node
        nodes_to_remove = []

        image_node_type = "CompositorNodeImage"

        denoise_node_types = ["CompositorNodeDenoise",
                              "CompositorNodeDespeckle"]

        composite_node_type = "CompositorNodeComposite"

        # add image node. Add denoise and compositor nodes if needed
        new_image_node = nodes.new(image_node_type)
        nodes_to_remove.append(new_image_node)

        new_image_out_socket = new_image_node.outputs[0]
        new_alpha_out_socket = new_image_node.outputs[1]

        if use_denoise:
            denoise_nodes = []
            for denoise_node_type in denoise_node_types:
                new_denoise_node = nodes.new(denoise_node_type)
                denoise_nodes.append(new_denoise_node)
                nodes_to_remove.append(new_denoise_node)

            links.new(new_image_node.outputs[0], denoise_nodes[0].inputs[0])
            links.new(denoise_nodes[0].outputs[0], denoise_nodes[1].inputs[1])

            new_image_out_socket = denoise_nodes[1].outputs[0]

        if not use_compositor:
            new_composite_node = nodes.new(composite_node_type)
            nodes_to_remove.append(new_composite_node)

            links.new(new_image_out_socket, new_composite_node.inputs[0])
            links.new(new_alpha_out_socket, new_composite_node.inputs[1])

            new_composite_node.use_alpha = (
                out_container.out_use_alpha
                and out_alpha_isAllowed(out_container))
            nodes.active = new_composite_node

        else:
            for input_socket in image_node_image_link_to:
                links.new(new_image_out_socket, input_socket)
            for input_socket in image_node_alpha_link_to:
                links.new(new_alpha_out_socket, input_socket)

            if composite_node is not None:
                nodes.active = composite_node
            else:
                for node in nodes:
                    if node.type != 'COMPOSITE':
                        continue
                    nodes.active = node

        self.bake_scene_output_settings(context, 'SET', image, out_container)

        tiles_size = len(image.tiles)

        # post-process tile by tile
        if image.source == 'TILED':
            for _ in range(tiles_size):
                tile = image.tiles[0]
                new_image_node.image = image

                filepath = image.filepath_raw.replace(
                    "<UDIM>", str(tile.number))

                # render and save post-processed image tile
                context.scene.render.filepath = filepath
                bpy.ops.render.render(self.render_op_type, animation=False,
                                      write_still=True, use_viewport=False)

                # remove saved tile
                image.tiles.remove(tile)

        # post-process once
        else:
            # set image node image
            new_image_node.image = image

            # render and save post-processed image tile
            context.scene.render.filepath = image.filepath
            bpy.ops.render.render(self.render_op_type, animation=False,
                                  write_still=True, use_viewport=False)

        # post-processed render is saved to disk, reload original image
        self.image_reload(image, colorspace, tiles_size=tiles_size)

        # remove created nodes
        for node in nodes_to_remove:
            nodes.remove(node)

        # restore Render Layers links
        for link_data in r_layers_links:
            out_socket, input_socket = link_data
            links.new(out_socket, input_socket)

        # unmute muted nodes
        for node in muted_nodes:
            node.mute = False

        self.bake_scene_settings(context, action='RESTORE')
        self.bake_scene_output_settings(context, 'RESTORE')

        # if context.area changed, restore back
        # if image_area.ui_type != old_area_type and old_area_type is not None:
        #     image_area.ui_type = old_area_type

    def bake_image_get_colorspace(_, context, map=None, out_container=None,
                                  tex_type=''):
        # Get image color space. Parameters:
        # tex_type - give texture type directly in {'color', 'data', 'linear'}.

        _, colorspace, *_ = map_image_getDefaults(
            context, map, out_container, tex_type=tex_type)

        return colorspace

    def vdata_set_active(self, vdata, layer) -> None:
        if self._version_current >= (3, 2, 0):
            bpy.ops.geometry.color_attribute_render_set(name=layer.name)
            vdata.active_color = layer
        else:
            layer.active_render = True
            vdata.active = layer

    def v_init_colors(self, layer) -> None:
        l_data = layer.data

        if l_data[-1].color[3] == 0:
            return

        l_data[-1].color[3] = 0

    def v_change_name_in_bake(self, l_name_old: str, l_name: str,
                              shell_index: int) -> None:

        l_old_ad_data = self.bake_images_ad_data[l_name_old]

        self.bake_images[self.bake_object_index][shell_index][
            self.bake_object_map_index] = l_name
        self.bake_images_ad_data[l_name] = l_old_ad_data

    def v_create_from_existing(self, context, vdata, name_init: str,
                               shell_index: int):

        overwrite = context.scene.bm_props.global_use_bake_overwrite

        index = self.v_name_get_index_in_data(
            vdata, name_init, overwrite=overwrite)
        l_name = self.v_name_get_indexed(
            name_init, str(index), vdata, overwrite=overwrite)

        if l_name != name_init:
            self.v_change_name_in_bake(name_init, l_name, shell_index)

        if vdata.find(l_name) != -1:
            layer = vdata[l_name]
            self.v_init_colors(layer)
            return layer

        if self._version_current >= (3, 2, 0):
            layer = vdata.new(name=l_name, domain='POINT', type='FLOAT_COLOR')
        else:
            layer = vdata.new(name=l_name, do_init=True)

        self.v_init_colors(layer)
        return layer

    def mesh_get_vdata(self, mesh):
        if self._version_current >= (3, 2, 0):
            vdata = mesh.color_attributes
        else:
            vdata = mesh.vertex_colors

        return vdata

    def obj_get_vdata(self, obj):
        return self.mesh_get_vdata(obj.data)

    def vdata_get_layer(self, vdata, l_name):
        if vdata.find(l_name) == -1:
            return None

        return vdata[l_name]

    def bake_image_get_or_create_vrtxcolorlayer(self, context, img_name: str,
                                                obj, shell_index: int):
        bpy.ops.object.mode_set(mode='OBJECT')

        vdata = self.obj_get_vdata(obj)

        if vdata.find(img_name) != -1:
            layer = self.v_create_from_existing(
                context, vdata, img_name, shell_index)
            self.vdata_set_active(vdata, layer)
            return layer

        if self._version_current >= (3, 2, 0):
            layer = vdata.new(name=img_name, domain='POINT',
                              type='FLOAT_COLOR')
        else:
            layer = vdata.new(name=img_name, do_init=True)

        self.vdata_set_active(vdata, layer)
        self.v_init_colors(layer)
        return layer

    def bake_image_get_or_create_init_name(self, container, map, image_name,
                                           shell_index):
        # get altered image name on its init

        # prepare data
        # get from format settings
        if container.out_use_unique_per_map:
            out_container = map
        else:
            out_container = container
        # tiled
        tiles_size = self.bake_images_ad_data[image_name]
        tiled = not (tiles_size[0] == 1001 and tiles_size[1] == 1001)
        # file format
        file_formats_data = {
            'PNG': 'png',
            'TIFF': 'tiff',
            'OPEN_EXR': 'exr',
            'CINEON': 'cin',
            'TARGA': 'tga',
            'TARGA_RAW': 'tga',
            'DPX': 'dpx',
            'BMP': 'bmp',
            'JPEG': 'jpg',
            'PSD': 'png',
        }
        file_format = file_formats_data[self.bake_container_get_file_format(
            out_container)]

        if tiled:
            # renaming (for channel pack, denoising)
            # when image is reopened, its name has file format and udim tag
            img_ad_data = self.bake_images_ad_data[image_name]
            name_ending = ".<UDIM>.%s" % file_format
            name = "%s%s" % (image_name, name_ending) if not image_name.endswith(
                name_ending) else image_name
            self.bake_images[self.bake_object_index][shell_index][self.bake_object_map_index] = name
            self.bake_images_ad_data[name] = img_ad_data
            return name

        else:
            # renaming (for channel pack, denoising)
            # when image is reopened, its name has file format and udim tag
            img_ad_data = self.bake_images_ad_data[image_name]
            name_ending = ".%s" % file_format
            name = "%s%s" % (image_name, name_ending) if not image_name.endswith(
                name_ending) else image_name
            self.bake_images[self.bake_object_index][shell_index][self.bake_object_map_index] = name
            self.bake_images_ad_data[name] = img_ad_data
            return name

    def bake_image_get_or_create(self, context, image_name, container, _,
                                 source_object, map, shell_index):
        # get or create self.bake_image
        if self.bake_image_type == 'VERTEX_COLORS':
            return self.bake_image_get_or_create_vrtxcolorlayer(
                context, image_name, source_object, shell_index)

        # create a new image
        # if found in bpy.data.images -> return that image
        try:
            # get properly initialized image_name
            image_name_init = self.bake_image_get_or_create_init_name(
                container, map, image_name, shell_index)
            return bpy.data.images[image_name_init]
        except KeyError:
            pass

        # get from format settings
        if container.out_use_unique_per_map:
            out_container = map
        else:
            out_container = container
        # height, width
        res_enum = out_container.out_res
        if res_enum == 'CUSTOM':
            width = out_container.out_res_width * \
                int(out_container.out_super_sampling_aa)
            height = out_container.out_res_height * \
                int(out_container.out_super_sampling_aa)
        else:
            width = int(out_container.out_res) * \
                int(out_container.out_super_sampling_aa)
            height = int(out_container.out_res) * \
                int(out_container.out_super_sampling_aa)
        # alpha
        alpha = out_container.out_use_alpha and out_alpha_isAllowed(
            out_container)

        # init color
        init_color = (0, 0, 0)
        if alpha and out_container.out_use_transbg:
            color = init_color + (0,)
        else:
            color = init_color + (1,)

        # gen type
        generated_type = 'BLANK'
        # float
        float = out_bit_depth_EvaluateFloat(out_container)
        # tiled
        tiles_size = self.bake_images_ad_data[image_name]
        tiled = not (tiles_size[0] == 1001 and tiles_size[1] == 1001)

        tex_type, colorspace, *_ = map_image_getDefaults(
            context, map, out_container)
        is_data = tex_type in {'DATA', 'LINEAR'}

        # create new image data block
        image = bpy.data.images.new(
            image_name,
            width,
            height,
            alpha=alpha,
            float_buffer=float,
            is_data=is_data,
            tiled=tiled)

        # set alpha mode
        if self.bake_container_get_file_format(out_container) == 'OPEN_EXR':
            image.alpha_mode = 'PREMUL' if alpha else 'NONE'
        else:
            image.alpha_mode = 'STRAIGHT' if alpha else 'NONE'
        # set colorspace profile
        try:
            image.colorspace_settings.name = colorspace
        except TypeError:
            msg = (f"Cannot set '{colorspace}' "
                   + f"color space for {image.name} - unsupported")
            self.report_msg('WARNING', msg, infobar=False)

        # file format
        file_formats_data = {
            'PNG': 'png',
            'TIFF': 'tiff',
            'OPEN_EXR': 'exr',
            'CINEON': 'cin',
            'TARGA': 'tga',
            'TARGA_RAW': 'tga',
            'DPX': 'dpx',
            'BMP': 'bmp',
            'JPEG': 'jpg',
            'PSD': 'png',
        }
        file_format = file_formats_data[self.bake_container_get_file_format(
            out_container)]
        image.file_format = self.bake_container_get_file_format(out_container)

        # filepath

        if container.bake_save_internal:
            filepath = bpy.path.abspath(tempfile.gettempdir())

        elif container.bake_create_subfolder:
            filepath = os.path.join(bpy.path.abspath(
                container.bake_output_filepath), container.bake_subfolder_name)
        else:
            filepath = bpy.path.abspath(container.bake_output_filepath)

        if tiled:
            # renaming (for channel pack, denoising)
            # when image is reopened, its name has file format and udim tag
            img_ad_data = self.bake_images_ad_data[image_name]
            name_ending = ".<UDIM>.%s" % file_format
            image.name = "%s%s" % (image_name, name_ending) if not image.name.endswith(
                name_ending) else image.name
            filepath = os.path.join(filepath, image.name)
            self.bake_images[self.bake_object_index][shell_index][self.bake_object_map_index] = image.name
            self.bake_images_ad_data[image.name] = img_ad_data

        else:
            # renaming (for channel pack, denoising)
            # when image is reopened, its name has file format and udim tag
            img_ad_data = self.bake_images_ad_data[image_name]
            name_ending = ".%s" % file_format
            image.name = "%s%s" % (image_name, name_ending) if not image.name.endswith(
                name_ending) else image.name
            filepath = os.path.join(filepath, image.name)
            self.bake_images[self.bake_object_index][shell_index][self.bake_object_map_index] = image.name
            self.bake_images_ad_data[image.name] = img_ad_data

        # for later saving
        self.bake_images_ad_data[image.name][8] = container.bake_save_internal

        # if container.bake_save_internal:
        #     # Create a temporary file to save bake to.
        #     # Warning: we're responsible for deleting the temp file (in save)
        #     fd = tempfile.NamedTemporaryFile(delete=False)

        #     # change temp file filepath basename to image name
        #     # important for UDIMs images
        #     filepath = fd.name.replace(os.path.basename(fd.name), image.name)
        #     os.rename(fd.name, filepath)
        #     fd.name = filepath

        #     # store for later removal
        #     self.bake_images_ad_data[image.name][8] = [fd, filepath]

        # image.filepath = filepath  # refreshes data
        image.filepath_raw = filepath

        # create tiles
        if tiled:
            image_data = {
                'color': color,
                'generated_type': generated_type,
                'width': width,
                'height': height,
                'float': float,
                'alpha': alpha,
                'start_tile_index': tiles_size[0],
                'end_tile_index': tiles_size[1],
            }
            self.bake_image_create_tiles(context, image, image_data)

        return image

    def bake_image_create_tiles(self, context, image, image_data):
        # create and fill tiles for an image
        color = image_data['color']
        generated_type = image_data['generated_type']
        width = image_data['width']
        height = image_data['height']
        float = image_data['float']
        alpha = image_data['alpha']
        start_tile_index = image_data['start_tile_index']
        end_tile_index = image_data['end_tile_index']

        # context regions: https://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-itemshttps://docs.blender.org/api/current/bpy_types_enum_items/region_type_items.html#rna-enum-region-type-items
        # file_tile poll and ot source code: https://git.blender.org/gitweb/gitweb.cgi/blender.git/blob/HEAD:/source/blender/editors/space_image/image_ops.c
        # 4117 static bool tile_fill_poll(bContext *C)
        # 4118 {
        # 4119   Image *ima = CTX_data_edit_image(C);
        # 4120
        # 4121   if (ima != NULL && ima->source == IMA_SRC_TILED) {
        # 4122     /* Filling secondary tiles is only allowed if the primary tile exists. */
        # 4123     return (ima->active_tile_index == 0) || BKE_image_has_ibuf(ima, NULL);
        # 4124   }
        # 4125   return false;
        # 4126 }
        # headers: https://github.com/martijnberger/blender/blob/master/source/blender/blenkernel/BKE_image.h
        # code: https://github.com/martijnberger/blender/blob/master/source/blender/blenkernel/intern/image.c
        # for testing tile_fill
        # start_tile_index = 1001
        # end_tile_index = 1012

        image_area = None
        image_screen = None
        image_region = None
        old_area_type = None

        # finding image_editor area to exec image OTs
        # for screen in bpy.data.screens:
        #     for area in screen.areas:
        #         if area.ui_type in ['IMAGE_EDITOR', 'UV']:
        #             image_area = area
        #             for region in area.regions:
        #                 print(region.height, region.type)
        #                 if region.type == 'WINDOW':
        #                     image_region = region
        #             # XXX don't know if there's always a WINDOW region
        #             if image_region is None:
        #                 image_region = area.regions[0]
        #             image_screen = screen
        #             break

        # if not found: change context.area ui_type
        if any([image_area is None, image_screen is None]):
            image_screen = context.screen
            for area in image_screen.areas:
                if area is None:
                    continue
                old_area_type = area.ui_type
                area.ui_type = 'UV'
                image_area = area
                for region in image_area.regions:
                    if region.type == 'WINDOW':
                        image_region = region
                        break
                break
            # XXX don't know if there's always a WINDOW region
            if image_region is None:
                image_region = context.area.regions[0]

        # set image_editor active image
        old_active_image = image_area.spaces.active.image
        image_area.spaces.active.image = image

        context_override = context.copy()
        context_override['area'] = image_area
        context_override['screen'] = image_screen
        context_override['region'] = image_region
        print("BakeMaster Info: Creating tiled image %s..." % image.name)

        # filling existing tiles to get the ability to add new ones
        for tile_index, tile in enumerate(image.tiles):
            # (checking channels doesn't suit)
            # if tile is not filled, it has no color channels
            # if tile.channels == 0:
            # (checking channels doesn't suit)
            # setting active tile and filling it
            image.tiles.active_index = tile_index

            if self._version_current >= (3, 2, 0):
                with context.temp_override(**context_override):
                    bpy.ops.image.tile_fill(color=color,
                                            generated_type=generated_type,
                                            width=width,
                                            height=height,
                                            float=float,
                                            alpha=alpha)
            else:
                bpy.ops.image.tile_fill(context_override,
                                        color=color,
                                        generated_type=generated_type,
                                        width=width,
                                        height=height,
                                        float=float,
                                        alpha=alpha)

        # adding tiles of count: udim baking range
        # and filling
        if self._version_current >= (3, 2, 0):
            with context.temp_override(**context_override):
                bpy.ops.image.tile_add(number=start_tile_index,
                                       count=(end_tile_index - start_tile_index
                                              + 1),
                                       label='',
                                       fill=True,
                                       color=color,
                                       generated_type=generated_type,
                                       width=width,
                                       height=height,
                                       float=float,
                                       alpha=alpha)
        else:
            bpy.ops.image.tile_add(context_override,
                                   number=start_tile_index,
                                   count=(end_tile_index - start_tile_index
                                          + 1),
                                   label='',
                                   fill=True,
                                   color=color,
                                   generated_type=generated_type,
                                   width=width,
                                   height=height,
                                   float=float,
                                   alpha=alpha)

        # restore old active image in the image_editor
        if old_active_image is not None:
            image_area.spaces.active.image = old_active_image
        # if context.area changed, restore back
        if image_area.ui_type != old_area_type and old_area_type is not None:
            image_area.ui_type = old_area_type

        # removing tiles that are not in the udim tiles baking range
        for tile_index, tile in enumerate(image.tiles):
            if tile.number not in range(start_tile_index, end_tile_index + 1):
                image.tiles.remove(image.tiles[tile_index])

    def bake_image_prepare(self, context, source_object, container, map, image,
                           type):
        # prepare bake image

        # prepare scene settings
        out_container = container
        if out_container.out_use_unique_per_map:
            out_container = map

        tex_type, *_ = map_image_getDefaults(
            context, map, out_container)
        is_data = tex_type in {'DATA', 'LINEAR'}

        self.bake_scene_settings(context, action='SET', data_bake=is_data)

        context.scene.cycles.device = container.bake_device
        if self._version_current >= (3, 4, 0):
            context.scene.render.bake.view_from = container.bake_view_from
        context.scene.cycles.samples = out_container.out_samples
        context.scene.cycles.use_adaptive_sampling = out_container.out_use_adaptive_sampling
        context.scene.cycles.adaptive_threshold = out_container.out_adaptive_threshold
        context.scene.cycles.adaptive_min_samples = out_container.out_min_samples

        if type == 'VERTEX_COLORS':
            return

        # if IMAGE_TEXTURES, add bm image node to all source_object mats
        if len(source_object.data.materials) == 0:
            new_mat = bpy.data.materials.new(
                name="%s_BM_Custom_Material" % source_object.name)
            source_object.data.materials.append(new_mat)

        for material in source_object.data.materials:
            if material is None:
                continue
            material.use_nodes = True
            nodes = material.node_tree.nodes
            image_node = nodes.new('ShaderNodeTexImage')
            image_node.image = image
            # image_node.label = "BM_TexImage"
            nodes.active = image_node
            self.bake_current_source_object_bm_image_nodes.append(image.name)

    def bake_operate_next_object(self, context, source_highpolies=None):
        # get, set next object data
        self.baking_now = False

        # get old data
        source_object = self.bake_current_source_object

        if source_highpolies is None:
            source_highpolies = self.bake_current_source_highpolies
        if source_highpolies is None:
            materials_source = source_object
        elif len(source_highpolies):
            materials_source = source_highpolies[self.bake_object_map_highpoly_index]
        else:
            materials_source = source_object

        if source_object is not None:
            # restore previous map materials' nodes replug
            self.bake_map_restore_mats_replug(materials_source)
            # handle map previews
            print("BakeMaster Info: Switching off all map previews...")
            self.bake_map_handle_preview(context, None, None, 'UNSET')
            # finish current object
            self.handle_object_finish(context)

        self.bake_object_index += 1
        self.bake_object_map_index = 0
        self.bake_object_map_highpoly_index = 0

        # get object data
        status, container, object, source_object = self.bake_object_get_data(
            context)
        if status == {'DONE'}:
            return status
        # set object data
        self.bake_current_container = container
        self.bake_current_object = object
        self.bake_current_source_object = source_object
        # prepare object
        self.bake_prepare_object(context, container, object, source_object)

        return {'CONTINUE'}

    def bake_scene_settings_colorspace(self, context):
        bm_props = context.scene.bm_props
        display_settings = context.scene.display_settings

        need_colorspace = bm_props.cm_color_space

        try:
            display_settings.display_device = need_colorspace
        except TypeError:
            colorspace_ok = False
        else:
            colorspace_ok = True

        return colorspace_ok, display_settings.display_device, need_colorspace

    def bake_scene_output_settings(self, context, action: str, image=None,
                                   out_container=None, color_mode='',
                                   render_filepath="", ssaa_downscaled=False):
        # manages render output settings only,
        # set color management using bake_scene_settings(...)

        sc = context.scene
        render = sc.render
        image_settings = render.image_settings

        w = sc.world
        w.use_nodes = True

        # try:
        if action == 'SET':
            if image is None or out_container is None:
                raise ValueError(
                    "Expected not NoneType image and out_container")

            if len(self.CMgin_old_settings):
                self.bake_scene_output_settings(context, action='RESTORE')

            self.CMgin_old_settings = [
                render.filepath,
                render.resolution_x,
                render.resolution_y,
                render.film_transparent,

                image_settings.file_format,
                image_settings.color_mode,
                image_settings.color_depth,

                # EXR
                image_settings.exr_codec,
                image_settings.use_preview,

                # PNG
                image_settings.compression,

                # JPEG
                image_settings.quality,

                # DPX
                image_settings.use_cineon_log,

                # TIFF
                image_settings.tiff_codec,
            ]

            if self._version_current >= (3, 2, 0):
                self.CMgin_old_settings.append(
                    image_settings.color_management)

            # context.scene.render.filepath,

            if self._version_current >= (3, 2, 0):
                image_settings.color_management = 'FOLLOW_SCENE'

            # height, width
            res_enum = out_container.out_res
            ssaa_scale_factor = int(out_container.out_super_sampling_aa)

            # out resolution is the chosen res on the last image iteration
            if ssaa_downscaled:
                ssaa_scale_factor = 1

            if res_enum == 'CUSTOM':
                width = out_container.out_res_width * ssaa_scale_factor
                height = out_container.out_res_height * ssaa_scale_factor
            else:
                width = int(out_container.out_res) * ssaa_scale_factor
                height = int(out_container.out_res) * ssaa_scale_factor

            render.resolution_x = width
            render.resolution_y = height

            if render_filepath != '':
                render.filepath = render_filepath

            image_settings.file_format = self.bake_container_get_file_format(
                out_container)

            if color_mode == '':
                if (out_container.out_use_alpha
                        and out_alpha_isAllowed(out_container)):
                    color_mode = 'RGBA'
                    render.film_transparent = True
                else:
                    color_mode = 'RGB'
                    render.film_transparent = False
            try:
                image_settings.color_mode = color_mode
            except TypeError:
                image_settings.color_mode = 'RGB'

            color_depth = out_container.out_bit_depth
            try:
                image_settings.color_depth = color_depth
            except TypeError:
                pass

            # EXR
            image_settings.exr_codec = out_container.out_exr_codec
            image_settings.use_preview = False

            # PNG
            image_settings.compression = out_container.out_compression

            # JPEG
            image_settings.quality = out_container.out_quality

            # DPX
            image_settings.use_cineon_log = out_container.out_dpx_use_log

            # TIFF
            image_settings.tiff_codec = out_container.out_tiff_compression

            # reset world surface color
            w_nodes = w.node_tree.nodes
            for w_node in w_nodes:
                if w_node is None or w_node.type != 'OUTPUT_WORLD':
                    continue
                for input in w_node.inputs:
                    if len(input.links) == 0:
                        continue
                    for link in input.links:
                        if link.from_node.mute:
                            continue
                        link.from_node.mute = True
                        self.w_muted_nodes.add(link.from_node)

        # restore for individual map
        elif action == 'RESTORE' and len(self.CMgin_old_settings) != 0:
            render.filepath = self.CMgin_old_settings[0]
            render.resolution_x = self.CMgin_old_settings[1]
            render.resolution_y = self.CMgin_old_settings[2]
            render.film_transparent = self.CMgin_old_settings[3]

            image_settings.file_format = self.CMgin_old_settings[4]
            image_settings.color_mode = self.CMgin_old_settings[5]
            image_settings.color_depth = self.CMgin_old_settings[6]

            # EXR
            image_settings.exr_codec = self.CMgin_old_settings[7]
            image_settings.use_preview = self.CMgin_old_settings[8]

            # PNG
            image_settings.compression = self.CMgin_old_settings[9]

            # JPEG
            image_settings.quality = self.CMgin_old_settings[10]

            # DPX
            image_settings.use_cineon_log = self.CMgin_old_settings[11]

            # TIFF
            image_settings.tiff_codec = self.CMgin_old_settings[12]

            if self._version_current >= (3, 2, 0):
                image_settings.color_management = self.CMgin_old_settings[13]

            for w_node in self.w_muted_nodes:
                w_node.mute = False
            self.w_muted_nodes.clear()

        # except (IndexError, KeyError, TypeError, AttributeError,
        #         ValueError) as error:
        #     print(("BakeMaster Error: Write/restore output settings failed "
        #            + "due to: %s" % error))

    def bake_scene_settings(self, context, action: str, data_bake=False,
                            color_manage=False, compositor=False):
        bm_props = context.scene.bm_props
        bake_colorspace = bm_props.cm_color_space
        vt = ""

        if data_bake:
            vt = "Raw"
        else:
            if bake_colorspace == 'ACES':
                vt = "sRGB"
            elif bake_colorspace in {'sRGB', 'XYZ', 'Display P3'}:
                vt = "Standard"

        # try:
        # write scene settings
        if action == 'SET':
            if len(self.Cgin_old_settings):
                self.bake_scene_settings(context, action='RESTORE')

            self.Cgin_old_settings = [
                context.scene.cycles.device,

                context.scene.cycles.samples,
                context.scene.cycles.use_adaptive_sampling,
                context.scene.cycles.adaptive_threshold,
                context.scene.cycles.adaptive_min_samples,

                context.scene.display_settings.display_device,
                context.scene.view_settings.view_transform,
                context.scene.view_settings.look,
                context.scene.view_settings.exposure,
                context.scene.view_settings.gamma,
                context.scene.sequencer_colorspace_settings.name,
                context.scene.view_settings.use_curve_mapping,

                context.view_layer.use,

                context.scene.render.resolution_x,
                context.scene.render.resolution_y,
                context.scene.render.resolution_percentage,
                context.scene.render.pixel_aspect_x,
                context.scene.render.pixel_aspect_y,
                context.scene.render.use_multiview,
                context.scene.render.use_compositing,
                context.scene.render.use_sequencer,
                context.scene.render.dither_intensity,
                context.scene.render.filepath,
                context.scene.render.image_settings.file_format,
                context.scene.render.image_settings.color_mode,
                context.scene.render.image_settings.color_depth,
                context.scene.render.image_settings.compression,
                context.scene.render.image_settings.quality
            ]

            if self._version_current >= (2, 90, 0):
                self.Cgin_old_settings.append(
                    context.scene.cycles.use_denoising)

            if self._version_current >= (3, 2, 0):
                self.Cgin_old_settings.append(
                    context.scene.render.image_settings.color_management)

            if self._version_current >= (3, 4, 0):
                self.Cgin_old_settings.append(
                    context.scene.render.bake.view_from)

            # context.scene.cycles.device,

            # context.scene.cycles.samples,
            # context.scene.cycles.use_adaptive_sampling,
            # context.scene.cycles.adaptive_threshold,
            # context.scene.cycles.adaptive_min_samples,
            if self._version_current >= (2, 90, 0):
                context.scene.cycles.use_denoising = False  # speed up bake

            # context.scene.display_settings.display_device,
            # context.scene.view_settings.view_transform,
            # context.scene.view_settings.look,
            # context.scene.view_settings.exposure,
            # context.scene.view_settings.gamma,
            # context.scene.sequencer_colorspace_settings.name,
            # context.scene.view_settings.use_curve_mapping,

            # context.view_layer.use,

            # context.scene.render.resolution_x,
            # context.scene.render.resolution_y,
            context.scene.render.resolution_percentage = 100
            context.scene.render.pixel_aspect_x = 1.0
            context.scene.render.pixel_aspect_y = 1.0
            context.scene.render.use_multiview = False
            context.scene.render.use_compositing = compositor
            context.scene.render.use_sequencer = False
            context.scene.render.dither_intensity = 1.0

            # context.scene.render.filepath,
            # context.scene.render.image_settings.file_format,
            # context.scene.render.image_settings.color_mode,
            # context.scene.render.image_settings.color_depth,
            # context.scene.render.image_settings.compression,
            # context.scene.render.image_settings.quality

            if self._version_current >= (3, 4, 0):
                context.scene.render.bake.view_from = 'ABOVE_SURFACE'

            # turn off render color management
            # (for denoise, channel pack, decal)
            if self._version_current >= (3, 2, 0):
                context.scene.render.image_settings.color_management = 'FOLLOW_SCENE'

            # if not color_manage or data_bake:
            #     pass
            #     try:
            #         context.scene.view_settings.view_transform = vt
            #     except TypeError:
            #         pass

            #     context.scene.view_settings.look = 'None'
            #     context.scene.view_settings.exposure = 0.0
            #     context.scene.view_settings.gamma = 1.0
            #     context.scene.sequencer_colorspace_settings.name #  for video editing
            #     context.scene.view_settings.use_curve_mapping = False

        # restore for individual map
        elif action == 'RESTORE' and len(self.Cgin_old_settings) != 0:
            context.scene.cycles.device = self.Cgin_old_settings[0]

            context.scene.cycles.samples = self.Cgin_old_settings[1]
            context.scene.cycles.use_adaptive_sampling = self.Cgin_old_settings[2]
            context.scene.cycles.adaptive_threshold = self.Cgin_old_settings[3]
            context.scene.cycles.adaptive_min_samples = self.Cgin_old_settings[4]

            context.scene.display_settings.display_device = self.Cgin_old_settings[5]
            context.scene.view_settings.view_transform = self.Cgin_old_settings[6]
            context.scene.view_settings.look = self.Cgin_old_settings[7]
            context.scene.view_settings.exposure = self.Cgin_old_settings[8]
            context.scene.view_settings.gamma = self.Cgin_old_settings[9]
            context.scene.sequencer_colorspace_settings.name = self.Cgin_old_settings[10]
            context.scene.view_settings.use_curve_mapping = self.Cgin_old_settings[11]

            context.view_layer.use = self.Cgin_old_settings[12]

            context.scene.render.resolution_x = self.Cgin_old_settings[13]
            context.scene.render.resolution_y = self.Cgin_old_settings[14]
            context.scene.render.resolution_percentage = self.Cgin_old_settings[15]
            context.scene.render.pixel_aspect_x = self.Cgin_old_settings[16]
            context.scene.render.pixel_aspect_y = self.Cgin_old_settings[17]
            context.scene.render.use_multiview = self.Cgin_old_settings[18]
            context.scene.render.use_compositing = self.Cgin_old_settings[19]
            context.scene.render.use_sequencer = self.Cgin_old_settings[20]
            context.scene.render.dither_intensity = self.Cgin_old_settings[21]
            context.scene.render.filepath = self.Cgin_old_settings[22]
            context.scene.render.image_settings.file_format = self.Cgin_old_settings[23]
            context.scene.render.image_settings.color_mode = self.Cgin_old_settings[24]
            context.scene.render.image_settings.color_depth = self.Cgin_old_settings[25]
            context.scene.render.image_settings.compression = self.Cgin_old_settings[26]
            context.scene.render.image_settings.quality = self.Cgin_old_settings[27]

            if self._version_current >= (2, 90, 0):
                context.scene.cycles.use_denoising = self.Cgin_old_settings[28]

            if self._version_current >= (3, 2, 0):
                context.scene.render.image_settings.color_management = self.Cgin_old_settings[
                    29]

            if self._version_current >= (3, 4, 0):
                context.scene.render.bake.view_from = self.Cgin_old_settings[30]

        # except (IndexError, KeyError, TypeError, AttributeError,
        #         ValueError) as error:
        #     print(("BakeMaster Error: Write/restore scene settings failed "
        #            + "due to: %s" % error))

    def bake_scene_objects_hide(self, context, action: str, to_hide=[]):
        # hide
        if action == 'HIDE':
            self.hidden_objects_names = []

            for ob in context.scene.objects:
                if ob.visible_get() is False and ob.hide_render is False:
                    ob.hide_render = True
                    self.hidden_objects_names.append(ob.name)

            bm_objects = []
            bm_objects_not_baked = []
            uni_c_master_index = 0
            for index, object in enumerate(context.scene.bm_table_of_objects):
                if object.nm_is_local_container:
                    continue
                if object.nm_is_universal_container:
                    uni_c_master_index = index
                    continue
                bm_objects.append(object.global_object_name)
                uni_c = context.scene.bm_table_of_objects[uni_c_master_index]
                if object.global_use_bake is False or (uni_c.global_use_bake is False and object.nm_item_uni_container_master_index == uni_c.nm_master_index):
                    bm_objects_not_baked.append(object.global_object_name)

            # hide not baked
            if context.scene.bm_props.global_use_hide_notbaked:
                for ob in context.scene.objects:
                    if ob.name not in bm_objects:
                        ob.hide_render = True
                        self.hidden_objects_names.append(ob.name)
            # hide with global_use_bake False
            for ob in context.scene.objects:
                if ob.name in bm_objects_not_baked:
                    ob.hide_render = True
                    self.hidden_objects_names.append(ob.name)

        # hide custom specified objects
        elif action == 'CUSTOM_HIDE':
            for ob in to_hide:
                ob.hide_render = True
                self.hidden_custom_objects_names.append(ob.name)

        # unhide hidden
        elif action == 'UNHIDE':
            for ob_name in self.hidden_objects_names:
                obj = self.object_get(context, ob_name)
                if obj is None:
                    continue
                obj.hide_render = False
            self.hidden_objects_names = []

        # unhide custom hidden
        elif action == 'CUSTOM_UNHIDE':
            for ob_name in self.hidden_custom_objects_names:
                obj = self.object_get(context, ob_name)
                if obj is None:
                    continue
                obj.hide_render = False
            self.hidden_custom_objects_names = []

    def bake_scene_objects_unselect(self, context):
        for ob in context.scene.objects:
            ob.select_set(False)

    def bake_scene_object_get_and_setactive(self, context, object_name):
        source_object = context.scene.objects[object_name]
        self.bake_scene_objects_unselect(context)
        source_object.hide_set(False)
        source_object.select_set(True)
        context.view_layer.objects.active = source_object
        return source_object

    def bake_scene_object_get_and_select(self, context, object_name):
        source_object = context.scene.objects[object_name]
        source_object.select_set(True)
        context.view_layer.objects.active = source_object
        return source_object

    def bake_object_auto_unwrap(self, _, source_object, angle_limit=66,
                                island_margin=0.01, scale_to_bounds=True):
        # smart_project auto adds uv_layer if there is no
        print("BakeMaster Info: Auto UV Unwrapping %s..." % source_object.name)
        # supported between 2.83-3.0, otherwise default smart_project
        if self._version_current >= (2, 91, 0):
            bpy.ops.uv.smart_project(angle_limit=math.radians(angle_limit),
                                     island_margin=island_margin,
                                     area_weight=0,
                                     correct_aspect=True,
                                     scale_to_bounds=scale_to_bounds)
        elif self._version_current >= (2, 83, 0):
            bpy.ops.uv.smart_project(angle_limit=angle_limit,
                                     island_margin=island_margin,
                                     user_area_weight=0,
                                     use_aspect=True,
                                     stretch_to_bounds=scale_to_bounds)
        else:
            bpy.ops.uv.smart_project()

    def obj_mods_add_triangulate(self, obj: bpy.types.Object,
                                 apply: bool = False) -> None:
        assert isinstance(obj, bpy.types.Object)

        mods = obj.modifiers

        if len([i for i in range(len(mods)) if mods[i].type == 'TRIANGULATE']):
            print("BakeMaster Info: Skipped adding Triangulate Modifier for "
                  + "%s - existing found." % obj.name)
            return

        print("BakeMaster Info: Adding Triangulate Modifier for %s..." %
              obj.name)

        mod = mods.new("bm_modifier_triangulate", 'TRIANGULATE')
        mods["bm_modifier_triangulate"].quad_method = 'FIXED'
        mods["bm_modifier_triangulate"].keep_custom_normals = True

        if not apply:
            return

        print("BakeMaster Info: Applying Triangulate modifier for %s..."
              % obj.name)

        try:
            bpy.ops.object.modifier_apply('INVOKE_DEFAULT', modifier=mod.name)
        except RuntimeError as error:
            print("BakeMaster Error: Cannot apply Triangulate modifier for "
                  + "%s due to %s" % (obj.name, str(error)))
            obj.modifiers.remove(mod)

    def bake_object_triangulate_modifier(self, ctx: bpy.types.Context, bm_obj,
                                         source_object: bpy.types.Object):
        self.obj_mods_add_triangulate(source_object)

        if not (bm_obj.hl_use_cage and bm_obj.hl_cage != 'NONE'):
            return

        cage_obj = self.bake_scene_object_get_and_setactive(
            ctx, bm_obj.hl_cage_name_old)
        if cage_obj is None:
            print("BakeMaster Error: Could not add  Triangulate Modifier for "
                  + "%s - Cage object not found" % bm_obj.hl_cage)
            return

        # Invoking Bake from BakeMaster results in error when Lowpoly and Cage
        # have triangulate modifiers. Bake succeeds if triangulate modifier is
        # applied for Cage. Note that there won't be any error on consequent
        # bakes with triangulate modifier applied for Cage only, because since
        # Cage is already triangulated, any additional triangulate modifiers
        # won't effect it.
        assert isinstance(cage_obj, bpy.types.Object)
        self.obj_mods_add_triangulate(cage_obj, apply=True)

    def bake_object_mesh_recalc_normals(self):
        # reset mesh normals
        # bpy.ops.mesh.normals_tools(mode='RESET')
        # recalculate outside
        bpy.ops.mesh.normals_make_consistent(inside=False)

    def bake_object_mesh_smooth(self, source_object, smooth_type, angle,
                                name_contains):
        # smooth normals
        bpy.ops.mesh.faces_shade_flat()
        if smooth_type == 'STANDARD':
            return True
        elif smooth_type == 'AUTO':
            source_object.data.use_auto_smooth = True
            if self._version_current >= (2, 91, 0):
                angle = math.radians(angle)
            source_object.data.auto_smooth_angle = angle
        elif smooth_type == 'VERTEX_GROUPS':
            for vrtx_group_index, vrtx_group in enumerate(
                    source_object.vertex_groups):
                if vrtx_group.name.find(name_contains) == -1:
                    continue
                bpy.ops.mesh.select_all(action='DESELECT')
                source_object.vertex_groups.active_index = vrtx_group_index
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.faces_shade_smooth()
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.mark_sharp()
        return False

    def bake_object_operate_highpoly_smoothing(self, context, container, highpoly, run_csh_recalc_normals_highpoly, run_csh_smooth_highpoly):
        if highpoly.global_highpoly_object_index == -1:
            return
        if self.object_get(context, highpoly.global_object_name) is None:
            return
        bpy.ops.object.mode_set(mode='OBJECT')
        source_highpoly = self.bake_scene_object_get_and_setactive(
            context, highpoly.global_object_name)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        # smooth highpoly
        if run_csh_recalc_normals_highpoly:
            self.bake_object_mesh_recalc_normals()

        if run_csh_smooth_highpoly:
            smooth_type = container.csh_highpoly_smoothing_groups_enum
            angle = container.csh_highpoly_smoothing_groups_angle
            name_contains = container.csh_highpoly_smoothing_groups_name_contains
            smooth_shade = self.bake_object_mesh_smooth(
                source_highpoly, smooth_type, angle, name_contains)
            if smooth_shade:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')

    def bake_map_remove_highpoly_multires(self, source_object):
        # remove multires added for highpoly
        if self.bake_object_disp_remove_multires and self.bake_object_disp_multires is not None:
            print("BakeMaster Info: Removing Multires Modifier from %s..." %
                  source_object.name)
            source_object.modifiers.remove(self.bake_object_disp_multires)
            self.bake_object_disp_remove_multires = False
            self.bake_object_disp_multires = None

    def bake_map_restore_object_multires(self, source_object):
        for index, mod in enumerate(source_object.modifiers):
            show = self.bake_object_mods_show.get(index, None)
            if show is not None:
                mod.show_viewport = show

            if all([index == 0, mod.type == 'MULTIRES',
                    self.bake_object_disp_multires_levels != -1]):
                mod.levels = self.bake_object_disp_multires_levels

        self.bake_object_disp_multires_levels = -1
        self.bake_object_mods_show.clear()

    def bake_map_prepare_highpoly_multires(self, map, source_object,
                                           source_highpoly):
        if not all([map.global_map_type == 'DISPLACEMENT',
                    map.map_displacement_data == 'HIGHPOLY',
                    source_highpoly is not None]):
            return

        # applying all modifiers
        for mod in source_object.modifiers:
            print("BakeMaster Info: Applying %s's %s Modifier..." %
                  (source_object.name, mod.name))
            try:
                bpy.ops.object.modifier_apply(
                    'INVOKE_DEFAULT', modifier=mod.name)
            except RuntimeError:
                print("BakeMaster Info: Error with Applying, Removing %s's %s Modifier..." % (
                    source_object.name, mod.name))
                source_object.modifiers.remove(mod)

        # adding multires
        print("BakeMaster Info: Adding Multires Modifier for %s..." %
              source_object.name)
        mod_multires_name = "BakeMaster Displacement Multires"
        mod_multires = source_object.modifiers.new(
            name=mod_multires_name, type='MULTIRES')

        # configure multires subdiv levels
        for i in range(map.map_displacement_subdiv_levels):
            print("BakeMaster Info: %s Multires Modifier: subdiving for the %d time..." % (
                source_object.name, i + 1))
            bpy.ops.object.multires_subdivide(modifier=mod_multires_name)
        mod_multires.render_levels = map.map_displacement_subdiv_levels

        # adding shrinkwrap
        print("BakeMaster Info: Adding Shrinkwrap Modifier for %s..." %
              source_object.name)
        mod_shrink_name = "BakeMaster Displacement Shrinkwrap"
        mod_shrink = source_object.modifiers.new(
            name=mod_shrink_name, type='SHRINKWRAP')
        mod_shrink.target = source_highpoly
        mod_shrink.wrap_method = 'PROJECT'
        mod_shrink.use_positive_direction = True
        mod_shrink.use_negative_direction = True

        print("BakeMaster Info: Applying Shrinkwrap Modifier for %s..." %
              source_object.name)
        if self._version_current >= (2, 90, 0):
            bpy.ops.object.modifier_apply(modifier=mod_shrink_name)
        else:
            bpy.ops.object.modifier_apply(
                apply_as='DATA', modifier=mod_shrink_name)

        print("BakeMaster Info: %s Multires Modifier: Setting Subdiv Levels to 1..." %
              source_object.name)
        mod_multires.levels = 0

        # remove multires mod after disp bake
        self.bake_object_disp_remove_multires = True
        self.bake_object_disp_multires = mod_multires

    def bake_object_materials_handle_replug(
            self, item, bake_args_22, required=None, take_parent_of_input=None,
            defaults=None, node_type=None, replug_order=None,
            replug_node_type=None, restore=None):
        # item                  -> current item with material data
        # bake_args_22          -> given args to restore material based of
        # required              -> node input indexes to unplug
        # take_parent_of_input  -> inputs[index] socket of the node that is plugged into required[index] socket node:
        #                          currently, only one occasion with this arg is used:
        #                          when baking displacement from material, we find mat_output node, store it's displacement input,
        #                          then, as take_parent_of_input = 0, in replug, we will use this [displacement node inputs[0] link]
        #                          to plug it into emission node
        # defaults              -> values to set for unplugged inputs
        # node_type             -> node type where to get and set inputs
        # replug_order          -> array where: socket_index input from array[0] to be plugged into socket_index input of array[1]
        #                          if array 2, 3 given, socket_index input from array[1] to be plugged into socket_index input of array[2]
        #                          socket_index output from array[2] to be plugged into socket_index input of array[3]
        #                          with array 2, 3 given, one more restore will be added to restore previous connections plugget into array[3]
        # replug_node_type      -> if 'SAME' - replugging will be made withing the same node, else - replug into new node of this type
        # restore               -> Bool: if True - restore material, if False - set args

        # reseting (item, required, defaults)
        if restore is not True:
            bake_args_22 = []

            mat_index = -1
            for mat in item.data.materials:
                if mat is None:
                    continue

                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                # as longs as we add only mats with bsdf, this is a check for mat index increase
                has_mat_instance = False
                node_index = 1
                # structre: [['BakeMaster_PreFinal_Material_For_Test',    -> in each mat with bsdf
                #           ['Principled BSDF',                          -> store bsdf node name
                #           [4, None, bpy.data.materials['BakeMaster_PreFinal_Material_For_Test'].node_tree.nodes["Map Range"].outputs[0]],
                #           [17, [0.14571306109428406, 0.015956589952111244, 0.5697985887527466, 1.0], None]    -> write value or input node
                #           ]
                #           ]]
                # [    [mat_name,   [bsdf_node_name,  [socket_index, value, input_node]  ]   ]    ]
                for node in nodes:
                    if node.type == node_type:

                        if not has_mat_instance:
                            bake_args_22.append([mat.name])
                            mat_index += 1
                            has_mat_instance = True

                        bake_args_22[mat_index].append([node.name])

                        for req, default in zip(required, defaults):
                            input_value = None
                            input_node = None

                            if len(node.inputs[req].links):
                                link = node.inputs[req].links[0]
                                input_node = link.from_socket
                                links.remove(link)

                            else:
                                # 3.0 brings sss ior and anitrosopy -> all sockets with index > 3 are moved 2 downwards
                                socket_inc_300 = 2 if self._version_current >= (
                                    3, 0, 0) else 0

                                # WARNING
                                # This use case is no longer reached,
                                # and not adapted to Blender >=4.0.
                                if req == 17 + socket_inc_300:
                                    input_value = list(
                                        node.inputs[req].default_value)

                                elif node_type != 'OUTPUT_MATERIAL':  # do not store value for Output Material
                                    input_value = node.inputs[req].default_value

                            if default is not None:
                                node.inputs[req].default_value = default

                            bake_args_22[mat_index][node_index].append(
                                [req, input_value, input_node])

                        # replugging
                        if replug_order is not None:
                            replug_from = None
                            value_node = None

                            for input_holder_index in range(1, len(bake_args_22[mat_index][node_index])):
                                input_holder = bake_args_22[mat_index][node_index][input_holder_index]

                                if input_holder[0] == replug_order[0]:

                                    if input_holder[1] is None and input_holder[2] is not None:
                                        replug_from = input_holder[2]

                                    elif input_holder[1] is not None:
                                        value_node = nodes.new(
                                            'ShaderNodeValue')
                                        value_node.name = 'BM_PBR_VALUE_NODE_VALUE'
                                        value_node.outputs[0].default_value = input_holder[1]
                                        replug_from = value_node.outputs[0]

                            if replug_node_type == 'SAME' and replug_from is not None:
                                links.new(
                                    replug_from, node.inputs[replug_order[1]])

                            elif replug_from is not None:  # black screen if there was no input
                                replug_node = nodes.new(replug_node_type)
                                replug_node.name = 'BM_PBR_VALUE_NODE_VALUE.001'

                                # here we need to reassign replug_from node to be not disp node output,
                                # but the node that is plugged into its input socket[index] of index take_parent_of_input
                                if take_parent_of_input is not None:
                                    parent_links = replug_from.node.inputs[take_parent_of_input].links
                                    # as long as disp height allows one link
                                    # syntax: replug_from was node output, we take .node class as it refers to the node itself,
                                    # then with the specified input, picking up socket from which the link outputs
                                    if len(parent_links):
                                        replug_from = parent_links[0].from_socket

                                # no checking for previous links in replug_array[3] to add to the restore:
                                # currently there is only a single occassion like this, so we know that
                                # it is Material Output and there is only one link and only one possible.
                                # we added it in required function argument so its links will be restored
                                links.new(
                                    replug_from, replug_node.inputs[replug_order[1]])
                                links.new(
                                    replug_node.outputs[replug_order[2]], node.inputs[replug_order[3]])

                        node_index += 1  # bsdf node index in args array

        # restoring (bake_args_22)
        elif restore is True and bake_args_22 is not None:

            for mat_holder in bake_args_22:

                try:
                    mat = item.data.materials[mat_holder[0]]
                except KeyError:
                    continue

                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                for node_holder_index in range(1, len(mat_holder)):
                    node_holder = mat_holder[node_holder_index]
                    node_name = node_holder[0]

                    for input_holder_index in range(1, len(node_holder)):
                        input_holder = node_holder[input_holder_index]

                        bsdf_input_index = input_holder[0]
                        input_value = input_holder[1]
                        input_node = input_holder[2]

                        if input_value is not None:
                            # if added link in bake_object_materials_handle_replug, remove it
                            r_links = nodes[node_name].inputs[bsdf_input_index].links
                            if len(r_links):
                                links.remove(r_links[0])
                            # restore value
                            nodes[node_name].inputs[bsdf_input_index].default_value = input_value

                        elif input_node is not None:
                            links.new(
                                input_node, nodes[node_name].inputs[bsdf_input_index])

                for node in nodes:
                    if node.name.find('BM_PBR_VALUE_NODE_VALUE') != -1:
                        nodes.remove(node)

        # Call examples (for Blender v2.83)
        # bake_object_materials_handle_replug

        # Albedo -> unplug metallic
        # bake_args_22_g = get_bake_args_22(item, None, [4], None, [0], 'BSDF_PRINCIPLED', None, None, False)  # set
        # _ = get_bake_args_22(item, bake_args_22_g, restore=True)  # restore

        # Metalness -> plug metallic into emission
        # bake_args_22_g = get_bake_args_22(item, None, [4, 17], None, [0.0, [0, 0, 0, 1]], 'BSDF_PRINCIPLED', [4, 17], 'SAME', False)  # set
        # _ = get_bake_args_22(item, bake_args_22_g, restore=True)  # restore

        # Opacity -> plug opacity into emission
        # version < 2.91: opac_socket = 18, else: opac_socket = 19
        # bake_args_22_g = get_bake_args_22(item, None, [17, opac_socket], None, [[0, 0, 0, 1], 1.0], 'BSDF_PRINCIPLED', [opac_socket, 17], 'SAME', False)  # set
        # _ = get_bake_args_22(item, bake_args_22_g, restore=True)  # restore

        # Displacement -> plug disp output into emission shader
        # bake_args_22_g = get_bake_args_22(item, None, [2, 0], 0, [None, None], 'OUTPUT_MATERIAL', [2, 0, 0, 0], 'ShaderNodeEmission', False)  # set
        # _ = get_bake_args_22(item, bake_args_22_g, restore=True)  # restore

        return bake_args_22

    def bake_map_handle_preview(self, context, map, object, action='SET'):
        # handle map previews toggling

        # unset always
        BM_MAP_PROPS_MapPreview_Unset(map, context)
        # and just return if action is UNSET
        if action == 'UNSET':
            return

        if object.decal_is_decal:
            no_preview = [
                # 'ALBEDO',
                # 'METALNESS',
                # 'ROUGHNESS',
                # 'OPACITY',
                # 'EMISSION',
                # 'NORMAL',
                'C_COMBINED',
                'C_AO',
                'C_SHADOW',
                'C_NORMAL',
                'C_UV',
                'C_ROUGNESS',
                'C_EMIT',
                'C_ENVIRONMENT',
                'C_DIFFUSE',
                'C_GLOSSY',
                'C_TRANSMISSION',
            ]

        else:
            no_preview = [
                'ALBEDO',
                # 'METALNESS',
                'ROUGHNESS',
                # 'OPACITY',
                'EMISSION',
                'NORMAL',
                'C_COMBINED',
                'C_AO',
                'C_SHADOW',
                'C_NORMAL',
                'C_UV',
                'C_ROUGNESS',
                'C_EMIT',
                'C_ENVIRONMENT',
                'C_DIFFUSE',
                'C_GLOSSY',
                'C_TRANSMISSION',
            ]

        if map.global_map_type in no_preview:
            return

        if map.global_map_type == 'DISPLACEMENT' and map.map_displacement_data != 'MATERIAL':
            return
        if map.global_map_type != 'ID':
            setattr(map, "map_%s_use_preview" % map.global_map_type, True)
            return

        # if matid map, switch to rendered view
        shading_types_restore = []
        for area in context.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for space in area.spaces:
                if space.type != 'VIEW_3D':
                    continue
                shading_types_restore.append(space.shading.type)
                space.shading.type = 'RENDERED'
        # turn on preview,
        setattr(map, "map_ID_use_preview", True)
        # switch back to the mode where was
        index = 0
        for area in context.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for space in area.spaces:
                if space.type != 'VIEW_3D':
                    continue
                space.shading.type = shading_types_restore[index]
                index += 1

    def bake_object_uv_layer_snap_to_pixels(self, source_object, uv_layer,
                                            res_x, res_y):
        # snap uv layer vertices to pixels of given res
        # (dev) debug .prefs/snap_uv_to_pixels.py to see how this works
        # time complexity is O(n) where n is number of loops

        # NOTE
        # snap to pixels' centers can be implemented

        # can snap onto pixel's edges aka pixel_step values
        # defined for both res, because uv coordinates are always
        # from 0 to 1 no matter the image aspect
        try:
            pixel_step_x = 1 / res_x
            pixel_step_y = 1 / res_y
            # change all uv coordinates
            for loop_index, _ in enumerate(source_object.data.loops):
                bpy.ops.object.mode_set(mode='OBJECT')
                uv_coords = uv_layer.data[loop_index].uv
                x = uv_coords[0]
                y = uv_coords[1]
                # skip if already enligned with pixel edges
                if (x % pixel_step_x) + (y % pixel_step_y) == 0:
                    continue

                # clean x, y are only the float part of the number
                x_clean = x
                y_clean = y
                if int(x) != 0:
                    x_clean %= int(x)
                if int(y) != 0:
                    x_clean %= int(y)

                # how far to the start and end of the pixel
                x_to_pixel_start = -(x_clean % pixel_step_x)
                d_x = {
                    'to_pixel_start': x_to_pixel_start,
                    # 'to_pixel_middle' : (pixel_step_x / 2) - x_to_pixel_start
                    'to_pixel_end': pixel_step_x - x_to_pixel_start,
                }
                y_to_pixel_start = -(y_clean % pixel_step_y)
                d_y = {
                    'to_pixel_start': y_to_pixel_start,
                    # 'to_pixel_middle' : (pixel_step_y / 2) - y_to_pixel_start
                    'to_pixel_end': pixel_step_y - y_to_pixel_start,
                }

                # get the change x, y values based on the shortest distance to
                # the pixel edge
                min_d_x = min(abs(d_x[key]) for key in d_x)
                change_x = [value for value in list(
                    d_x.values()) if abs(value) == min_d_x][0]
                min_d_y = min(abs(d_y[key]) for key in d_y)
                change_y = [value for value in list(
                    d_y.values()) if abs(value) == min_d_y][0]

                uv_layer.data[loop_index].uv = (x + change_x, y + change_y)

        except (IndexError, RuntimeError, ValueError, KeyError) as error:
            print("BakeMaster Error: Could not snap %s UV Map to pixels due to %s" % (
                uv_layer.name, error))

    def bake_object_get_udim_tiles_indexes(self, out_container, source_object,
                                           uv_layer, uv_type):
        # set udim tiles start and end indexes
        if uv_type == 'SINGLE':
            return 1001, 1001
        if uv_type == 'TILED':
            return out_container.out_udim_start_tile, out_container.out_udim_end_tile
        uv_layer = source_object.data.uv_layers[uv_layer]

        # (dev) debug .prefs/udims_get_automatic_start_end_tile_indexes.py
        # to see how this algo works
        # time complexity is O(n*2), where n is number of loops

        # initialize uv_layer vertices max y coordinate
        max_y = tuple(uv_layer.data[0].uv)[1]
        # find max y
        for loop_index, _ in enumerate(source_object.data.loops):
            uv_coords = uv_layer.data[loop_index].uv
            y = tuple(uv_coords)[1]
            if y < 0:
                continue
            if y > max_y:
                max_y = y
        # set to 0 if uv island y is outside of regular area
        if max_y < 0:
            max_y = 0
        # if vertex y value lies onto tile edge,
        # tile index should be decreased
        # for ex, if y = 1, tile_y should be 0 instead of 1
        if max_y % 1 == 0 and max_y >= 1:
            tile_y = int(max_y) - 1
        else:
            tile_y = int(max_y)

        # initialize uv_layer vertices max x coordinate
        max_x = tuple(uv_layer.data[0].uv)[0]
        # find max x
        for loop_index, _ in enumerate(source_object.data.loops):
            uv_coords = uv_layer.data[loop_index].uv
            x = tuple(uv_coords)[0]
            if x < 0:
                continue
            y = tuple(uv_coords)[1]
            # same can be decreased
            found_tile_y = int(y) - 1 if y % 1 == 0 and y >= 1 else int(y)
            # find max x within the max found tile_y
            if found_tile_y != tile_y:
                continue
            elif x > max_x:
                max_x = x
        # set to 0 if uv island x is outside of regular area
        if max_x < 0:
            max_y = 0
            max_x = 0
        # same can be decreased
        if max_x % 1 == 0 and max_x >= 1:
            tile_x = int(max_x) - 1
        else:
            tile_x = int(max_x)
        # clip tile_x to blender's max 10 tiles in one row
        if tile_x > 9:
            tile_x = 9

        # calculate how many tiles are used
        number = 0
        if tile_y > 0:
            number = tile_y * 10
        number += tile_x + 1

        # calculate start, end tiles' indexes
        start = 1001
        end = 1000 + number

        return start, end

    def v_name_get_indexed(self, name: str, index: str, vdata,
                           overwrite=False) -> str:
        # 'image' '3' -> 'image.003'
        if index == '0':
            return name

        image_zeros = '.'
        c = 3 - len(index) if len(index) < 3 else 0  # how many 0 to add
        image_zeros += '0' * c
        new_name = name + image_zeros + index

        # image name can't exceed 63 characters
        exceeds_by = len(new_name) - 63
        if exceeds_by <= 0:
            return new_name

        name = name[:-(exceeds_by + 5)]  # remove 5 more - space for index

        # need to reiterate with the new name and make sure it isn't repeated
        new_index = self.v_name_get_index_in_data(vdata, name, overwrite)

        index = str(int(index) + new_index)
        image_zeros = '.'
        c = 3 - len(index) if len(index) < 3 else 0  # how many 0 to add
        image_zeros += '0' * c
        new_name = name + image_zeros + index
        return new_name

    def type_name_get_indexed(self, name: str, index: str, data,
                              image_overwrite=False, dir_filepath=None):
        # 'image' '3' -> 'image.003'
        if index == '0':
            return name

        image_zeros = '.'
        c = 3 - len(index) if len(index) < 3 else 0  # how many 0 to add
        image_zeros += '0' * c
        new_name = name + image_zeros + index

        # image name can't exceed 63 characters
        exceeds_by = len(new_name) - 63
        if exceeds_by <= 0:
            return new_name

        name = name[:-(exceeds_by + 5)]  # remove 5 more - space for index

        # need to reiterate with the new name and make sure it isn't repeated
        new_index = self.image_name_get_index_in_data(
            data, name, image_overwrite, dir_filepath)

        index = str(int(index) + new_index)
        image_zeros = '.'
        c = 3 - len(index) if len(index) < 3 else 0  # how many 0 to add
        image_zeros += '0' * c
        new_name = name + image_zeros + index
        return new_name

    def type_name_get_index_of(self, new_name: str, filename: str):
        filename = self.image_name_without_ext(filename)

        # remove dot and 4-digit number from the end - possible UDIM marker
        filename = re.sub(r'\.[0-9]{4}$', "", filename, count=1)
        name, index = os.path.splitext(filename)

        try:
            if not index:
                index = 0
            else:
                index = int(index[1:])
        except ValueError:
            index = -1

        if name.find(new_name) != 0:
            return -1
        else:
            return index

    def image_name_without_ext(self, filename: str) -> str:
        file_formats_data = [
            '.bmp', '.png', '.jpg', '.tiff', '.tga', '.exr', '.cin', '.dpx'
        ]

        if any(True for fileformat in file_formats_data if filename.find(
                fileformat) != -1):
            filename = os.path.splitext(filename)[0].replace(".<UDIM>", "")

        return filename

    def os_remove_file(self, filename: str, dir_filepath: str) -> None:
        file_path = os.path.join(dir_filepath, filename)
        if not os.path.isfile(file_path):
            return
        try:
            os.remove(file_path)
        except (FileNotFoundError, OSError) as error:
            print("BakeMaster Error: couldn't overwrite %s file: %s" % (
                filename, error))
            return
        else:
            # print("Removed from disk: ", file_path)
            return

    def v_name_get_index_in_data(self, vdata, name_init: str,
                                 overwrite=False) -> int:

        count = 0
        max_index_in_vs = -1

        for layer in vdata:
            l_name = layer.name

            index_in_vs = self.type_name_get_index_of(name_init, l_name)

            if index_in_vs == -1:
                continue

            if not overwrite:
                count += 1
                if index_in_vs > max_index_in_vs:
                    max_index_in_vs = index_in_vs
                continue

            try:
                vdata.remove(layer)
            except (KeyError, RuntimeError):
                count += 1
                if index_in_vs > max_index_in_vs:
                    max_index_in_vs = index_in_vs

        if not overwrite:
            return max_index_in_vs + 1
        else:
            return count

    def image_name_get_index_in_data(
            self, data, name_init: str, image_overwrite=False,
            dir_filepath=None) -> int:

        if dir_filepath is None:
            dir_filepath = ''

        count = 0
        max_index_in_filename = -1

        for item in data:
            filename, image_exists = item

            index_in_filename = self.type_name_get_index_of(
                name_init, filename)
            # if index_in_filename != -1:
            #     print(name_init, filename, index_in_filename)

            # if index_in_filename <= max_index_in_filename:  # XXX, wrong
            if index_in_filename == -1:
                continue

            if not image_overwrite:
                count += 1
                if index_in_filename > max_index_in_filename:
                    max_index_in_filename = index_in_filename
                continue

            self.os_remove_file(filename, dir_filepath)

            try:
                bpy.data.images.remove(bpy.data.images[filename],
                                       do_unlink=True)
            except (KeyError, RuntimeError):
                if image_exists:
                    continue
                count += 1
                if index_in_filename > max_index_in_filename:
                    max_index_in_filename = index_in_filename
            # else:
            #     print("Removed from Blender: ", filename)

        if not image_overwrite:
            return max_index_in_filename + 1
        else:
            return count

    def bake_image_getnewname(self, context, name_init: str,
                              output_filepath=None, run_data=True,
                              instead_data=[]):
        # want 'my_bake_image':
        # if with the same name exists:
        #     if overwrite: remove with the same name, -> 'my_bake_image'
        #     else: -> 'my_bake_image.002'
        # else: -> 'my_bake_image'

        overwrite = context.scene.bm_props.global_use_bake_overwrite

        if not run_data:
            data = instead_data

            index = self.image_name_get_index_in_data(
                data, name_init, image_overwrite=overwrite,
                dir_filepath=output_filepath)

            return self.type_name_get_indexed(
                name_init, str(index), data,
                image_overwrite=overwrite, dir_filepath=output_filepath)

        file_formats_data = [
            '.bmp', '.png', '.jpg', '.tiff', '.tga', '.exr'
        ]

        data = [[image.name, True] for image in bpy.data.images]

        # check image files in the output dir too if given
        if output_filepath is not None:
            try:
                dir_listed = os.listdir(output_filepath)
            except NotADirectoryError:
                dir_listed = os.listdir(os.path.dirname(output_filepath))

            dir_data = []
            for filename in dir_listed:
                splited = os.path.splitext(filename)

                # check only image files
                if splited[1] not in file_formats_data:
                    continue

                if filename not in data:
                    dir_data.append([filename, True])

            data += dir_data

        # append already initialized images
        for obj_shell in self.bake_images:
            for maps_shells in obj_shell:
                for map_shell in maps_shells:
                    data.append([map_shell, False])

        index = self.image_name_get_index_in_data(
            data, name_init, image_overwrite=overwrite,
            dir_filepath=output_filepath)

        return self.type_name_get_indexed(
            name_init, str(index), data, image_overwrite=overwrite,
            dir_filepath=output_filepath)

    def bake_object_get_cage_and_highpolies(self, _, object):
        # get object's cage and highpolies names in []

        names = []
        if object.hl_use_unique_per_map:
            # get highpolies, cage
            for map in object.global_maps:
                for highpoly in map.hl_highpoly_table:
                    if highpoly.global_highpoly_object_index == -1:
                        continue
                    if highpoly.global_highpoly_name_old in names:
                        continue
                    names.append(highpoly.global_highpoly_name_old)

                if map.hl_use_cage is False or map.hl_cage_object_index == -1:
                    continue
                elif map.hl_cage_name_old in names:
                    continue
                names.append(map.hl_cage_name_old)

        else:
            for highpoly in object.hl_highpoly_table:
                if highpoly.global_highpoly_object_index == -1:
                    continue
                if highpoly.global_highpoly_name_old in names:
                    continue
                names.append(highpoly.global_highpoly_name_old)

            if object.hl_use_cage is False or object.hl_cage_object_index == -1:
                return names
            elif object.hl_cage_name_old in names:
                return names
            names.append(object.hl_cage_name_old)

        return names

    def bake_container_get_file_format(self, container):
        file_format = container.out_file_format
        if file_format == 'TARGA' and container.out_tga_use_raw:
            file_format += '_RAW'
        return file_format

    def object_get(self, context, object_name: str):
        try:
            context.scene.objects[object_name]
        except (KeyError, AttributeError, UnboundLocalError):
            return None
        else:
            return context.scene.objects[object_name]

    def bake_map_get_or_return_invalid(self, context, container, object,
                                       source_object):
        # returns:
        # map, source_cage, source_highpolies, [report_type, report_message]

        report_type = None
        report_message = None
        ob_name = object.global_object_name
        source_highpolies = []
        source_highpolies_decals = []
        # skip map if cannot be accessed
        try:
            container.global_maps[self.bake_object_map_index]
        except IndexError:
            return None, None, [], [report_type, report_message]

        map = object.global_maps[self.bake_object_map_index]

        # skip if use_bake is False
        if map.global_use_bake is False:
            return None, None, [], [report_type, report_message]
        # skip if no images added
        try:
            images_object_shell = self.bake_images[self.bake_object_index]
            map_image = images_object_shell[0][self.bake_object_map_index]
            map_image_decal = images_object_shell[1][self.bake_object_map_index]
        except IndexError:
            return None, None, [], [report_type, report_message]

        # skip if bake_data is VERTEX_COLORS,
        # map is not VERTEX_COLOR_LAYER,
        # or map vrtx layer is None
        bake_data = container.uv_bake_data
        if container.uv_use_unique_per_map:
            bake_data = map.uv_bake_data
        if bake_data == 'VERTEX_COLORS':
            if map.global_map_type != 'VERTEX_COLOR_LAYER':
                return None, None, [], [report_type, report_message]
            elif map.map_vertexcolor_layer == 'NONE':
                return None, None, [], [report_type, report_message]

        # get cage_name, highpolies
        if object.hl_use_unique_per_map:
            cage_name = map.hl_cage_name_old
            use_cage = map.hl_use_cage
            # cage_index = map.hl_cage_object_index
            highpolies = map.hl_highpoly_table
        else:
            cage_name = object.hl_cage_name_old
            use_cage = object.hl_use_cage
            # cage_index = object.hl_cage_object_index
            highpolies = object.hl_highpoly_table

        # check cage
        cage_obj = self.object_get(context, cage_name) if use_cage else None

        if use_cage and cage_obj is None:
            report_type = 'ERROR'
            report_message = "%s Error: %s Cage not found in the Scene" % (
                ob_name, cage_name)
            return None, None, [], [report_type, report_message]

        elif use_cage:
            assert isinstance(cage_obj, bpy.types.Object)
            dg = context.evaluated_depsgraph_get()
            cage_obj_eval = dg.objects.get(cage_obj.name)
            obj_eval = dg.objects.get(source_object.name)
            assert isinstance(cage_obj_eval, bpy.types.Object)
            assert isinstance(obj_eval, bpy.types.Object)

            cage_mesh = cage_obj_eval.data
            obj_mesh = obj_eval.data
            assert isinstance(cage_mesh, bpy.types.Mesh)
            assert isinstance(obj_mesh, bpy.types.Mesh)

            # cage must have the same number of polygons as the object
            if len(cage_mesh.polygons) != len(obj_mesh.polygons):
                report_type = 'ERROR'
                report_message = ("%s Error: Cage mesh must have the same "
                                  % ob_name + "number of faces as the %s mesh"
                                  % ob_name)
                return None, None, [], [report_type, report_message]

        # check highpolies
        for highpoly in highpolies:
            highpoly_name = highpoly.global_highpoly_name_old
            highpoly_index = highpoly.global_highpoly_object_index
            if highpoly_index == -1:
                continue
            source_highpoly = self.object_get(context, highpoly_name)
            if source_highpoly is None:
                report_type = 'ERROR'
                report_message = "%s Error: %s Highpoly not found in the scene" % (
                    ob_name, highpoly_name)
                return None, None, [], [report_type, report_message]
            # appending highpoly to regular or decals
            if context.scene.bm_table_of_objects[highpoly_index].hl_is_decal:
                source_highpolies_decals.append(source_highpoly)
            else:
                source_highpolies.append(source_highpoly)

        # check if able to bake normal, disp with their chosen data
        if map.global_map_type == 'NORMAL':
            if map.map_normal_data == 'HIGHPOLY' and len(source_highpolies + source_highpolies_decals) == 0:
                report_type = 'ERROR'
                report_message = "%s Error: Normal Map: data is Highpolies but no highpolies chosen" % ob_name
                return None, None, [], [report_type, report_message]
            multires_mods = list(
                filter(lambda mod: mod.type == 'MULTIRES', source_object.modifiers))
            if map.map_normal_data == 'MULTIRES' and len(multires_mods) == 0:
                report_type = 'ERROR'
                report_message = "%s Error: Normal Map: data is Multires but no multires modifiers found" % ob_name
                return None, None, [], [report_type, report_message]
        if map.global_map_type == 'DISPLACEMENT':
            if map.map_displacement_data == 'HIGHPOLY' and len(source_highpolies + source_highpolies_decals) == 0:
                report_type = 'ERROR'
                report_message = "%s Error: Displacement Map: data is Highpolies but no highpolies chosen" % ob_name
                return None, None, [], [report_type, report_message]
            multires_mods = list(
                filter(lambda mod: mod.type == 'MULTIRES', source_object.modifiers))
            if map.map_displacement_data == 'MULTIRES' and len(multires_mods) == 0:
                report_type = 'ERROR'
                report_message = "%s Error: Displacement Map: data is Multires but no multires modifiers found" % ob_name
                return None, None, [], [report_type, report_message]

        if container.uv_use_unique_per_map:
            uv_container = map
        else:
            uv_container = container

        skip_map = False
        if uv_container.uv_bake_data == 'VERTEX_COLORS':
            if map.global_map_type != 'VERTEX_COLOR_LAYER':
                skip_map = True
        if uv_container.uv_bake_target == 'VERTEX_COLORS':
            if map.global_map_type == 'NORMAL' and map.map_normal_data == 'MULTIRES':
                skip_map = True
            elif map.global_map_type == 'DISPLACEMENT' and map.map_displacement_data in ['HIGHPOLY', 'MULTIRES']:
                skip_map = True
        if skip_map:
            return None, None, [], [None, None]

        # for highpolies, decals are baked lastly
        return map, cage_obj, source_highpolies + source_highpolies_decals, [report_type, report_message]

    def bake_object_get_or_return_invalid(self, context):
        # returns: container, object, source_object, [report_type, report_message]
        report_type = None
        report_message = None
        container_index = self.bake_objects_indexes[self.bake_object_index]
        # skip object that was not prepared in prepare_all_objects()
        if container_index == -1:
            return None, None, None, [report_type, report_message]
        # skip object if cannot be accessed
        try:
            context.scene.bm_table_of_objects[self.bake_object_index]
        except IndexError:
            self.handle_bake_invalid(None, None, 'OBJECT')
            return None, None, None, [report_type, report_message]

        container = context.scene.bm_table_of_objects[container_index]
        object = context.scene.bm_table_of_objects[self.bake_object_index]
        ob_name = object.global_object_name

        # skip if use_bake is False
        container1 = object
        for object1 in context.scene.bm_table_of_objects:
            if object1.nm_is_universal_container and object.nm_item_uni_container_master_index == object1.nm_master_index:
                container1 = object1
                break

        if container1.global_use_bake is False:
            return None, None, None, [report_type, report_message]
        # skip if no images added
        if len(self.bake_images[self.bake_object_index][0]) == 0:
            return None, None, None, [report_type, report_message]
        # skip containers, highs, cages
        if any([object.nm_is_universal_container, object.nm_is_local_container, object.hl_is_highpoly, object.hl_is_cage]):
            return None, None, None, [report_type, report_message]
        # skip if not found in the scene
        if self.object_get(context, ob_name) is None:
            return None, None, None, [report_type, report_message]

        source_object = self.bake_scene_object_get_and_setactive(
            context, ob_name)

        return container, object, source_object, [report_type, report_message]

    def bake_map_restore_mats_replug(self, materials_source):
        # restore previous map materials' nodes replug
        _ = self.bake_object_materials_handle_replug(
            materials_source, self.bake_object_materials_restore_args, restore=True)
        self.bake_object_materials_restore_args = None

    def bake_map_get_data(self, context):
        # recursively try to get map data
        # get object data
        container = self.bake_current_container
        object = self.bake_current_object
        source_object = self.bake_current_source_object
        if self.bake_current_source_highpolies is None:
            materials_source = source_object
        elif len(self.bake_current_source_highpolies):
            materials_source = self.bake_current_source_highpolies[
                self.bake_object_map_highpoly_index]
        else:
            materials_source = source_object

        # restore previous map materials' nodes replug
        self.bake_map_restore_mats_replug(materials_source)
        # handle map previews
        print("BakeMaster Info: Switching off all map previews...")
        self.bake_map_handle_preview(context, None, None, 'UNSET')

        # check if should go to the next object
        if self.bake_object_map_index == len(self.bake_images[self.bake_object_index][0]):
            return {'DONE'}, None, None, None

        # check if map is valid to be baked
        map, source_cage, source_highpolies, report_data = self.bake_map_get_or_return_invalid(
            context, container, object, source_object)
        if map is None:
            self.handle_bake_invalid(report_data[0], report_data[1], 'MAP')
            # check if should go to the next object
            if self.bake_object_map_index == len(self.bake_images[self.bake_object_index][0]):
                return {'DONE'}, map, source_cage, source_highpolies
            else:
                return self.bake_map_get_data(context)
        # prepare map
        if len(source_highpolies):
            source_highpoly = source_highpolies[self.bake_object_map_highpoly_index]
        else:
            source_highpoly = None
        self.bake_prepare_map(context, container, object,
                              source_object, source_highpoly, map)
        return {'CONTINUE'}, map, source_cage, source_highpolies

    def bake_object_get_data(self, context):
        # recursively try to get object data
        # check if should finish bake
        if self.bake_object_index == len(self.bake_images):
            return {'DONE'}, None, None, None
        container, object, source_object, report_data = self.bake_object_get_or_return_invalid(
            context)
        # check if object is valid to be baked
        if any([container is None, object is None, source_object is None]):
            self.handle_bake_invalid(report_data[0], report_data[1], 'OBJECT')
            # check if should finish bake
            if self.bake_object_index == len(self.bake_images):
                return {'DONE'}, container, object, source_object
            else:
                return self.bake_object_get_data(context)
        return {'CONTINUE'}, container, object, source_object

    def bake_finish_object(self, context, container, object, source_object):
        # finish baking object
        self.bake_scene_objects_hide(context, 'CUSTOM_UNHIDE')

        # remove old baked materials on overwrite
        if context.scene.bm_props.global_use_bake_overwrite:
            for mat_i in range(len(source_object.data.materials) - 1, -1, -1):
                material = source_object.data.materials[mat_i]
                if material is None or material.name.find("_Baked_BM") == -1:
                    continue
                # crashes blender due to linked image users present in material
                # bpy.data.materials.remove(source_object.data.materials.pop(index=mat_i))
                source_object.data.materials.pop(index=mat_i)

        # create material with baked maps if needed
        if container.bake_create_material is False:
            return

        # 2.91 brings emission strength socket, so opacity and normal sockets got moved 1 socket downwards
        socket_inc_291 = 1 if self._version_current >= (2, 91, 0) else 0
        # 3.0 brings sss ior and anitrosopy -> all sockets with index > 3 are moved 2 downwards
        socket_inc_300 = 2 if self._version_current >= (3, 0, 0) else 0

        socket_metal_i = 4
        socket_rough_i = 7
        socket_trans_i = 15
        socket_emissionc_i = 17
        socket_opac_i = 18
        socket_normal_i = 19

        if self._version_current >= (4, 0, 0):
            socket_metal_i = 1
            socket_rough_i = 2
            socket_trans_i = 17
            socket_emissionc_i = 26
            socket_opac_i = 4
            socket_normal_i = 5
        elif self._version_current >= (3, 0, 0):
            socket_metal_i += 2
            socket_rough_i += 2
            socket_trans_i += 2
            socket_emissionc_i += 2
            socket_opac_i += 3
            socket_normal_i += 3
        elif self._version_current >= (2, 91, 0):
            socket_opac_i += 1
            socket_normal_i += 1

        new_mat = bpy.data.materials.new("%s_Baked_BM" % source_object.name)
        source_object.data.materials.append(new_mat)

        add_images = {
            'ALBEDO_DIFFUSE_C_COMBINED': [0, [], (-300, 300), (-260, 0)],
            'METALNESS': [socket_metal_i, [], (-300, 170), (-260, 0)],
            # 'SPECULAR': [5 + socket_inc_300, [], (-300, 130), (-260, 0)],
            'ROUGHNESS_C_ROUGHNESS': [socket_rough_i, [], (-300, 90), (-260, 0)],
            'C_TRANSMISSION': [socket_trans_i, [], (-300, -85), (-260, 0)],
            'EMISSION_C_EMIT': [socket_emissionc_i, [], (-300, -125), (-260, 0)],
            'OPACITY': [socket_opac_i, [], (-300, -165), (-260, 0)],
            'NORMAL_C_NORMAL': [socket_normal_i, [], (-600, -205), (-260, 0)],
            'DISPLACEMENT_VECTOR_DISPLACEMENT': [0, [], (300, 0), (0, -40)],
            'OTHER': [None, [], (-300, -310), (0, -40)],
        }

        # collect images that can be added
        for img_tag_index, images_shell in enumerate(self.bake_images[
                self.bake_object_index]):
            # images_shell[0] and images_shell[1] are of equal length
            for image_index, image in enumerate(images_shell):
                if not (self.bake_images_ad_data[image][3]
                        or self.bake_images_ad_data[image][4]):
                    continue

                try:
                    map = container.global_maps[image_index]
                except IndexError:
                    continue

                if map.global_map_type == 'NORMAL' and map.map_normal_data != 'MATERIAL':
                    # continue
                    pass
                if map.global_map_type == 'DISPLACEMENT' and map.map_displacement_result != 'MATERIAL':
                    continue
                if map.global_map_type == 'VECTOR_DISPLACEMENT' and map.map_vector_displacement_result != 'MATERIAL':
                    continue
                added = False
                for key in add_images:
                    if map.global_map_type in key:
                        add_images[key][1].append([image_index, img_tag_index])
                        added = True
                        break
                if added is False:
                    add_images['OTHER'][1].append([image_index, img_tag_index])

        # add image nodes
        new_mat.use_nodes = True
        nodes = new_mat.node_tree.nodes
        links = new_mat.node_tree.links
        bsdf_node = nodes['Principled BSDF']
        nm_node = nodes.new('ShaderNodeNormalMap')
        nm_node.location = (-300, 205)
        links.new(nm_node.outputs[0], bsdf_node.inputs[socket_normal_i])
        for key in add_images:
            images_indexes = add_images[key][1]
            if len(images_indexes) == 0:
                continue
            for shell_index, shell in enumerate(images_indexes):
                img_tag_index = add_images[key][1][shell_index][1]
                image_index = add_images[key][1][shell_index][0]
                image_name = self.bake_images[self.bake_object_index][img_tag_index][image_index]

                if self.bake_images_ad_data[image_name][4]:
                    if self._version_current >= (3, 1, 0) and self._version_current < (3, 2, 0):
                        new_node = nodes.new('ShaderNodeAttribute')
                        new_node.attribute_type = 'GEOMETRY'
                        new_node.attribute_name = image_name
                    else:
                        new_node = nodes.new('ShaderNodeVertexColor')
                        new_node.layer_name = image_name
                else:
                    new_node = nodes.new('ShaderNodeTexImage')
                    new_node.image = bpy.data.images[image_name]

                    # add uv map node
                    uv_container = container
                    if container.uv_use_unique_per_map:
                        uv_container = container.global_maps[image_index]
                    if container.nm_uni_container_is_global:
                        uv_container = object
                    uv_map = uv_container.uv_active_layer
                    uv_new_node = nodes.new('ShaderNodeUVMap')
                    uv_new_node.uv_map = uv_map
                    uv_new_node.hide = True
                    links.new(uv_new_node.outputs[0], new_node.inputs[0])
                    uv_new_node.location = add_images[key][2]

                new_node.hide = True
                new_node.location = add_images[key][2]

                loc_x_inc = add_images[key][3][0]
                loc_y_inc = add_images[key][3][1]
                loc_x = add_images[key][2][0]
                loc_y = add_images[key][2][1]
                add_images[key][2] = (loc_x + loc_x_inc, loc_y + loc_y_inc)

                # link if shell is the first
                if shell_index != 0:
                    continue
                bsdf_input_index = add_images[key][0]
                if bsdf_input_index is None:
                    continue
                if key == 'DISPLACEMENT_VECTOR_DISPLACEMENT':
                    link_to = nodes['Material Output'].inputs[2]
                elif key == 'NORMAL_C_NORMAL':
                    link_to = nm_node.inputs[1]
                else:
                    link_to = bsdf_node.inputs[bsdf_input_index]
                links.new(new_node.outputs[0], link_to)

        # reset sss ior to 0, why is 1.4 a default value? >-<
        if self._version_current >= (3, 0, 0) and self._version_current < (4, 0, 0):
            try:
                nodes["Principled BSDF"].inputs[4].default_value = 0
            except KeyError:
                pass

    def bake_finish_map(self, container, object, source_object, map, image):
        # finish baking map
        # remove bm image nodes from source_object mats
        for mat in source_object.data.materials:
            if mat is None:
                continue
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            remove_nodes = []
            for node_index, node in enumerate(nodes):
                if node.type != 'TEX_IMAGE':
                    continue
                if node.image is None:
                    continue
                if node.image.name in self.bake_current_source_object_bm_image_nodes:
                    remove_nodes.append(node_index)
            for node_index in reversed(remove_nodes):
                try:
                    nodes.remove(nodes[node_index])
                except (RuntimeError, ReferenceError):
                    pass
        self.bake_current_source_object_bm_image_nodes = []

        # assign modifiers if needed
        if container.bake_assign_modifiers is False:
            return
        run_add_modifs = False
        if map.global_map_type == 'DISPLACEMENT' and map.map_displacement_result == 'MODIFIER':
            run_add_modifs = True
        elif map.global_map_type == 'VECTOR_DISPLACEMENT' and map.map_vector_displacement_result == 'MODIFIER':
            run_add_modifs = True
        if run_add_modifs is False:
            return

        # add modifs
        map_prefix = getattr(map, "map_%s_prefix" % map.global_map_type)
        tex = bpy.data.textures.new(name=image.name, type='IMAGE')
        tex.image = image
        if map.global_map_type == 'VECTOR_DISPLACEMENT' and map.map_vector_displacement_use_negative:
            tex.use_clamp = False
        print("BakeMaster Info: Adding Displace Modifier for %s..." %
              source_object.name)
        mod = source_object.modifiers.new("Baked %s" % map_prefix, 'DISPLACE')
        mod.show_viewport = False
        mod.show_render = False
        mod.texture = tex
        mod.texture_coords = 'UV'
        uv_container = object
        if container.uv_use_unique_per_map:
            uv_container = map
        if container.nm_uni_container_is_global:
            uv_container = object
        mod.uv_layer = uv_container.uv_active_layer
        mod.strength = 0.1

    def bake_prepare_map(self, context, container, object, source_object, source_highpoly, map):
        # prepare map for bake
        container.global_maps_active_index = self.bake_object_map_index

        # get containers with map settings
        uv_container = container
        if container.uv_use_unique_per_map:
            uv_container = map

        # uv snap to pixels
        # NOTE
        # this can be improved so that we don't snap,
        # if identical snapping was performed for the same uv for previous map
        if container.nm_uni_container_is_global:
            uv_layer = object.uv_active_layer
        else:
            uv_layer = uv_container.uv_active_layer
        if uv_container.uv_snap_islands_to_pixels:
            print("BakeMaster Info: UV Snapping to pixels %s..." %
                  source_object.name)
            self.bake_object_uv_layer_snap_to_pixels(
                source_object, source_object.data.uv_layers[uv_layer], res_x, res_y)
        # set active source_object uv_layer
        source_object.data.uv_layers.active = source_object.data.uv_layers[uv_layer]

        # Bake to active but not set it to be the one user's baking from
        # source_object.data.uv_layers.active.active_render = True

        # update decal view after all render settings were set
        if object.decal_is_decal:
            status = self.dv_lot.modal(context)
            if status[0] != {'PASS_THROUGH'} and status[1]:
                self.report_msg(
                    status[1][0].pop(),
                    "Cannot update Decal Render Frame: %s" % status[1][1])

        # materials' nodes replugging

        socket_metal_i = 4
        if self._version_current >= (4, 0, 0):
            socket_metal_i = 1
        elif self._version_current >= (3, 0, 0):
            socket_metal_i = 6

        # 2.91 brings emission strength socket, so opacity and normal sockets
        # got moved 1 socket downwards
        # socket_inc_291 = 1 if self._version_current >= (2, 91, 0) else 0
        # 3.0 brings sss ior and anitrosopy -> all sockets with index > 3 are
        # moved 2 downwards
        # socket_inc_300 = 2 if self._version_current >= (3, 0, 0) else 0

        mats_restore = None
        if source_highpoly is None:
            materials_source = source_object
        else:
            materials_source = source_highpoly

        # ALBEDO -> unplug metallic input
        if map.global_map_type == 'ALBEDO':
            mats_restore = self.bake_object_materials_handle_replug(
                materials_source, None, [socket_metal_i], None, [0],
                'BSDF_PRINCIPLED', None, None, False)

        # NOTE
        # Metalness, Opacity, and Displacement are commented out below
        # as they are baked through the preview technique.
        # Same applies to Specular, AlbedoS, and Glossiness maps.

        # METALNESS -> plug metallic into emission
        # elif map.global_map_type == 'METALNESS':
        #     mats_restore = self.bake_object_materials_handle_replug(materials_source, None, [4 + socket_inc_300, 17 + socket_inc_300], None, [0.0, [0, 0, 0, 1]], 'BSDF_PRINCIPLED', [4 + socket_inc_300, 17 + socket_inc_300], 'SAME', False)

        # OPACITY -> plug opacity into emission
        # elif map.global_map_type == 'OPACITY':
        #     mats_restore = self.bake_object_materials_handle_replug(materials_source, None, [17 + socket_inc_300, 18 + socket_inc_291 + socket_inc_300], None, [[0, 0, 0, 1], 1.0], 'BSDF_PRINCIPLED', [18 + socket_inc_291 + socket_inc_300, 17 + socket_inc_300], 'SAME')

        # Displacement replug is commented out to
        # fix displacement not baking out.

        # DISPLACEMENT -> plug disp output into emission shader
        # elif map.global_map_type == 'DISPLACEMENT' and map.map_displacement_data == 'MATERIAL':
        #     mats_restore = self.bake_object_materials_handle_replug(materials_source, None, [2, 0], 0, [None, None], 'OUTPUT_MATERIAL', [2, 0, 0, 0], 'ShaderNodeEmission')

        # restore in get map data, object operate
        self.bake_object_materials_restore_args = mats_restore

        # handle map previews
        print("BakeMaster Info: Toggling %s map preview for %s..." %
              (map.global_map_type, source_object.name))
        self.bake_map_handle_preview(context, map, object)

    def bm_obj_get_container(self, ctx: bpy.types.Context,
                             bm_obj: bpy.types.PropertyGroup
                             ) -> bpy.types.PropertyGroup:
        sc = ctx.scene
        bm_objs = sc.bm_table_of_objects
        if not sc.bm_props.global_use_name_matching:
            return bm_obj
        elif bm_obj.nm_is_detached:
            return bm_obj

        bm_ctnr_i = bm_obj.nm_item_uni_container_master_index
        if bm_ctnr_i == -1:
            return bm_obj

        assert bm_ctnr_i < len(bm_objs)
        return bm_objs[bm_ctnr_i]

    def bake_prepare_object(self, context, container, object, source_object):
        # prepare object for bake
        source_object.hide_viewport = False
        source_object.hide_render = False
        context.scene.bm_props.global_active_index = self.bake_object_index
        # remove none materials
        # change uv_active_layer if was auto unwrapped,
        # visibility groups,
        # prepare for decal object baking

        # remove None materials
        to_remove = []
        for index, material in enumerate(source_object.data.materials):
            if material is None:
                to_remove.append(index)
        for index in sorted(to_remove, reverse=True):
            source_object.data.materials.pop(index=index)

        # if object was auto unwrapped, new uv layer was added,
        # reassign uv_active_layer to that new uv layer
        source_object_uvs = source_object.data.uv_layers
        if object.uv_use_auto_unwrap or len(source_object_uvs) == 1:
            if object.uv_use_unique_per_map:
                for map in object.global_maps:
                    map.uv_active_layer = source_object_uvs[len(
                        source_object_uvs) - 1].name
            else:
                object.uv_active_layer = source_object_uvs[len(
                    source_object_uvs) - 1].name

        # set OBJECT mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # unhide previous visibility groups
        self.bake_scene_objects_hide(context, 'CUSTOM_UNHIDE')

        # visibility groups
        to_hide = []
        for index, container1_index in enumerate(self.bake_objects_indexes):
            try:
                object1 = context.scene.bm_table_of_objects[index]
                if container1_index == -1:  # i.e bm_objs[index] won't be baked
                    container1 = self.bm_obj_get_container(context, object1)
                else:
                    container1 = context.scene.bm_table_of_objects[
                        container1_index]
            except IndexError:
                continue

            source_object1 = self.object_get(
                context, object1.global_object_name)

            # check if valid object
            if any([source_object1 is None, object1.nm_is_universal_container,
                    object1.nm_is_local_container]):
                continue

            # skip if not baked
            # if len(self.bake_images[index][0]) == 0:
            #     continue

            # skip itself and the same visibility group
            if any([container1.bake_hide_when_inactive
                    and index == self.bake_object_index,
                    container1.bake_hide_when_inactive is False
                    and container1.bake_vg_index == container.bake_vg_index]):
                continue

            # append source_object1 with its cages and highpolies to to_hide[]
            to_hide.append(source_object1)
            for name in self.bake_object_get_cage_and_highpolies(
                    container1, object1):
                ch_source = self.object_get(context, name)
                if ch_source is not None:
                    to_hide.append(ch_source)

        # set OBJECT mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # hide for visibility groups
        self.bake_scene_objects_hide(context, 'CUSTOM_HIDE', to_hide)

        # set OBJECT mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # decal object
        if not object.decal_is_decal:
            return None

        self.dv_lot = BM_LOT_DECAL_View(
            bm_obj_i=self.bake_object_index,
            # bm_ctnr_i=self.bake_object_index)
            bm_ctnr_i=self.bake_objects_indexes[self.bake_object_index],
            use_obj_res=True)
        status = self.dv_lot.invoke(None, context)

        if status[0] == {'FINISHED'} or not status[1]:
            return None

        self.report_msg(
            status[1][0].pop(),
            "Cannot update Decal Render Frame: %s" % status[1][1])
        return None

    def bake_prepare_all_objects(self, context, prepare_index=[]):
        # prepare all objects for bake

        # mode_set requires active object
        if context.active_object is None:
            context.view_layer.objects.active = context.scene.objects[0]

        bpy.ops.object.mode_set(mode='OBJECT')
        # hide hidden in the scene, so they do no affect this bake
        self.bake_scene_objects_hide(context, 'HIDE')

        # display this message once
        if context.scene.bm_props.global_use_bake_overwrite:
            print("BakeMaster Info: Overwriting previous baked files...")

        # set self.bake_objects_indexes
        # set self.bake_images
        # auto unwrap, shading, uv repack
        uni_c_index = -1
        uni_c_master_index = -1
        local_c_master_index = -1
        for index, object in enumerate(context.scene.bm_table_of_objects):
            context.scene.bm_props.global_active_index = index
            # add images shell for current object
            self.bake_images.append([[], []])
            self.bake_channel_pack_data.append([])

            if self.object_get(context, object.global_object_name) is None:
                if not any([object.nm_is_universal_container, object.nm_is_local_container]):
                    continue

            # skip highpolies, cages, objs not regular and not in lowpoly containers
            if any([object.hl_is_highpoly, object.hl_is_cage]):
                continue

            if context.scene.bm_props.global_use_name_matching:
                if object.nm_is_universal_container:
                    uni_c_master_index = object.nm_master_index
                elif object.nm_is_lowpoly_container and object.nm_item_uni_container_master_index == uni_c_master_index:
                    local_c_master_index = object.nm_master_index
                elif object.nm_is_detached:
                    uni_c_master_index = -1
                    local_c_master_index = -1
                # object in container
                else:
                    if object.nm_item_uni_container_master_index == uni_c_master_index and object.nm_item_local_container_master_index == local_c_master_index:
                        pass
                    else:
                        continue
            # skip local container
            if object.nm_is_local_container:
                continue

            # get global uni_c master_index to then access its settings
            if object.nm_is_detached:
                uni_c_index = -1
            if object.nm_is_universal_container:
                if object.nm_uni_container_is_global:
                    uni_c_index = index
                else:
                    uni_c_index = -1
            # object
            else:
                # for self.control == 'BAKE_THIS'
                if all([uni_c_index == -1, len(prepare_index) != 0, index not in prepare_index]):
                    continue
                if uni_c_index != -1 and len(prepare_index) != 0:
                    if uni_c_index not in prepare_index and index not in prepare_index:
                        continue
                    if object.nm_item_uni_container_master_index != context.scene.bm_table_of_objects[uni_c_index].nm_master_index:
                        continue

                # get container data class with props
                container = context.scene.bm_table_of_objects[uni_c_index] if uni_c_index != -1 else object

                # add global container's maps
                # otherwise just bakes black for object's maps with preview
                if container.nm_uni_container_is_global:
                    # unset all previews
                    BM_MAP_PROPS_MapPreview_Unset(None, context)
                    # trash
                    to_remove = []
                    for map_index, map in enumerate(object.global_maps):
                        to_remove.append(map_index)
                    for map_index in sorted(to_remove, reverse=True):
                        # unset highpolies
                        BM_ITEM_PROPS_hl_highpoly_SyncedRemoval(
                            context, map_index, 'MAP', False)
                        # update use_cage
                        BM_ITEM_PROPS_hl_cage_UpdateOnRemove(
                            context, map_index, 'MAP')
                        object.global_maps.remove(map_index)
                        BM_ITEM_PROPS_hl_highpoly_UpdateNames(context)
                    object.global_maps_active_index = 0

                    # add
                    for map_index, map in enumerate(container.global_maps):
                        new_map = object.global_maps.add()
                        new_map.global_map_object_index = index
                        object.global_maps_active_index = map_index
                        map_data = {
                            'global_map_index': map_index + 1,
                            'global_use_bake': map.global_use_bake,
                            'global_map_type': map.global_map_type,

                            # 'hl_use_cage' : map.hl_use_cage,
                            'hl_cage_type': map.hl_cage_type,
                            'hl_cage_extrusion': map.hl_cage_extrusion,
                            'hl_max_ray_distance': map.hl_max_ray_distance,

                            'uv_bake_data': map.uv_bake_data,
                            'uv_bake_target': map.uv_bake_target,
                            # 'uv_active_layer' : map.uv_active_layer,
                            'uv_type': map.uv_type,
                            'uv_snap_islands_to_pixels': map.uv_snap_islands_to_pixels,

                            'out_use_denoise': map.out_use_denoise,
                            'out_file_format': map.out_file_format,
                            'out_tga_use_raw': map.out_tga_use_raw,
                            'out_dpx_use_log': map.out_dpx_use_log,
                            'out_tiff_compression': map.out_tiff_compression,
                            'out_exr_codec': map.out_exr_codec,
                            'out_compression': map.out_compression,
                            'out_quality': map.out_quality,
                            'out_res': map.out_res,
                            'out_res_height': map.out_res_height,
                            'out_res_width': map.out_res_width,
                            'out_margin': map.out_margin,
                            'out_margin_type': map.out_margin_type,
                            'out_bit_depth': map.out_bit_depth,
                            'out_use_alpha': map.out_use_alpha,
                            'out_use_transbg': map.out_use_transbg,
                            # 'out_udim_start_tile' : map.out_udim_start_tile,
                            # 'out_udim_end_tile' : map.out_udim_end_tile,
                            'out_super_sampling_aa': map.out_super_sampling_aa,
                            'out_upscaling': map.out_upscaling,
                            'out_samples': map.out_samples,
                            'out_use_adaptive_sampling': map.out_use_adaptive_sampling,
                            'out_adaptive_threshold': map.out_adaptive_threshold,
                            'out_min_samples': map.out_min_samples,

                            'map_ALBEDO_prefix': map.map_ALBEDO_prefix,

                            'map_METALNESS_prefix': map.map_METALNESS_prefix,

                            'map_ROUGHNESS_prefix': map.map_ROUGHNESS_prefix,

                            'map_DIFFUSE_prefix': map.map_DIFFUSE_prefix,

                            'map_SPECULAR_prefix': map.map_SPECULAR_prefix,

                            'map_GLOSSINESS_prefix': map.map_GLOSSINESS_prefix,

                            'map_OPACITY_prefix': map.map_OPACITY_prefix,

                            'map_EMISSION_prefix': map.map_EMISSION_prefix,

                            'map_PASS_prefix': map.map_PASS_prefix,
                            # 'map_PASS_use_preview' : map.map_PASS_use_preview,
                            'map_pass_type': map.map_pass_type,

                            'map_DECAL_prefix': map.map_DECAL_prefix,
                            # 'map_DECAL_use_preview' : map.map_DECAL_use_preview,
                            'map_decal_pass_type': map.map_decal_pass_type,
                            'map_decal_height_opacity_invert': map.map_decal_height_opacity_invert,
                            'map_decal_normal_preset': map.map_decal_normal_preset,
                            'map_decal_normal_custom_preset': map.map_decal_normal_custom_preset,
                            'map_decal_normal_r': map.map_decal_normal_r,
                            'map_decal_normal_g': map.map_decal_normal_g,
                            'map_decal_normal_b': map.map_decal_normal_b,

                            'map_VERTEX_COLOR_LAYER_prefix': map.map_VERTEX_COLOR_LAYER_prefix,
                            # 'map_VERTEX_COLOR_LAYER_use_preview' : map.map_VERTEX_COLOR_LAYER_use_preview,
                            # 'map_vertexcolor_layer' : map.map_vertexcolor_layer,

                            'map_C_COMBINED_prefix': map.map_C_COMBINED_prefix,

                            'map_C_AO_prefix': map.map_C_AO_prefix,

                            'map_C_SHADOW_prefix': map.map_C_SHADOW_prefix,

                            'map_C_POSITION_prefix': map.map_C_POSITION_prefix,

                            'map_C_NORMAL_prefix': map.map_C_NORMAL_prefix,

                            'map_C_UV_prefix': map.map_C_UV_prefix,

                            'map_C_ROUGHNESS_prefix': map.map_C_ROUGHNESS_prefix,

                            'map_C_EMIT_prefix': map.map_C_EMIT_prefix,

                            'map_C_ENVIRONMENT_prefix': map.map_C_ENVIRONMENT_prefix,

                            'map_C_DIFFUSE_prefix': map.map_C_DIFFUSE_prefix,

                            'map_C_GLOSSY_prefix': map.map_C_GLOSSY_prefix,

                            'map_C_TRANSMISSION_prefix': map.map_C_TRANSMISSION_prefix,

                            'map_cycles_use_pass_direct': map.map_cycles_use_pass_direct,
                            'map_cycles_use_pass_indirect': map.map_cycles_use_pass_indirect,
                            'map_cycles_use_pass_color': map.map_cycles_use_pass_color,
                            'map_cycles_use_pass_diffuse': map.map_cycles_use_pass_diffuse,
                            'map_cycles_use_pass_glossy': map.map_cycles_use_pass_glossy,
                            'map_cycles_use_pass_transmission': map.map_cycles_use_pass_transmission,
                            'map_cycles_use_pass_ambient_occlusion': map.map_cycles_use_pass_ambient_occlusion,
                            'map_cycles_use_pass_emit': map.map_cycles_use_pass_emit,

                            'map_NORMAL_prefix': map.map_NORMAL_prefix,
                            # 'map_NORMAL_use_preview' : map.map_NORMAL_use_preview,
                            'map_normal_data': map.map_normal_data,
                            'map_normal_space': map.map_normal_space,
                            'map_normal_multires_subdiv_levels': map.map_normal_multires_subdiv_levels,
                            'map_normal_preset': map.map_normal_preset,
                            'map_normal_custom_preset': map.map_normal_custom_preset,
                            'map_normal_r': map.map_normal_r,
                            'map_normal_g': map.map_normal_g,
                            'map_normal_b': map.map_normal_b,

                            'map_DISPLACEMENT_prefix': map.map_DISPLACEMENT_prefix,
                            # 'map_DISPLACEMENT_use_preview' : map.map_DISPLACEMENT_use_preview,
                            'map_displacement_data': map.map_displacement_data,
                            'map_displacement_result': map.map_displacement_result,
                            'map_displacement_subdiv_levels': map.map_displacement_subdiv_levels,
                            'map_displacement_multires_subdiv_levels': map.map_displacement_multires_subdiv_levels,
                            'map_displacement_use_lowres_mesh': map.map_displacement_use_lowres_mesh,

                            'map_VECTOR_DISPLACEMENT_prefix': map.map_VECTOR_DISPLACEMENT_prefix,
                            # 'map_VECTOR_DISPLACEMENT_use_preview' : map.map_VECTOR_DISPLACEMENT_use_preview,
                            'map_vector_displacement_use_negative': map.map_vector_displacement_use_negative,
                            'map_vector_displacement_result': map.map_vector_displacement_result,
                            'map_vector_displacement_subdiv_levels': map.map_vector_displacement_subdiv_levels,

                            'map_POSITION_prefix': map.map_POSITION_prefix,
                            # 'map_POSITION_use_preview' : map.map_POSITION_use_preview,

                            'map_AO_prefix': map.map_AO_prefix,
                            # 'map_AO_use_preview' : map.map_AO_use_preview,
                            'map_AO_use_default': map.map_AO_use_default,
                            'map_ao_samples': map.map_ao_samples,
                            'map_ao_distance': map.map_ao_distance,
                            'map_ao_black_point': map.map_ao_black_point,
                            'map_ao_white_point': map.map_ao_white_point,
                            'map_ao_brightness': map.map_ao_brightness,
                            'map_ao_contrast': map.map_ao_contrast,
                            'map_ao_opacity': map.map_ao_opacity,
                            'map_ao_use_local': map.map_ao_use_local,
                            'map_ao_use_invert': map.map_ao_use_invert,

                            'map_CAVITY_prefix': map.map_CAVITY_prefix,
                            # 'map_CAVITY_use_preview' : map.map_CAVITY_use_preview,
                            'map_CAVITY_use_default': map.map_CAVITY_use_default,
                            'map_cavity_black_point': map.map_cavity_black_point,
                            'map_cavity_white_point': map.map_cavity_white_point,
                            'map_cavity_power': map.map_cavity_power,
                            'map_cavity_use_invert': map.map_cavity_use_invert,

                            'map_CURVATURE_prefix': map.map_CURVATURE_prefix,
                            # 'map_CURVATURE_use_preview' : map.map_CURVATURE_use_preview,
                            'map_CURVATURE_use_default': map.map_CURVATURE_use_default,
                            'map_curv_samples': map.map_curv_samples,
                            'map_curv_radius': map.map_curv_radius,
                            'map_curv_black_point': map.map_curv_black_point,
                            'map_curv_mid_point': map.map_curv_mid_point,
                            'map_curv_white_point': map.map_curv_white_point,
                            'map_curv_body_gamma': map.map_curv_body_gamma,

                            'map_THICKNESS_prefix': map.map_THICKNESS_prefix,
                            # 'map_THICKNESS_use_preview' : map.map_THICKNESS_use_preview,
                            'map_THICKNESS_use_default': map.map_THICKNESS_use_default,
                            'map_thick_samples': map.map_thick_samples,
                            'map_thick_distance': map.map_thick_distance,
                            'map_thick_black_point': map.map_thick_black_point,
                            'map_thick_white_point': map.map_thick_white_point,
                            'map_thick_brightness': map.map_thick_brightness,
                            'map_thick_contrast': map.map_thick_contrast,
                            'map_thick_use_invert': map.map_thick_use_invert,

                            'map_ID_prefix': map.map_ID_prefix,
                            # 'map_ID_use_preview' : map.map_ID_use_preview,
                            'map_matid_data': map.map_matid_data,
                            'map_matid_vertex_groups_name_contains': map.map_matid_vertex_groups_name_contains,
                            'map_matid_algorithm': map.map_matid_algorithm,
                            'map_matid_seed': map.map_matid_seed,

                            'map_MASK_prefix': map.map_MASK_prefix,
                            # 'map_MASK_use_preview' : map.map_MASK_use_preview,
                            'map_mask_data': map.map_mask_data,
                            'map_mask_vertex_groups_name_contains': map.map_mask_vertex_groups_name_contains,
                            'map_mask_materials_name_contains': map.map_mask_materials_name_contains,
                            'map_mask_color1': map.map_mask_color1,
                            'map_mask_color2': map.map_mask_color2,
                            'map_mask_use_invert': map.map_mask_use_invert,

                            'map_XYZMASK_prefix': map.map_XYZMASK_prefix,
                            # 'map_XYZMASK_use_preview' : map.map_XYZMASK_use_preview,
                            'map_XYZMASK_use_default': map.map_XYZMASK_use_default,
                            'map_xyzmask_use_x': map.map_xyzmask_use_x,
                            'map_xyzmask_use_y': map.map_xyzmask_use_y,
                            'map_xyzmask_use_z': map.map_xyzmask_use_z,
                            'map_xyzmask_coverage': map.map_xyzmask_coverage,
                            'map_xyzmask_saturation': map.map_xyzmask_saturation,
                            'map_xyzmask_opacity': map.map_xyzmask_opacity,
                            'map_xyzmask_use_invert': map.map_xyzmask_use_invert,

                            'map_GRADIENT_prefix': map.map_GRADIENT_prefix,
                            # 'map_GRADIENT_use_preview' : map.map_GRADIENT_use_preview,
                            'map_GRADIENT_use_default': map.map_GRADIENT_use_default,
                            'map_gmask_type': map.map_gmask_type,
                            'map_gmask_location_x': map.map_gmask_location_x,
                            'map_gmask_location_y': map.map_gmask_location_y,
                            'map_gmask_location_z': map.map_gmask_location_z,
                            'map_gmask_rotation_x': map.map_gmask_rotation_x,
                            'map_gmask_rotation_y': map.map_gmask_rotation_y,
                            'map_gmask_rotation_z': map.map_gmask_rotation_z,
                            'map_gmask_scale_x': map.map_gmask_scale_x,
                            'map_gmask_scale_y': map.map_gmask_scale_y,
                            'map_gmask_scale_z': map.map_gmask_scale_z,
                            'map_gmask_coverage': map.map_gmask_coverage,
                            'map_gmask_contrast': map.map_gmask_contrast,
                            'map_gmask_saturation': map.map_gmask_saturation,
                            'map_gmask_opacity': map.map_gmask_opacity,
                            'map_gmask_use_invert': map.map_gmask_use_invert,

                            'map_EDGE_prefix': map.map_EDGE_prefix,
                            # 'map_EDGE_use_preview' : map.map_EDGE_use_preview,
                            'map_EDGE_use_default': map.map_EDGE_use_default,
                            'map_edgemask_samples': map.map_edgemask_samples,
                            'map_edgemask_radius': map.map_edgemask_radius,
                            'map_edgemask_edge_contrast': map.map_edgemask_edge_contrast,
                            'map_edgemask_body_contrast': map.map_edgemask_body_contrast,
                            'map_edgemask_use_invert': map.map_edgemask_use_invert,

                            'map_WIREFRAME_prefix': map.map_WIREFRAME_prefix,
                            # 'map_WIREFRAME_use_preview' : map.map_WIREFRAME_use_preview,
                            'map_wireframemask_line_thickness': map.map_wireframemask_line_thickness,
                            'map_wireframemask_use_invert': map.map_wireframemask_use_invert,
                        }

                        # set
                        for map_key in map_data:
                            setattr(new_map, map_key, map_data[map_key])

                # store container data class index
                container_index = uni_c_index if uni_c_index != -1 else index
                self.bake_objects_indexes[index] = container_index

                # skip if has no maps or not baked
                if len(container.global_maps) == 0 or container.global_use_bake is False:
                    continue

                # get output_filepath
                if container.bake_save_internal:
                    output_filepath = None
                else:
                    output_filepath = bpy.path.abspath(
                        container.bake_output_filepath)

                    if not all([os.path.exists(output_filepath), os.path.isdir(output_filepath)]):
                        output_filepath = None
                        msg = ("Invalid Bake Output Filepath for "
                               + f"{object.global_object_name}, baking "
                               + "internally")
                        self.report_msg('WARNING', msg)

                    # create subfolder for baked maps if bake_create_subfolder is true
                    elif container.bake_create_subfolder:
                        dir_name = container.bake_subfolder_name
                        path = os.path.join(bpy.path.abspath(
                            container.bake_output_filepath), dir_name)
                        try:
                            os.makedirs(path, exist_ok=True)
                            output_filepath = path
                        except OSError as error:
                            msg = ("Cannot create subfolder for "
                                   + f"{object.global_object_name} due to "
                                   + f"{error}, will use output filepath")
                            self.report({'WARNING'}, msg)

                # add maps to bake_images' current object shell
                for map in object.global_maps:
                    image_name = ""
                    image_name_decal = ""

                    if map.global_use_bake:
                        batch_name_preview = BM_ITEM_PROPS_bake_batchname_GetPreview(
                            container, context, object, map, index)
                        image_name = self.bake_image_getnewname(
                            context, batch_name_preview, output_filepath)

                        d_prefix = container.hl_decals_separate_texset_prefix
                        batch_name_preview_decal = BM_ITEM_PROPS_bake_batchname_GetPreview(
                            container, context, object, map, index, d_prefix)
                        image_name_decal = self.bake_image_getnewname(
                            context, batch_name_preview_decal, output_filepath)

                    self.bake_images[index][0].append(image_name)
                    self.bake_images[index][1].append(image_name_decal)

                # (reassign images based of maps in channel packs)
                # (do not need! because should have different images to then)
                # (be able to pack into one)

                # collect bake_channel_pack_data
                chnlp_data_index = -1
                for channel_pack in container.chnlp_channelpacking_table:
                    chnlp_type = channel_pack.global_channelpack_type
                    type_data = {
                        'R1G1B': ['R', 'G', 'B'],
                        'RGB1A': ['RGB', 'A'],
                        'R1G1B1A': ['R', 'G', 'B', 'A'],
                    }
                    # collect map indexes that are in the channel_pack
                    maps_images_reassign = []
                    for prop in type_data[chnlp_type]:
                        value = getattr(channel_pack, "%s_map_%s" %
                                        (chnlp_type, prop))
                        use = getattr(channel_pack, "%s_use_%s" %
                                      (chnlp_type, prop))
                        try:
                            int(value)
                        except ValueError:
                            map_index = 'NONE'
                            use = False
                        else:
                            map_index = int(value) - 1
                        maps_images_reassign.append([use, map_index])
                    if len(maps_images_reassign) == 0:
                        continue
                    self.bake_channel_pack_data[index].append(['', []])
                    chnlp_data_index += 1
                    self.bake_channel_pack_data[index][chnlp_data_index][0] = chnlp_type
                    # add data
                    for map_image_index in maps_images_reassign:
                        self.bake_channel_pack_data[index][chnlp_data_index][1].append(
                            map_image_index)

                if object.global_use_bake is False:
                    continue
                # source object operations
                source_object = self.bake_scene_object_get_and_setactive(
                    context, object.global_object_name)

                # get uv_active_layer to determine if need to run auto unwrap
                if len(source_object.data.uv_layers):
                    uv_active_layer = ""
                else:
                    uv_active_layer = 'NONE_AUTO_CREATE'

                run_auto_uv_unwrap = container.uv_use_auto_unwrap
                run_auto_uv_unwrap = True if uv_active_layer == 'NONE_AUTO_CREATE' else run_auto_uv_unwrap
                # do not run auto unwrap if bake_target is VERTEX_COLORS
                if container.uv_use_unique_per_map:
                    has_not_vrtx_bake_target = any(
                        True for map in container.global_maps if map.uv_bake_target != 'VERTEX_COLORS')
                else:
                    has_not_vrtx_bake_target = not (
                        container.uv_bake_target == 'VERTEX_COLORS')
                run_auto_uv_unwrap = has_not_vrtx_bake_target and run_auto_uv_unwrap

                run_csh_triangulate = container.csh_use_triangulate_lowpoly
                run_csh_recalc_normals = container.csh_use_lowpoly_recalc_normals
                run_csh_smooth = container.csh_lowpoly_use_smooth
                run_csh_recalc_normals = container.csh_use_lowpoly_recalc_normals
                run_csh_smooth_highpoly = container.csh_highpoly_use_smooth
                run_csh_recalc_normals_highpoly = container.csh_use_highpoly_recalc_normals

                # entering edit mode
                if any([run_auto_uv_unwrap, run_csh_recalc_normals, run_csh_smooth]):
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='VERT')
                    bpy.ops.mesh.select_all(action='SELECT')

                # run auto_uv_unwrap
                if run_auto_uv_unwrap:
                    # create new uv layer if just auto unwrapping
                    if uv_active_layer != 'NONE_AUTO_CREATE':
                        new_uv = source_object.data.uv_layers.new()
                        source_object.data.uv_layers.active = new_uv
                    angle_limit = container.uv_auto_unwrap_angle_limit
                    island_margin = container.uv_auto_unwrap_island_margin
                    scale_to_bounds = container.uv_auto_unwrap_use_scale_to_bounds
                    self.bake_object_auto_unwrap(
                        context, source_object, angle_limit, island_margin, scale_to_bounds)
                # run csh triangulate
                if run_csh_triangulate:
                    self.bake_object_triangulate_modifier(
                        context, object, source_object)
                # run csh reset lowpoly normals
                if run_csh_recalc_normals:
                    self.bake_object_mesh_recalc_normals()
                # run csh smooth
                if run_csh_smooth:
                    smooth_type = container.csh_lowpoly_smoothing_groups_enum
                    angle = container.csh_lowpoly_smoothing_groups_angle
                    name_contains = container.csh_lowpoly_smoothing_groups_name_contains
                    smooth_shade = self.bake_object_mesh_smooth(
                        source_object, smooth_type, angle, name_contains)
                    if smooth_shade:
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.shade_smooth()
                # run csh smooth for highpolies
                if any([run_csh_smooth_highpoly, run_csh_recalc_normals_highpoly]):
                    if object.hl_use_unique_per_map:
                        for map in object.global_maps:
                            for highpoly in map.hl_highpoly_table:
                                # smooth highpoly
                                self.bake_object_operate_highpoly_smoothing(
                                    context, container, highpoly, run_csh_recalc_normals_highpoly, run_csh_smooth_highpoly)

                    else:
                        for highpoly in object.hl_highpoly_table:
                            # smooth highpoly
                            self.bake_object_operate_highpoly_smoothing(
                                context, container, highpoly, run_csh_recalc_normals_highpoly, run_csh_smooth_highpoly)

                # exiting edit mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # constructing bake_images_ad_data[]
                # 0 - udims start_tile_index
                # 1 - udims end_tile_index
                # 2 - source object name
                # 3 - marked True when baked
                # 4 - marked True if vrtxcolorlayer baked
                # 5 - stands for the image index indicating when it's ready for denoise
                # 6 - marked False when image is not available for Channel Pack (marked after chnlp to exclude recursive chnlp)
                # 7 - True when baking image for the first time (for use_clear), False otherwise
                # 8 - True when image should be baked internally
                # set udim tiles start and end indexes
                for map_index, map in enumerate(container.global_maps):
                    # get uv layer
                    if container.nm_uni_container_is_global:
                        uv_layer = object.uv_active_layer
                    elif container.uv_use_unique_per_map:
                        uv_layer = map.uv_active_layer
                    else:
                        uv_layer = object.uv_active_layer
                    # get uv type
                    if container.uv_use_unique_per_map:
                        uv_type = map.uv_type
                    else:
                        uv_type = container.uv_type
                    # get out container
                    out_container = container
                    if container.out_use_unique_per_map:
                        out_container = map

                    # get tiles size
                    start, end = self.bake_object_get_udim_tiles_indexes(
                        out_container, source_object, uv_layer, uv_type)
                    try:
                        self.bake_images_ad_data[self.bake_images[index]
                                                 [0][map_index]]
                        self.bake_images_ad_data[self.bake_images[index]
                                                 [1][map_index]]
                    except KeyError:
                        self.bake_images_ad_data[self.bake_images[index][0][map_index]] = [
                            start, end, object.global_object_name, False, False, 0, True, True, False]
                        self.bake_images_ad_data[self.bake_images[index][1][map_index]] = [
                            start, end, object.global_object_name, False, False, 0, True, True, False]
                    else:
                        shell0 = self.bake_images_ad_data[self.bake_images[index]
                                                          [0][map_index]]
                        if start > shell0[0]:
                            start = shell0[0]
                        if end < shell0[1]:
                            end = shell0[1]

                        self.bake_images_ad_data[self.bake_images[index][0][map_index]] = [
                            start, end, object.global_object_name, False, False, 0, True, True, False]
                        self.bake_images_ad_data[self.bake_images[index][1][map_index]] = [
                            start, end, object.global_object_name, False, False, 0, True, True, False]

        # uv repacks and bake_images reassign
        for texset in context.scene.bm_props.global_texturesets_table:
            # for self.control == 'BAKE_THIS'
            if len(prepare_index):
                check1 = True
                check2 = False
                if not any(True for object in texset.global_textureset_table_of_objects if object.global_source_object_index in prepare_index):
                    check1 = False
                for object in texset.global_textureset_table_of_objects:
                    if check2:
                        break
                    for subobject in object.global_object_name_subitems:
                        if subobject.global_source_object_index in prepare_index:
                            check2 = True
                            break
                if not any([check1, check2]):
                    continue

            objects_images_reassign = []
            run_repack = False

            if texset.uvp_use_uv_repack:
                self.bake_scene_objects_unselect(context)
            for object in texset.global_textureset_table_of_objects:
                bpy.ops.object.mode_set(mode='OBJECT')
                source_container = context.scene.bm_table_of_objects[object.global_source_object_index]
                if source_container.nm_is_universal_container:
                    for subobject in object.global_object_name_subitems:
                        if self.object_get(context, subobject.global_object_name) is None:
                            continue
                        if subobject.global_object_include_in_texset is False:
                            continue
                        # uv repack
                        if texset.uvp_use_uv_repack:
                            source_object = self.bake_scene_object_get_and_select(
                                context, subobject.global_object_name)
                            run_repack = True
                        # image reassign collect index
                        if subobject.global_source_object_index != -1:
                            objects_images_reassign.append(
                                subobject.global_source_object_index)

                else:
                    if self.object_get(context, object.global_object_name) is None:
                        continue
                    # uv repack
                    if texset.uvp_use_uv_repack:
                        source_object = self.bake_scene_object_get_and_select(
                            context, object.global_object_name)
                        run_repack = True
                    # image reassign collect index
                    if object.global_source_object_index != -1:
                        objects_images_reassign.append(
                            object.global_source_object_index)

            # run repack
            if texset.uvp_use_uv_repack and run_repack:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='VERT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.select_all(action='SELECT')

                rotate = texset.uvp_use_islands_rotate
                margin = texset.uvp_pack_margin
                run_average_islands_scale = texset.uvp_use_average_islands_scale

                if run_average_islands_scale:
                    bpy.ops.uv.average_islands_scale()

                if self._version_current >= (3, 0, 0):
                    bpy.ops.uv.pack_islands(
                        udim_source='CLOSEST_UDIM', rotate=rotate, margin=margin)
                else:
                    bpy.ops.uv.pack_islands(rotate=rotate, margin=margin)
                bpy.ops.object.mode_set(mode='EDIT', toggle=True)

            # images reassign
            if len(objects_images_reassign) == 0:
                continue
            maps_match_type = context.scene.bm_props.global_bake_match_maps_type
            # for not reassigning the same map more than once
            maps_marked = []
            for object_index, object in enumerate(context.scene.bm_table_of_objects):
                if object_index in objects_images_reassign:
                    maps_marked.append([False] * len(object.global_maps))
                else:
                    maps_marked.append([])

            # reassign
            for global_object_index in objects_images_reassign:
                global_object_maps = context.scene.bm_table_of_objects[global_object_index].global_maps
                for map_index, map in enumerate(global_object_maps):
                    if maps_marked[global_object_index][map_index]:
                        continue

                    map_prefix = getattr(map, "map_%s_prefix" %
                                         map.global_map_type)
                    try:
                        self.bake_images[global_object_index][0][map_index]
                        self.bake_images[global_object_index][1][map_index]
                    except IndexError:
                        continue
                    new_image = self.bake_images[global_object_index][0][map_index]
                    new_image_decal = self.bake_images[global_object_index][1][map_index]

                    for object_index in objects_images_reassign:
                        object_maps = context.scene.bm_table_of_objects[object_index].global_maps

                        reassigned = False

                        # try to reassign map with the same map_prefix
                        if maps_match_type in ['MAP_PREFIX', 'MAP_PREFIX_AND_TYPE']:
                            for map1_index, map1 in enumerate(object_maps):
                                if maps_marked[object_index][map1_index]:
                                    continue
                                if getattr(map1, "map_%s_prefix" % map1.global_map_type) == map_prefix:
                                    try:
                                        self.bake_images[object_index][0][map1_index]
                                        self.bake_images[object_index][1][map1_index]
                                    except IndexError:
                                        continue
                                    self.bake_images[object_index][0][map1_index] = new_image
                                    self.bake_images[object_index][1][map1_index] = new_image_decal
                                    maps_marked[object_index][map1_index] = True
                                    reassigned = True
                                    break

                        if reassigned:
                            maps_marked[global_object_index][map_index] = True
                            continue

                        # if reassign with the same map_prefix was unsuccessful
                        # try to reassign map with the same map_type
                        if maps_match_type in ['MAP_TYPE', 'MAP_PREFIX_AND_TYPE']:
                            for map1_index, map1 in enumerate(object_maps):
                                if maps_marked[object_index][map1_index]:
                                    continue
                                if map1.global_map_type == map.global_map_type:
                                    try:
                                        self.bake_images[object_index][0][map1_index]
                                        self.bake_images[object_index][1][map1_index]
                                    except IndexError:
                                        continue
                                    self.bake_images[object_index][0][map1_index] = new_image
                                    self.bake_images[object_index][1][map1_index] = new_image_decal
                                    maps_marked[object_index][map1_index] = True
                                    reassigned = True
                                    break

                        if reassigned:
                            maps_marked[global_object_index][map_index] = True

        # mark images available for post-processing
        for key in self.bake_images_ad_data:
            index = 0
            for obj_shell in self.bake_images:
                for images_shell in obj_shell:
                    for image_name in images_shell:
                        if image_name == key:
                            index += 1
            self.bake_images_ad_data[key][5] = index
            self.bake_images_ad_data[key][7] = True

        # XXX print all images
        # print("\n\nImages after texsets:\n")
        # for obj_shell in self.bake_images:
        #     for i, images_shell in enumerate(obj_shell):
        #         print(i, images_shell)
        # print("\n\Channel Pack data:\n")
        # for obj_shell in self.bake_channel_pack_data:
        #     print(obj_shell)
        # raise RuntimeError

    def execute(self, context):
        # call after UI or direct call (from terminal)

        # block bake_ot call in the ui
        # context.scene.bm_props.global_bake_available = False

        # status variables
        self.bake_cancel = False
        self.bake_error = False
        self.bake_done = False
        self.baking_now = False
        self.rendering_decal = False
        self.wait_handle_object = False
        self.waiting_start_bake = False
        self.map_skip_error_raised = False  # not used yet

        # variables
        self.hidden_objects_names = []
        self.hidden_custom_objects_names = []
        self.bake_images = []
        self.bake_objects_indexes = [-1] * len(
            context.scene.bm_table_of_objects)
        self.bake_object_index = -1
        self.bake_object_map_index = 0
        self.bake_object_map_highpoly_index = 0
        self.bake_current_container = None
        self.bake_current_object = None
        self.bake_current_source_object = None
        self.bake_current_source_cage = None
        self.bake_current_source_highpolies = None
        self.bake_current_map = None
        self.bake_image = None
        self.bake_arguments = None
        # to set tiles indexes, origin map_index, and baked status
        self.bake_images_ad_data = {}
        self.bake_image_type = 'IMAGE_TEXTURES'  # default value
        # channel pack data
        self.bake_channel_pack_data = []

        # local varibles for restoring
        self.bake_object_materials_restore_args = None
        self.bake_object_disp_remove_multires = False
        self.bake_object_disp_multires_levels = -1
        self.bake_object_mods_show = {}
        self.bake_object_disp_multires = None
        self.bake_current_source_object_bm_image_nodes = []

        self.Cgin_old_settings = []
        self.CMgin_old_settings = []
        self.w_muted_nodes = set()

        # time record
        now = time.time()
        self.start_time = now
        self.last_report_time = now - self.report_delay
        self.last_map_start_time = now

        # prepare scene
        self.bake_scene_settings(context, 'SET', data_bake=False)

        colorspace_ok, current_colorspace, need_colorspace = self.bake_scene_settings_colorspace(
            context)
        if not colorspace_ok:
            msg = (f"Chosen {need_colorspace} color space not supported. Will "
                   + f"use default: {current_colorspace}")
            self.report_msg('ERROR', msg)

            msg = "Baked textures will have default color spaces."
            self.report_msg('WARNING', msg)

        # prepare all objects
        prepare_index = []
        if self.control == 'BAKE_THIS':
            prepare_index.append(context.scene.bm_props.global_active_index)

        try:
            self.bake_prepare_all_objects(context, prepare_index)

        except KeyboardInterrupt:
            msg = "Bake Process Interrupted by user - execution aborted"
            self.report_msg('ERROR', msg)

            self.exit_common(context)
            return {'FINISHED'}

        except Exception as error:
            msg = (f"Code Execution Error: {error}.\nPlease, contact support: "
                   + "click 'Support' in the Help panel (below Bake buttons).")
            self.report_msg('ERROR', msg)

            print(("\nBakeMaster Code Error Traceback:\n "
                   + "%s\n\n" % traceback.format_exc()))

            self.exit_common(context)
            return {'FINISHED'}

        # exit bake if no bake_images formed
        bake_images_formed = False
        for object_shell in self.bake_images:
            bake_images_formed = len(object_shell[0])
            if bake_images_formed:
                break
            bake_images_formed = len(object_shell[1])
            if bake_images_formed:
                break

        # proceeding bake
        if bake_images_formed:
            cls = self.__class__

            if cls._timer is None:
                wm = context.window_manager
                self._timer = wm.event_timer_add(
                    self.wait_delay, window=context.window)
                wm.modal_handler_add(self)
                cls._handler = self

            self.report_bake_progress()

            return {'RUNNING_MODAL'}

        # nothing to bake
        else:
            self.report({'ERROR'}, "Nothing to bake")
            print("BakeMaster Bake Invalid: Nothing to bake")
            self.exit_common(context)
            return {'FINISHED'}

    def invoke(self, context, _):
        # call from the UI

        bake_abort_message = self.bake_poll(context)

        if bake_abort_message is None:
            # wm = context.window_manager
            # return wm.invoke_props_dialog(self, width=500)
            return self.execute(context)

        else:
            print("BakeMaster Bake Invalid: %s" % bake_abort_message)
            self.report({'ERROR'}, bake_abort_message)
            return {'FINISHED'}
