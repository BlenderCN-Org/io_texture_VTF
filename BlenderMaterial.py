import bpy
try:
    from VMT import VMT
    from VTF import VTF
except:
    from .VMT import VMT
    from .VTF import VTF

class BlenderMaterial:
    def __init__(self,vmt:VMT):
        vmt.parse()
        self.vmt = vmt
        self.textures = {}
    def load_textures(self):
        for key,texture in self.vmt.textures.items():
            vtf = VTF(texture)
            vtf.load()
            image = vtf.read_image()
            if image:
                self.textures[key] = image

    def create_material(self,override = False):
        mat_name = self.vmt.filepath.name(True)
        if bpy.data.materials.get(mat_name) and not override:
            return 'EXISTS'
        bpy.data.materials.new(mat_name)
        mat = bpy.data.materials.get(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.remove(nodes.get('Diffuse BSDF',None))
        out = nodes.get('ShaderNodeOutputMaterial',None)
        if not out:
            out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (0,0)
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (100,0)
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs['Surface'])
        if self.textures.get('basetexture',None):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('basetexture')
            tex.location = (200, -100)
            mat.node_tree.links.new(tex.outputs["Color"],bsdf.inputs['Base Color'])
        if self.textures.get('bumpmap',None):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('bumpmap')
            tex.location = (200, -50)
            tex.color_space = 'NONE'
            normal = nodes.new("ShaderNodeNormalMap")
            normal.location = (150,-50)
            mat.node_tree.links.new(tex.outputs["Color"], normal.inputs['Color'])
            mat.node_tree.links.new(normal.outputs["Normal"], bsdf.inputs['Normal'])
        if self.textures.get('phongexponenttexture',None):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('phongexponenttexture')
            tex.location = (200, 0)
            # mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs['Base Color'])

