# import jupedsim as jps 
# import numpy as np 
# SHAPELY DOC
import matplotlib.pyplot as plt
from shapely import Polygon, GeometryCollection
from shapely.plotting import plot_polygon, plot_line, plot_points

shape1 = Polygon(
    # complete area
    [
        (3.5, -2),
        (3.5, 8),
        (-3.5, 8),
        (-3.5, -2),
    ],
    holes=[
        # left barrier
        [
            (-0.7, -1.1),
            (-0.25, -1.1),
            (-0.25, -0.15),
            (-0.4, 0.0),
            (-2.8, 0.0),
            (-2.8, 6.7),
            (-3.05, 6.7),
            (-3.05, -0.3),
            (-0.7, -0.3),
            (-0.7, -1.0),
        ],
        # right barrier
        [
            (0.25, -1.1),
            (0.7, -1.1),
            (0.7, -0.3),
            (3.05, -0.3),
            (3.05, 6.7),
            (2.8, 6.7),
            (2.8, 0.0),
            (0.4, 0.0),
            (0.25, -0.15),
            (0.25, -1.1),
        ],
    ],
)
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
plot_polygon(shape1)
# plot_polygon(area, color="g")


plt.show()

