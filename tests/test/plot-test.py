# import jupedsim as jps 
# import numpy as np 
# SHAPELY DOC
import matplotlib.pyplot as plt
from shapely import Polygon, GeometryCollection
from shapely.plotting import plot_polygon, plot_line, plot_points

shape1 = Polygon([(1,0),(5,0),(5,3),(1,3),(1,0)], [[(3,1),(1.7,2),(1.3,0.5),(3,1)][::-1]]) # این ::-1 برای سوراخ انداختن فراموش نشه
shape2 = Polygon([(2,0),(4,0),(4,-2),(2,-2)])
area = GeometryCollection(shape1.union(shape2))
"""
to create a shape, first and last coordinates should be the same
to create a hole [::-1] should be used at the end of hole
"""
# GENERAL ATTRIBUTES AND METHODS
"""
print(shape1.area) #returns area
print(shape1.length) #retunes peripheral
print(shape1.bounds) #returns a tuple that bounds the object
print(shape1.distance(shape2)) #returns minimum distance
"""


# PLOTTING
plot_polygon(shape1, color="g")
plot_polygon(shape2, color="r")
# plot_polygon(area)

plt.show()

