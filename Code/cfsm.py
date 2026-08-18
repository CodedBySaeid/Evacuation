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

peds1 = jps.distribute_by_number(polygon=walkable, number_of_agents=150, distance_to_agents=0.2, distance_to_polygon=0.2, seed=1)
peds2 = jps.distribute_by_number(polygon=walkable, number_of_agents=10, distance_to_agents=0.2, distance_to_polygon=0.2, seed=7)

peds_poly1 = shapely.Polygon(peds1)
peds_poly2 = shapely.Polygon(peds2)

plot_polygon(walkable)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")
plot_points(peds_poly1, color="yellow")
plot_points(peds_poly2, color="green")



start_positions1 = peds1
trajectory_file = "./Trajectories/CFSM1.sqlite"
simulation_cfsm = jps.Simulation(
    model=jps.CollisionFreeSpeedModel(),
    geometry=walkable,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

exit1_id = simulation_cfsm.add_exit_stage(exit1)
journey1 = jps.JourneyDescription([exit1_id])
journey1_id = simulation_cfsm.add_journey(journey1)

exit2_id = simulation_cfsm.add_exit_stage(exit2)
journey2 = jps.JourneyDescription([exit2_id])
journey2_id = simulation_cfsm.add_journey(journey2)

for position in start_positions1:
    simulation_cfsm.add_agent(
        jps.CollisionFreeSpeedModelAgentParameters(
            journey_id=journey1_id,
            stage_id=exit1_id,
            position=position,
            radius=0.12,
        )
    )

start_positions2 = peds2
for position in start_positions2:
    simulation_cfsm.add_agent(
        jps.CollisionFreeSpeedModelAgentParameters(
            journey_id=journey2_id,
            stage_id=exit2_id,
            position=position,
            radius=0.12,
        )
    )
while (
    simulation_cfsm.agent_count() > 0
    and simulation_cfsm.iteration_count() < 5000
):
    simulation_cfsm.iterate()

import pedpy
from jupedsim.internal.notebook_utils import animate, read_sqlite_file

trajectory_data, walkable_area = read_sqlite_file(trajectory_file)
speed = pedpy.compute_individual_speed(traj_data=trajectory_data, frame_step=5)
speed = speed.merge(trajectory_data.data, on=["id", "frame"], how="left")

animate(trajectory_data, walkable_area)
pedpy.plot_trajectories(
    traj=trajectory_data, walkable_area=pedpy.WalkableArea(walkable)
)

import sqlite3
from matplotlib.animation import FuncAnimation

# Step 1: Connect to the SQLite database
db_path = './Trajectories/CFSM1.sqlite'
conn = sqlite3.connect(db_path)

# Step 2: Load the agent position data into a pandas dataframe
query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)

conn.close()

# Step 3: Inspect the data (Assumes columns: frame, agent_id, x, y)
print(df.head())

# Step 4: Set up the figure and axis for plotting
fig, ax = plt.subplots()


scat = ax.scatter([], [])

# Step 5: Define the initialization function
def init():
    ax.set_xlim(df['pos_x'].min(), df['pos_x'].max())
    ax.set_ylim(df['pos_y'].min(), df['pos_y'].max())
    return scat,

# Step 6: Define the animation function
def animate(i):
    current_frame = df[df['frame'] == i]
    scat.set_offsets(current_frame[['pos_x', 'pos_y']].values)
    return scat,

# Step 7: Create the animation
num_frames = df['frame'].max()  # Number of frames in the data
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=10, blit=True)

plot_polygon(walkable, color="grey", linewidth=0.5)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")

plt.show()

