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

bl_info = {
    "name": "Image Changer",
    "author": "Dalai Felinto (dfelinto)",
    "version": (1,0),
    "blender": (2, 6, 8),
    "location": "Properties > Texture",
    "description": "Change your texture everyframe",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Texture"}

# ########################################################
# Image Changer
# (note: barely based in an old script, completely remodernized to Blender 2.5)
#
# last update: August, 2013
#
# Dalai Felinto (dfelinto)
# www.dalaifelinto.com
# www.blendernetwork.org/dalai-felinto
#
# Rio de Janeiro - Brasil
# ########################################################

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, StringProperty, IntProperty
import os


class DATA_PT_image_swapper(bpy.types.Panel):
    bl_label = "Image Swapper"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        if not context.texture or context.texture.type != 'IMAGE':
            return False
        return True

    def draw_header(self, context):
        texture = context.texture
        self.layout.prop(texture, "image_animate", text="")

    def draw(self, context):
        layout = self.layout
        texture = context.texture

        col = layout.column()
        col.active = texture.image_animate
        col.prop(texture, "image_slide")
        col.prop(texture, "use_custom_hash")
        if texture.use_custom_hash:
            col.prop(texture, "image_hash")


def customHash(self, context):
    '''changes the custom hash option'''
    if self.image and           \
       self.image.filepath != "":

        if self.use_custom_hash:
            self.image_hash = calculateHash(self.image.filepath)


def slideUpdate(self, context):
    '''updates'''
    # extract properties from the texture object
    if self.type == 'IMAGE' and       \
       self.image_animate and         \
       self.image and                 \
       self.image.filepath != "":

        if self.use_custom_hash:
            if self.image_hash:
                image_hash = self.image_hash
            else:
                return

        # automatically calculate the hash
        else:
            image_hash = calculateHash(self.image.filepath)

        imageChanger(self, self.image_slide, image_hash)


def calculateHash(filepath):
    '''copy from blender code
       it's the same calculation
       that goes on when using a
       sequence of images'''
    import re
    pattern = re.compile('[0-9]+')

    filepath = os.path.basename(filepath)
    match = re.search(pattern, filepath)

    if match:
        start,end = match.span()
        return "%s%%0%dd%s" % (filepath[:start], end - start, filepath[end:])
    else:
        return ""


def imageChanger(texture, image_slide, image_hash):
    ''''''
    image = texture.image

    # it needs to be absolute otherwise it fails on windows
    filepath = bpy.path.abspath(image.filepath)
    if filepath != image.filepath:
        relative = True
    else:
        relative = False

    basedir = os.path.dirname(filepath)
    if image_hash:
        filename = image_hash % image_slide
    else:
        filename = os.path.basename(filepath)

    filepath = os.path.join(basedir, filename)

    if relative:
        filepath = bpy.path.relpath(filepath)

    image.filepath = filepath
# image automatically reloaded


@persistent
def update_textures(context):
    for tex in bpy.data.textures:
        if tex.image_animate:
            # hack to force call of python update function
            tex.image_slide = tex.image_slide


def register_callbacks():
    bpy.app.handlers.frame_change_post.append(update_textures)


def unregister_callbacks():
    bpy.app.handlers.frame_change_post.remove(update_textures)


def register():
    bpy.types.Texture.image_animate = BoolProperty(
        name="Animate",
        default=False,
        description="Animate texture",
        update=slideUpdate)

    bpy.types.Texture.use_custom_hash = BoolProperty(
        name="Custom Hash",
        default=False,
        description="Customize how the formatting of the other frames",
        update=customHash)

    bpy.types.Texture.image_hash = StringProperty (
        name="Hash",
        description="String formatting for the filename. Use python notation (e.g. \"img-%03d.png\" will be \"img-003.png\" or \"img-9999.png\")",
        update=slideUpdate)

    bpy.types.Texture.image_slide = IntProperty(
        name="Slide",
        min=0,
        subtype='UNSIGNED',
        description="Slide number to use in this frame",
        update=slideUpdate)

    bpy.utils.register_module(__name__)
    register_callbacks()


def unregister():
    del bpy.types.Texture.image_hash
    del bpy.types.Texture.image_slide
    del bpy.types.Texture.image_animate
    del bpy.types.Texture.use_custom_hash
    bpy.utils.unregister_module(__name__)
    unregister_callbacks()


if __name__ == "__main__":
    register()
