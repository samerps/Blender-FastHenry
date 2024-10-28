# Blender FastHenry    

**Samer Aldhaher @samerps 2024**

Blender FastHenry is a Blender 4.2 extension for creating FastHenry simulations. You can model geometries (curves) and planes, and call FastHenry executable to solve for resistance, inductance and mutual inductance. The results are displayed visually in Blender.

This extension uses geometry nodes to set some parameters, such segment width and thickness. It also use geometry nodes to visualize ports and connecting nodes between separate curve objects. 

## Installation Instructions - Windows 
- only compatible with **Blender 4.2** and above
- download extension archive package
- compile/download `fasthenry.exe` executable from [FastHenry-Sam](https://github.com/samerps/FastHenry2-Sam)
- drag and drop archive in Blender
- enable extension, go to addon preferences and set path for `fasthenry.exe` 
- Blender FastHenry should now be available in the N panel

*MacOS and Linux versions coming soon*

![preferences](docs/images/preferences.jpg) 
![N panel](docs/images/N%20panel.jpg)

## Quick Start Guide

### Simulation set-up
- watch YouTube quick start video (coming soon)
- use included predefined Geometry Node Groups for curve objects and planes
- move all **curves** required to be solved in a separate **Curves** collection
- move all **planes** required to be solved in a separate **Planes** collection
- set simulation parameters in N panel and set the curves and panels collections 
- run simulation
- any objects that do not have the right properties (ex. object type, geometry node group) will be automatically moved to a new collection named **rejected**

### Visualizing results  
- results are overlaid in the view port. Each row represents the impedance at a certain frequency of a single object along with a mutually coupled object.
- use **up/down keyboard arrow** keys to scroll through all simulation objects, the impedance results will be updated based on the object selected. A **red** bounding box is drawn around the selected object
- use the **left/right keyboard** arrow keys to scroll through all the mutually coupled objects for the current set. A **yellow** bounding box is drawn around the set mutually coupled object. 
- **blue** bounding boxes are drawn around each plane object


## Extension Capabilities 

- Separate curves within the same curve object will be considered as a single coil, the end point of each individual will be automatically  connected to the start point of the next curve. This connection will be automatically visually displayed as a single solid line. 
- Multiple curve objects will considered as mutually coupled. 
- Combine with ElectroMag Nodes to visualize magnetic field.

## Limitations

### FastHenry limitations
As this extension uses FastHenry, it is bound by the same limitations of FastHenry itself, specifically:
- cannot model material permeability, only conductors.
- FastHenry is not field solver, it will not calculate the magnetic field.
- Rectangular cross sections only, though width and thickness can be changed per segment.
- Plane objects can only be in xy, xz and yz planes, no arbitrary rotations allowed, this is a limitation of FastHenry.

### Extension limitations

- All segments within a curve will have same the width and thickness. This is in the To Do list to change
- Plane holes cannot be modelled. This is in the To Do list to change.
- Connect curve segments to planes. This is in the To Do list to change.
- Currently only one segment can connect to another. i.e. each node can only connect to two segments. This is in the To Do list to change.    

## To Do
- [ ] ability to change the length and width for each segment within a curve. 
- [ ] specify holes in planes. 
- [ ] connect curves to planes.
- [ ] connect multiple segments to nodes.

## Applications and Use Cases
- Semiconductor wire bonds and copper clip impedance extraction
- PCB layout impedance extraction
- RF Air core impedance calculation
- Core-less transformers
- Cables and wiring impedance calculation
- Bus bar impedance calculation
- Wireless power transfer coils modelling and coupling coefficient calculation  
- Induction heating coil design
