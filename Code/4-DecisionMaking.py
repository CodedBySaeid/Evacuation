import pedpy
import jupedsim as jps
import shapely
import pandas as pd
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import matplotlib.pyplot as plt 
import pathlib
import numpy as np

def load_coordinates(file_path):
    data = pd.read_csv(file_path)
    return list(zip(data["x"], data["y"]))

# Load all geometries
area = load_coordinates("./Geometries/Walkable.csv")
wall1 = load_coordinates("./Geometries/Walls1.csv")
wall2 = load_coordinates("./Geometries/Walls2.csv")
col1 = load_coordinates("./Geometries/Column1.csv")
col2 = load_coordinates("./Geometries/Column2.csv")
col3 = load_coordinates("./Geometries/Column3.csv")
exit1 = load_coordinates("./Geometries/Exit1.csv")
exit2 = load_coordinates("./Geometries/Exit2.csv")

exit1 = Polygon(exit1)
exit2 = Polygon(exit2)

walkable = Polygon(area, holes=[wall1[::-1], wall2[::-1], col1[::-1], col2[::-1], col3[::-1]])

peds1 = jps.distribute_by_number(polygon=walkable, number_of_agents=10, distance_to_agents=0.2, distance_to_polygon=0.2, seed=1)
peds2 = jps.distribute_by_number(polygon=walkable, number_of_agents=40, distance_to_agents=0.2, distance_to_polygon=0.2, seed=3)

peds_poly1 = shapely.Polygon(peds1)
peds_poly2 = shapely.Polygon(peds2)

plot_polygon(walkable)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")
plot_points(peds_poly1, color="yellow")
plot_points(peds_poly2, color="green")



trajectory_file = "./Trajectories/DM.sqlite"
simulation_cfsm = jps.Simulation(
    model=jps.SocialForceModel(),
    geometry=walkable,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

exit1_id = simulation_cfsm.add_exit_stage(exit1.exterior.coords[:-1])
journey1 = jps.JourneyDescription([exit1_id])
journey1_id = simulation_cfsm.add_journey(journey1)

exit2_id = simulation_cfsm.add_exit_stage(exit2.exterior.coords[:-1])
journey2 = jps.JourneyDescription([exit2_id])
journey2_id = simulation_cfsm.add_journey(journey2)

start_positions1 = peds1
for position in start_positions1:
    simulation_cfsm.add_agent(
        jps.SocialForceModelAgentParameters(
            journey_id=journey1_id,
            stage_id=exit1_id,
            position=position,
            radius=0.12,
        )
    )

start_positions2 = peds2
for position in start_positions2:
    simulation_cfsm.add_agent(
        jps.SocialForceModelAgentParameters(
            journey_id=journey2_id,
            stage_id=exit2_id,
            position=position,
            radius=0.12,
        )
    )

while (simulation_cfsm.agent_count() > 0 and simulation_cfsm.iteration_count() < 5000):
    simulation_cfsm.iterate()

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

db_path = './Trajectories/DM.sqlite'
conn = sqlite3.connect(db_path)

query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)
conn.close()
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
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=5, blit=True)

plot_polygon(walkable, color="grey", linewidth=0.5)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")

plt.show()

