import pandas as pd
import matplotlib.pyplot as plt 
import os
from shapely.geometry import Polygon
import sqlite3
from matplotlib.animation import FuncAnimation
from shapely.plotting import plot_polygon, plot_points

def load_coordinates(file_path):
    data = pd.read_csv(file_path)
    return list(zip(data["x"], data["y"]))

# Load all geometries
area = load_coordinates("./Geometries/Walkable.csv")
wall1 = load_coordinates("./Geometries/Walls1.csv")
wall2 = load_coordinates("./Geometries/Walls2.csv")
cols = load_coordinates("./Geometries/Columns.csv")
cols_list = [cols[i:i+4] for i in range(0, len(cols), 4)]
desk = load_coordinates("./Geometries/Plot/RoomDesks.csv")
desk_list = [desk[i:i+4] for i in range(0, len(desk), 4)]

for i in range(0, len(desk_list)):
    desk_list[i].append(desk_list[i][0])

holes = [wall1[::-1], wall2[::-1]]


for i in range(0, len(cols_list)):
    holes.append(cols_list[i][::-1])

j = 0
for i in range(0, len(desk_list)):
    if j % 3 != 0:
        holes.append(desk_list[i])
    else:
        holes.append(desk_list[i][::-1])
    j += 1

walkable = Polygon(area, holes)

# x, y = walkable.exterior.xy
# plt.plot(x, y, color='blue', linewidth=1)
# plt.plot(x, y, 'o', color='red', markersize=2)  # Set markersize to a smaller value
# plt.show()

exit1 = load_coordinates("./Geometries/Exit1.csv")
exit2 = load_coordinates("./Geometries/Exit2.csv")
exit1 = Polygon(exit1)
exit2 = Polygon(exit2)

db_path = './Trajectories/Final15.sqlite'
conn = sqlite3.connect(db_path)

query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)
conn.close()



fig, ax = plt.subplots()

import matplotlib.image as mpimg
background_img = mpimg.imread("mappp-Model.png")
ax.imshow(background_img, extent=[182.91, 258.49, 22.25, 64.77], aspect='auto')

scat = ax.scatter([], [])

def init():
    ax.set_xlim(190,250)
    ax.set_ylim(25,55)
    return scat,

def animate(i):
    current_frame = df[df['frame'] == i]
    scat.set_offsets(current_frame[['pos_x', 'pos_y']].values)
    return scat,

num_frames = df['frame'].max()
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=10, blit=True)

plot_polygon(walkable, color="grey", linewidth=0.1, add_points=False)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")

plt.show()










