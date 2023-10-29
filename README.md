# GCodeRepair
Script to repair GCode

**What it does
This kit repairs failed FDM 3D print gcodes based on the layer it failed at, to enable direct printing starting from the failed layer.

The effect is similar to power loss recovery, but for all kinds of failures involving stopping at a specific layer (and without the blobbing).

**How we built it
It first uses OpenCV enabled camera measurement of failed part, or physical measurement.

Once a measurement is obtained, it can be sent to a separate Python script that modifies the GCode model directly to enable the printer to restart from that layer.
