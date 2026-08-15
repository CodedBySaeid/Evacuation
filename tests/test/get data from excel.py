# import jupedsim as jps 
# import numpy as np 
# SHAPELY DOC
import matplotlib.pyplot as plt
from shapely import Polygon, GeometryCollection
from shapely.plotting import plot_polygon, plot_line, plot_points
import pandas as pd 

data = pd.read_csv("test.csv")
x = data["x"]
y = data["y"]
point_list = []
i = 0
while i<len(x):
    point_list.append((x[i], y[i]))
    i += 1

shape1 = Polygon(point_list)
# shape2 = Polygon([(945.49,541.53),(941.6,541.53),(941.6,546.58),(943.99,546.58),(943.99,547.58),(944.29,547.58),(944.99,547.58),(945.29,547.58),(945.49,547.58),(945.49,541.53)])
# area = GeometryCollection(shape1.union(shape2))
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
# plot_polygon(area, color="g")


plt.show()

