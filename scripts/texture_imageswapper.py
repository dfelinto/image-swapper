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
    "blender": (2, 6, 6),
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
# last update: August 13, 2012
#
# Dalai Felinto (dfelinto)
# www.dalaifelinto.com
# www.blendernetwork.org/member/dalai-felinto
#
# Rio de Janeiro - Brasil
# Vancouver - Canada
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
        col.prop(context.texture, "image_hash")
        col.prop(context.texture, "image_slide")

def slideUpdate(self, context):
    '''updates'''
    # extract properties from the texture object
    if self.image_animate and self.image_hash != "" and self.image and self.image.filepath != "":
        imageChanger(self, self.image_slide, self.image_hash)

def imageChanger(texture, image_slide, image_hash):
    ''''''
    if texture.type != 'IMAGE': return
    
    image = texture.image
    
    # it needs to be absolute otherwise it fails on windows
    filepath = bpy.path.abspath(image.filepath)
    if filepath != image.filepath:
        relative = True
    else:
        relative = False
    
    basedir = os.path.dirname(filepath)
    filename = image_hash % image_slide
    
    filepath = os.path.join(basedir, filename)
    
    if relative:
        filepath = bpy.path.relpath(filepath)
    
    image.filepath = filepath
# image automatically reloaded

@persistent
def update_textures(context):
    for tex in bpy.data.textures:
        if tex.image_animate:
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
        
    bpy.types.Texture.image_hash = StringProperty (
        name="Hash",
        default="%03d.png",
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
    bpy.utils.unregister_module(__name__)
    unregister_callbacks()

if __name__ == "__main__":
    register()
