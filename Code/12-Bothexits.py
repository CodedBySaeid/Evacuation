import jupedsim as jps
import pandas as pd
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import matplotlib.pyplot as plt 
import pathlib, random, pedpy , shapely
import numpy as np
random.seed(1)

def load_coordinates(file_path):
    data = pd.read_csv(file_path)
    return list(zip(data["x"], data["y"]))

# Load all geometries
area = load_coordinates("./Geometries/Walkable.csv")

wall1 = load_coordinates("./Geometries/Walls1.csv")
wall2 = load_coordinates("./Geometries/Walls2.csv")
holes = [wall1[::-1], wall2[::-1]]

cols = load_coordinates("./Geometries/Columns.csv")

cols_list = [cols[i:i+4] for i in range(0, len(cols), 4)]
for i in range(0, len(cols_list)):
    holes.append(cols_list[i][::-1])

# COMPLEX ----------------------------------------------------------
# desk = load_coordinates("./Geometries/RoomDesks.csv")
# desk_list = [desk[i:i+4] for i in range(0, len(desk), 4)]

# for i in range(0, len(desk_list)):
#     desk_list[i].append(desk_list[i][0])
# j = 0
# for i in range(0, len(desk_list)):
#     if j % 3 == 0:
#         holes.append(desk_list[i][::-1])
#     else:
#         holes.append(desk_list[i])
#     j += 1
# --------------------------------------------------------------------
# SIMPLE -------------------------------------------------------------
desk1 = load_coordinates("./Geometries/Boundingbox1.csv")
desk2 = load_coordinates("./Geometries/Boundingbox2.csv")
desk3 = load_coordinates("./Geometries/Boundingbox3.csv")
desk4 = load_coordinates("./Geometries/Boundingbox4.csv")
desk5 = load_coordinates("./Geometries/Boundingbox5.csv")


desk1_list = [desk1[i:i+4] for i in range(0, len(desk1), 4)]
desk2_list = [desk2[i:i+4] for i in range(0, len(desk2), 4)]
desk3_list = [desk3[i:i+4] for i in range(0, len(desk3), 4)]
desk4_list = [desk4[i:i+4] for i in range(0, len(desk4), 4)]
desk5_list = [desk5[i:i+4] for i in range(0, len(desk5), 4)]


desk_lists = [desk1_list, desk2_list, desk3_list, desk4_list, desk5_list]

for desk in desk_lists:
    for sublist in desk:
        sublist.append(sublist[0])

for desk in desk_lists:
    for sublist in desk:
        holes.append(sublist[::-1])
# -----------------------------------------------------------------------
walkable = Polygon(area, holes)

exit1 = Polygon(load_coordinates("./Geometries/Exit1.csv"))
exit2 = Polygon(load_coordinates("./Geometries/Exit2.csv"))

spawn1 = load_coordinates("./Geometries/Spawn1.csv")
spawn2 = load_coordinates("./Geometries/Spawn2.csv")
spawn3 = load_coordinates("./Geometries/Spawn3.csv")
spawn4 = load_coordinates("./Geometries/Spawn4.csv")
spawn5 = load_coordinates("./Geometries/Spawn5.csv")

spawn1_poly = shapely.Polygon(spawn1)
spawn2_poly = shapely.Polygon(spawn2)
spawn3_poly = shapely.Polygon(spawn3)
spawn4_poly = shapely.Polygon(spawn4)
spawn5_poly = shapely.Polygon(spawn5)

plot_polygon(walkable)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")
plot_points(spawn1_poly, color="blue")
plot_points(spawn2_poly, color="blue")
plot_points(spawn3_poly, color="blue")
plot_points(spawn4_poly, color="blue")
plot_points(spawn5_poly, color="blue")

