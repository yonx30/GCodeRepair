import aspose.threed as a3d

scene = a3d.Scene.from_file(directory + "Input.ply")
scene.save(directory + "Output.stl", a3d.FileFormat.STLASCII)

