import bpy
import bgl
import blf
from os import path
path_sep = path.sep

bl_info = {
    "name": "Test BGL",
    "description": "A collection of tests to make sure bgl is not buggy",
    "author": "Kilon",
    "version": (0, 0, 1),
    "blender": (2, 6, 3),
    "location": "View3D > Left panel ",
    "warning": 'warn',  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"}

running = False

if "bpy" in locals():
    import imp
    if "test_bgl" in locals():
        imp.reload(test_bgl)
    else:
        import test_bgl

texture_path = bpy.utils.script_paths()[0] + \
                          "/addons/test_bgl/".replace("/",path_sep)

def set_texture(file_name):
        """setter : set_texture(file_name). Set the texture to be used by the morph, the file_name is just the name of the file, path used is the folder images inside Ephestos in data"""
        file_path = texture_path + file_name
        return bpy.data.images.load(filepath = file_path)
texture = set_texture("weetniet.png")

iterations = 0
height = 200
width = 200

def draw(self,context):

    global iterations
    global texture
    global height
    global width
    texture.gl_load()
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 0.5)
    bgl.glLineWidth(1.5)

    #------ TEXTURE ---------#

    bgl.glBindTexture(bgl.GL_TEXTURE_2D, texture.bindcode)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)

    bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST) #GL_LINEAR seems to be used in Blender for background images

    bgl.glEnable(bgl.GL_TEXTURE_2D)

    #bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)


    bgl.glColor4f(1,1,1,1)
    bgl.glBegin(bgl.GL_QUADS)
    bgl.glTexCoord2d(0,0)
    bgl.glVertex2d(0 + iterations ,100 )
    bgl.glTexCoord2d(0,1)
    bgl.glVertex2d(0+iterations ,100 + height)
    bgl.glTexCoord2d(1,1)
    bgl.glVertex2d(0 + iterations + width, 100 + height )
    bgl.glTexCoord2d(1,0)
    bgl.glVertex2d(0 + iterations + width , 100)
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_TEXTURE_2D)
    texture.gl_free()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    #iteration = iterations + 1

class open_ephestos(bpy.types.Operator):
    bl_idname = "bg_test_button.modal"
    bl_label = "run test"
    _timer = None
    def modal(self, context, event):
        global running
        global iterations
        context.area.tag_redraw()

        if context.area:
            context.area.tag_redraw()

        if event.type == 'TIMER':
            return {'PASS_THROUGH'}

        if context.area.type == 'VIEW_3D' and running and event.type in {'ESC',} :
            print("bgl has been cancelled")
            running = False
            return  {'CANCELLED'}
        if context.area.type == 'VIEW_3D' and running and iterations > 500:
            print("I reeached 500 iterations and now will stop")
            return {'FINISHED'}

        if context.area.type == 'VIEW_3D' and running and not event.type in {'MOUSEMOVE',} :
            return  {'PASS_THROUGH'}

        iterations = iterations + 10
        print("I am at iteration",iterations)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global running
        if context.area.type == 'VIEW_3D' and running == False :

            self.cursor_on_handle = 'None'
            context.window_manager.modal_handler_add(self)

            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = context.region.callback_add(draw, (self, context), 'POST_PIXEL')
#PKHG.notneeded            self._handle_world = context.region.callback_add(draw_World, (self, context), 'POST_PIXEL')
            self._timer = context.window_manager.event_timer_add(0.01,
                    context.window)
            running = True
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "BGL Test already running ")
            return {'CANCELLED'}


class the_world(bpy.types.Operator):
    bl_idname = "world.toggle"
    bl_label = "start or stop showing the world"

    def execute(self, context):
        global world
        result = {"PASS_THROUGH"}
        sce = context.scene

        if runing_value:
            world.running = True
            sce.world_is_running = False
        else:
            world.running = False
            result = {'FINISHED'}
            sce.world_is_running = True
        return result

class bgl_test_panel(bpy.types.Panel):
    bl_label = "BGL Test"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    def draw(self, context):
        sce = context.scene
        layout = self.layout
        box = layout.box()
        box.label(text="BGL TEST")
        box.operator("bg_test_button.modal")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