trajectory_file = "./Trajectories/Final.sqlite"
simulation_sfm = jps.Simulation(
    model=jps.SocialForceModel(),
    geometry=walkable,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

# Define constants
SWITCH_DISTANCE = 0.5
WAYPOINT_DISTANCE = 0.5
AGENT_RADIUS = 0.03
AGENT_COUNT = 25

# Define function to create journeys with specified waypoints and exits
def create_journey(simulation_sfm, switch_point, waypoints, exit1, exit2):
    switch_id = simulation_sfm.add_waypoint_stage(switch_point, SWITCH_DISTANCE)
    waypoint_id = simulation_sfm.add_waypoint_stage(waypoints, WAYPOINT_DISTANCE)
    
    exit1_id = simulation_sfm.add_exit_stage(exit1.exterior.coords[:-1])
    journey1 = jps.JourneyDescription([switch_id, waypoint_id, exit1_id])
    journey1.set_transition_for_stage(switch_id, jps.Transition.create_fixed_transition(waypoint_id))
    journey1.set_transition_for_stage(waypoint_id, jps.Transition.create_fixed_transition(exit1_id))
    journey1_id = simulation_sfm.add_journey(journey1)

    exit2_id = simulation_sfm.add_exit_stage(exit2.exterior.coords[:-1])
    journey2 = jps.JourneyDescription([switch_id, waypoint_id, exit2_id])
    journey2.set_transition_for_stage(switch_id, jps.Transition.create_fixed_transition(waypoint_id))
    journey2.set_transition_for_stage(waypoint_id, jps.Transition.create_fixed_transition(exit2_id))
    journey2_id = simulation_sfm.add_journey(journey2)

    return switch_id, journey1_id, journey2_id

# Function to add agents with specified percentage for journey distribution
def add_agents(simulation_sfm, start_positions, switch_id, journey1_id, journey2_id, journey1_percentage=50):
    num_agents_journey1 = int(len(start_positions) * (journey1_percentage / 100))
    positions_journey1 = start_positions[:num_agents_journey1]
    positions_journey2 = start_positions[num_agents_journey1:]
    
    # Add agents for journey1
    for position in positions_journey1:
        simulation_sfm.add_agent(
            jps.SocialForceModelAgentParameters(
                stage_id=switch_id,
                journey_id=journey1_id,
                position=position,
                radius=AGENT_RADIUS,
                orientation=(-1,0)
            )
        )
    
    # Add agents for journey2
    for position in positions_journey2:
        simulation_sfm.add_agent(
            jps.SocialForceModelAgentParameters(
                stage_id=switch_id,
                journey_id=journey2_id,
                position=position,
                radius=AGENT_RADIUS,
                orientation=(1,1)
            )
        )

# Class 1:
switch_point1 = (245.63, 35.08)
waypoints1 = (245.63, 35.8)
switch_id1, journey1_id1, journey2_id1 = create_journey(simulation_sfm, switch_point1, waypoints1, exit1, exit2)
start_positions1 = random.sample(spawn1, AGENT_COUNT)
add_agents(simulation_sfm, start_positions1, switch_id1, journey1_id1, journey2_id1, journey1_percentage=10)

# Class 2:
switch_point2 = (231.8, 35.08)
waypoints2 = (231.8, 35.8)
switch_id2, journey1_id2, journey2_id2 = create_journey(simulation_sfm, switch_point2, waypoints2, exit1, exit2)
start_positions2 = random.sample(spawn2, 25)
add_agents(simulation_sfm, start_positions2, switch_id2, journey1_id2, journey2_id2, journey1_percentage=30)

# Class 3:
switch_point3 = (221.6, 35.08)
waypoints3 = (221.6, 35.8)
switch_id3, journey1_id3, journey2_id3 = create_journey(simulation_sfm, switch_point3, waypoints3, exit1, exit2)
start_positions3 = random.sample(spawn3, 30)
add_agents(simulation_sfm, start_positions3, switch_id3, journey1_id3, journey2_id3, journey1_percentage=50)

# Class 4:
switch_point4 = (209.5, 34.3)
waypoints4 = (209.5, 35.3)
switch_id4, journey1_id4, journey2_id4 = create_journey(simulation_sfm, switch_point4, waypoints4, exit1, exit2)
start_positions4 = random.sample(spawn4, 20)
add_agents(simulation_sfm, start_positions4, switch_id4, journey1_id4, journey2_id4, journey1_percentage=70)

# Class 5:
switch_point5 = (195.1, 35.1)
waypoints5 = (195.1, 35.8)
switch_id5, journey1_id5, journey2_id5 = create_journey(simulation_sfm, switch_point5, waypoints5, exit1, exit2)
start_positions5 = random.sample(spawn5, 30)
add_agents(simulation_sfm, start_positions5, switch_id5, journey1_id5, journey2_id5, journey1_percentage=90)


while (simulation_sfm.agent_count() > 0 and simulation_sfm.iteration_count() < 5000):
    simulation_sfm.iterate()


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

db_path = './Trajectories/Final.sqlite'
conn = sqlite3.connect(db_path)

query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)
conn.close()
fig, ax = plt.subplots()
scat = ax.scatter([], [])

def init():
    # ax.set_xlim(df['pos_x'].min(), df['pos_x'].max())
    # ax.set_ylim(df['pos_y'].min(), df['pos_y'].max())
    ax.set_xlim(190, 250)
    ax.set_ylim(25, 55)
    return scat,

def animate(i):
    current_frame = df[df['frame'] == i]
    scat.set_offsets(current_frame[['pos_x', 'pos_y']].values)
    return scat,

num_frames = df['frame'].max()
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=20, blit=True)

plot_polygon(walkable, color="grey", linewidth=0.5)
plot_polygon(exit1, color="red")
plot_polygon(exit2, color="red")

plt.show()

