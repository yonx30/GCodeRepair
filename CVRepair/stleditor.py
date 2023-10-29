import trimesh 
import pyglet # Needed for trimesh plot
import numpy as np
from PIL import Image
import io
import cv2 as cv
# import scipy # Needed for trimesh plot

path = r'C:\Users\yonx3\Documents\Crossbow\3DBenchySlice1.stl'
savePath1 = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model7.stl'
savePath2 = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model7.jpg'
savePath3 = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\splitModel1.stl'

class stlMesh:
    def __init__(self, filepath):
        # trimesh.util.attach_to_log()

        self.filepath = filepath
        self.createMesh(self.filepath)


    def createMesh(self, filepath):
        # Read the STL using numpy-stl
        self.mesh = trimesh.load(filepath)
        

    # Plot the mesh
    def plotMesh(self, colourArray:list or tuple=[0,0,0,255]):
        self.mesh.visual.face_colors = colourArray
        self.mesh.show()
        
    # Save the figure
    def saveMesh(self, savefilepath:str, mesh=None):
        if not mesh:
            self.mesh.export(savefilepath)
        else:
            mesh.export(savefilepath)

    # Save the figure
    def saveSnapshot(self, savefilepath:str, mode:str):
        try:
            # data = self.mesh.scene.save_image(resolution=(1080,1080))
            window_conf = pyglet.gl.Config(double_buffer=True, depth_size=6)
            scene = trimesh.load(self.filepath, force='scene')
            # scene.DirectionalLight.color = [0,0,255,255]
            points = np.array([self.mesh.centroid]) # Point towards CG of mesh
            points[0, 2] = points[0, 2] - 10
            if mode == "B":
                rotation = np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]) # x,y,z,magnification rotation matrix
            elif mode == "T":
                rotation = None
            scene.camera_transform = scene.camera.look_at(points=points, rotation=rotation, distance=max(self.mesh.extents)*2, center=None)
            
            data = scene.save_image(resolution=[320, 240], window_conf=window_conf)
        except:
            return
        image = np.array(Image.open(io.BytesIO(data))) 
        encode = cv.imencode('.jpg', image)
        decode = cv.imdecode(encode[1], cv.IMREAD_GRAYSCALE)
        cv.imwrite(savefilepath,decode)

    def find_x_dim(self):
        try:
            meshExtents = self.mesh.extents
        # print(meshExtents)
            return abs(meshExtents[0])
        except:
            return 0
    
    def find_z_dim(self):
        try:
            meshExtents = self.mesh.extents
            print(meshExtents)
            return abs(meshExtents[1])
        except:
            return 0
    
    def section(self, sectionHeight:int or float):
        splitSTL = trimesh.intersections.slice_mesh_plane(self.mesh, (0,0,-1), (0,0,sectionHeight))
        return splitSTL


if __name__ == "__main__":
    path = r"C:\Users\yonx3\Documents\Crossbow\Random\catstretch_voronoi updated.stl"
    savePath2 = r"C:\Users\yonx3\Documents\Crossbow\Random\catstretch_voronoi slice1.stl"
    savePath3 = r"C:\Users\yonx3\Documents\Crossbow\Random\catstretch_voronoi slice2.stl"
    newMesh = stlMesh(path)
    #newMesh.plotMesh([255,0,0,255])
    #newMesh.saveMesh(savePath1)
    #newMesh.saveSnapshot(savePath2)
    splitMesh = newMesh.section(10)
    splitMesh.export(savePath2)
    splitMesh = newMesh.section(30)
    splitMesh.export(savePath3)
    #splitMesh.show()
