import pedpy
import jupedsim as jps
import shapely
import pandas as pd
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import matplotlib.pyplot as plt 
import pathlib
from descartes import PolygonPatch

data = pd.read_csv("./Geometries/Walkable.csv")
i = 0
area = []
while i < len(data["x"]):
    area.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Walls1.csv")
i = 0
wall1 = []
while i < len(data["x"]):
    wall1.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Walls2.csv")
i = 0
wall2 = []
while i < len(data["x"]):
    wall2.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Column1.csv")
i = 0
col1 = []
while i < len(data["x"]):
    col1.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Column2.csv")
i = 0
col2 = []
while i < len(data["x"]):
    col2.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Column3.csv")
i = 0
col3 = []
while i < len(data["x"]):
    col3.append((data["x"][i], data["y"][i]))
    i += 1

data = pd.read_csv("./Geometries/Exit1.csv")
i = 0
exit1 = []
while i < len(data["x"]):
    exit1.append((data["x"][i], data["y"][i]))
    i += 1
exit1 = Polygon(exit1)

data = pd.read_csv("./Geometries/Exit2.csv")
i = 0
exit2 = []
while i < len(data["x"]):
    exit2.append((data["x"][i], data["y"][i]))
    i += 1
exit2 = Polygon(exit2)

walkable = Polygon(area, holes=[wall1[::-1], wall2[::-1], col1[::-1], col2[::-1], col3[::-1]])

import sqlite3
from matplotlib.animation import FuncAnimation

#Connect to the SQLite database
db_path = 'Trajectories/Final.sqlite'
conn = sqlite3.connect(db_path)

query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)

conn.close()

# print(df.head())
fig, ax = plt.subplots()
scat = ax.scatter([], [])
def init():
    ax.set_xlim(df['pos_x'].min(), df['pos_x'].max())
    ax.set_ylim(df['pos_y'].min(), df['pos_y'].max())
    return scat,

def animate(i):
    current_frame = df[df['frame'] == i]
    scat.set_offsets(current_frame[['pos_x', 'pos_y']].values)
    return scat,

num_frames = df['frame'].max()
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=10, blit=True)

plot_polygon(walkable, color="grey", linewidth=0.5)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")

plt.show()

