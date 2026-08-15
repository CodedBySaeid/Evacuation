import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.plotting import plot_line, plot_points

# from figures import SIZE, BLACK, BLUE, GRAY, YELLOW, set_limits

fig = plt.figure(1, dpi=90)

# 1: simple line
ax = fig.add_subplot(121)
line = LineString([(0, 0), (1, 1), (0, 2), (2, 2), (3, 1), (1, 0)])

plot_line(line, ax=ax, add_points=False, alpha=0.7)
plot_points(line, ax=ax, alpha=0.7)
plot_points(line.boundary, ax=ax)

ax.set_title('a) simple')

# set_limits(ax, -1, 4, -1, 3)

# 2: complex line
ax = fig.add_subplot(122)
line2 = LineString([(0, 0), (1, 1), (0, 2), (2, 2), (-1, 1), (1, 0)])

plot_line(line2, ax=ax, add_points=False, alpha=0.7)
plot_points(line2, ax=ax, alpha=0.7)
plot_points(line2.boundary, ax=ax)

ax.set_title('b) complex')

# set_limits(ax, -2, 3, -1, 3)

plt.show()
