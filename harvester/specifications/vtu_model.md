# VTK Schema

*This is a prototype implementation of an sdRDM markdown version of a VTK file.*

- [Specifications](#specifications)
  - [VTKFile](#vtkfile)
  - [UnstructuredGrid](#unstructuredgrid)
  - [Piece](#piece)
  - [DataArray](#dataarray)


A VTK file refers to a file format used in the field of scientific visualization and computer graphics. VTK stands for Visualization Toolkit, which is an open-source software system developed by Kitware Inc. The VTK file format is specifically designed to store and exchange data related to 3D computer graphics, including geometric models, volumetric data, and various attributes associated with the data.

<p align="center">
  <img width="600" src="https://raw.githubusercontent.com/mrklein/matveichev.blogspot.com/master/Cylinder/colors/Ux-Gamma-2.png">
</p>



## Specifications

### VTKFile

VTK files are typically used to represent complex 3D objects or datasets in a structured manner. They can contain information about points, vertices, polygons, lines, and other geometric elements. Additionally, VTK files support the inclusion of scalar values, vector fields, and other attributes associated with the geometry, such as color, transparency, or texture coordinates.

<details>
  <summary><i>Inspect attributes</i></summary>

- type
  - Type: string
  - Description: Type of the VTK file
  - XML: @type
- version
  - Type: string
  - Description: Version of the VTK file
  - XML: @version
- byte_order
  - Type: string
  - Description: Byte order of the file
  - XML: @byte_order
- unstructured_grid
  - Type: UnstructuredGrid
  - Description: Contains specifications and data of an unstructured grid

</details>

### UnstructuredGrid

In the context of VTK files, an unstructured grid refers to a type of data structure used to represent complex geometries that cannot be easily described by regular grids or structured meshes. It is a flexible and versatile representation that allows for the efficient storage and visualization of irregularly shaped objects or datasets.

An unstructured grid in a VTK file is composed of a collection of points and cells. The points represent the vertices or nodal positions in the 3D space, while the cells define the connectivity between these points to form the geometric elements, such as polygons or tetrahedra.

<details>
    <summary><i>Inspect attributes</i></summary>

- piece
  - Type: Piece
  - Description: Piece of an unstructured grid

</details>

### Piece

A "piece" refers to a subdivision or partitioning of a dataset into smaller, manageable parts. It is commonly used when dealing with large datasets that cannot be efficiently processed or visualized as a whole.

A VTK file can contain multiple pieces, each representing a subset of the complete dataset. Each piece corresponds to a distinct portion of the data, such as a region of space or a subset of cells or points. The purpose of dividing the dataset into pieces is to enable parallel processing or incremental loading and visualization of the data.

<details>
    <summary><i>Inspect attributes</i></summary>

- number_of_points
  - Type: int
  - Description: Number of points within this piece
  - XML: @NumberOfPoints
- number_of_cells
  - Type: int
  - Description: Number of cells within this piece
  - XML: @NumberOfCells
- points
  - Type: DataArray
  - Description: Array of points present in this piece
  - Multiple: True
  - XML: Points
- point_data
  - Type: DataArray
  - Description: Data associated to the points
  - Multiple: True
  - XML: PointData
- cells
  - Type: DataArray
  - Description: Array of cells present in this piece
  - Multiple: True
  - XML: Cells
- cell_data
  - Type: DataArray
  - Description: Data associated to the cells
  - Multiple: True
  - XML: CellData

</details>

### DataArray

A data array in a VTK file contains values corresponding to each point or cell in the dataset. The values can represent various properties or attributes, such as temperature, pressure, velocity, color, or any other information related to the dataset.

Data arrays can be categorized into two main types: point data arrays and cell data arrays.

**Point Data Arrays**

Point data arrays associate data values with individual points in the dataset. Each point in the dataset has a corresponding value in the array. For example, a point data array could represent the temperature at each point in a computational fluid dynamics simulation.

**Cell Data Arrays**

Cell data arrays associate data values with the cells of the dataset. Each cell in the dataset has a corresponding value in the array. Cell data arrays are often used to represent data that is constant within a cell but may vary between cells. For instance, a cell data array could represent the material type assigned to each cell in a structural analysis.

<details>
    <summary><i>Inspect attributes</i></summary>

- type
  - Type: string
  - Description: Data type of the data array.
  - XML: @type
- name
  - Type: string
  - Description: name of the data array.
  - XML: @Name
- format
  - Type: string
  - Description: Format of the given data
  - XML: @format
- number_of_components
  - Type: string
  - Description: Number of components within this DataArray
  - XML: @NumberOfComponents

</details>
