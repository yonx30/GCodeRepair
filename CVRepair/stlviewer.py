import vtkplotlib as vpl
from stl.mesh import Mesh
import stl
import numpy as np

path = r'C:\Users\yonx3\Documents\Crossbow\3DBenchySliced.stl'
savePath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model6.jpg'

class stlMesh:
    def __init__(self, filepath):
        self.filepath = filepath
        self.createMesh(self.filepath)

    def createMesh(self, filepath):
        # Read the STL using numpy-stl
        self.mesh = Mesh.from_file(filename=filepath)

    # Plot the mesh
    def plotMesh(self, colour:str="red"):
        vpl.mesh_plot(self.mesh, color=colour, fig="gcf")
        
    def viewMesh(self, focus_coord=np.array([25,0,0]), camera_coord=np.array([25,-112.5,10])):
        vpl.view(focal_point=focus_coord, camera_position=camera_coord, fig="gcf")

    # Save the figure
    def saveFig(self, savefilepath:str, magnification=1):
        print(savefilepath)
        vpl.save_fig(path=savefilepath, magnification=magnification, fig="gcf")

    def find_x_dim(self):
        minx = maxx = None # = miny = maxy = minz = maxz = 
        for p in self.mesh.points:
            # p contains (x, y, z)
            if minx is None:
                minx = p[stl.Dimension.X]
                maxx = p[stl.Dimension.X]
                # miny = p[stl.Dimension.Y]
                # maxy = p[stl.Dimension.Y]
                # minz = p[stl.Dimension.Z]
                # maxz = p[stl.Dimension.Z]
            else:
                maxx = max(p[stl.Dimension.X], maxx)
                minx = min(p[stl.Dimension.X], minx)
                # maxy = max(p[stl.Dimension.Y], maxy)
                # miny = min(p[stl.Dimension.Y], miny)
                # maxz = max(p[stl.Dimension.Z], maxz)
                # minz = min(p[stl.Dimension.Z], minz)
            
        return abs(maxx - minx)

if __name__ == "__main__":
    newMesh = stlMesh(path)
    newMesh.plotMesh()
    newMesh.viewMesh()
    newMesh.saveFig(savePath, magnification=2)

# import vtkplotlib as vpl
# from stl.mesh import Mesh
# import numpy as np

# path = r'C:\Users\yonx3\Documents\Crossbow\3DBenchy.stl'
# print(path)
# savePath = r"C:\Users\yonx3\Documents\Crossbow\model2.stl"
# print(savePath)

# def plotVPL(filePath, savePath, colour:str="red", focus_coord=np.array([0,0,0]), camera_coord=np.array([112.5,-112.5,125]), magnification=1):
#     vplmesh = Mesh.from_file(filePath=filePath,)

#     # Plot the mesh
#     vpl.mesh_plot(vplmesh, color=colour, fig="gcf")
        
#     # Change the view
#     vpl.view(focal_point=focus_coord, camera_position=camera_coord, fig="gcf")

#     # Save the figure
#     vpl.save_fig(path=savePath, magnification=magnification, fig="gcf")

# if __name__ == "__main__":
#     plotVPL(path, savePath, "red", np.array([10,10,10]), magnification=1)