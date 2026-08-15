from readcsv import (
                    area,columns,wall_1,wall_2,c1_tables,c2_tables,c3_tables,c4_tables,
                    c5_tables,exit_1,exit_2,c1_spawn_points,c2_spawn_points,c3_spawn_points,
                    c4_spawn_points,c5_spawn_points,s1_spawn_points,s2_spawn_points,wall_1_plot,
                    wall_2_plot,s1_tables_plot,s2_tables_plot,c_tables_plot
                    )
import jupedsim as jps
import pandas as pd
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import matplotlib.pyplot as plt 
import pathlib, random, pedpy , shapely
import numpy as np
random.seed(1)

holes = [wall_1[::-1], wall_2[::-1]]
holes_to_plot = [wall_1_plot[::-1], wall_2_plot[::-1]]


columns_list = [columns[i:i+4] for i in range(0, len(columns), 4)]
for i in range(0, len(columns_list)):
    holes.append(columns_list[i][::-1])
    holes_to_plot.append(columns_list[i][::-1])

# Plot ----------------------------------------------------------
c_tables_plot_list = [c_tables_plot[i:i+4] for i in range(0, len(c_tables_plot), 4)]

for i in range(0, len(c_tables_plot_list)):
    c_tables_plot_list[i].append(c_tables_plot_list[i][0])
j = 0
for i in range(0, len(c_tables_plot_list)):
    if j % 3 == 0:
        holes_to_plot.append(c_tables_plot_list[i][::-1])
    else:
        holes_to_plot.append(c_tables_plot_list[i])
    j += 1
s1_tables_plot_list = [s1_tables_plot[i:i+4] for i in range(0, len(s1_tables_plot), 4)]
s2_tables_plot_list = [s2_tables_plot[i:i+4] for i in range(0, len(s2_tables_plot), 4)]
c_tables_plot_site_lists = [s1_tables_plot_list, s2_tables_plot_list]
for c_tables_plot in c_tables_plot_site_lists:
    for sublist in c_tables_plot:
        holes_to_plot.append(sublist)
# --------------------------------------------------------------------
# Simulation -------------------------------------------------------------
c1_tables_list = [c1_tables[i:i+4] for i in range(0, len(c1_tables), 4)]
c2_tables_list = [c2_tables[i:i+4] for i in range(0, len(c2_tables), 4)]
c3_tables_list = [c3_tables[i:i+4] for i in range(0, len(c3_tables), 4)]
c4_tables_list = [c4_tables[i:i+4] for i in range(0, len(c4_tables), 4)]
c5_tables_list = [c5_tables[i:i+4] for i in range(0, len(c5_tables), 4)]

c_tables_plot_lists = [c1_tables_list, c2_tables_list, c3_tables_list, c4_tables_list, c5_tables_list]

for c_tables_plot in c_tables_plot_lists:
    for sublist in c_tables_plot:
        sublist.append(sublist[0])

for c_tables_plot in c_tables_plot_lists:
    for sublist in c_tables_plot:
        holes.append(sublist)
# -----------------------------------------------------------------------
walkable = Polygon(area, holes)
walkable_to_plot = Polygon(area, holes_to_plot)

exit_1 = Polygon(exit_1)
exit_2 = Polygon(exit_2)


plot_polygon(walkable_to_plot)
plot_polygon(exit_1, color="red")
plot_polygon(exit_2, color="red")
plot_points(Polygon(c1_spawn_points))
plot_points(Polygon(c2_spawn_points))
plot_points(Polygon(c3_spawn_points))
plot_points(Polygon(c4_spawn_points))
plot_points(Polygon(c5_spawn_points))
plot_points(Polygon(s1_spawn_points))
plot_points(Polygon(s2_spawn_points))

trajectory_file = "./Trajectories/Final18.sqlite"
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
AGENT_RADIUS = 0.1
AGENT_COUNT = 25

# Define function to create journeys with specified waypoints and exits
def create_journey(simulation_sfm, switch_point, waypoints, exit_1, exit_2):
    switch_id = simulation_sfm.add_waypoint_stage(switch_point, SWITCH_DISTANCE)
    waypoint_id1 = simulation_sfm.add_waypoint_stage(waypoints[0], WAYPOINT_DISTANCE)
    waypoint_id2 = simulation_sfm.add_waypoint_stage(waypoints[1], WAYPOINT_DISTANCE)

    exit1_id = simulation_sfm.add_exit_stage(exit_1.exterior.coords[:-1])
    journey1 = jps.JourneyDescription([switch_id, waypoint_id1, exit1_id])
    journey1.set_transition_for_stage(switch_id, jps.Transition.create_fixed_transition(waypoint_id1))
    journey1.set_transition_for_stage(waypoint_id1, jps.Transition.create_fixed_transition(exit1_id))
    journey1_id = simulation_sfm.add_journey(journey1)

    exit2_id = simulation_sfm.add_exit_stage(exit_2.exterior.coords[:-1])
    journey2 = jps.JourneyDescription([switch_id, waypoint_id2, exit2_id])
    journey2.set_transition_for_stage(switch_id, jps.Transition.create_fixed_transition(waypoint_id2))
    journey2.set_transition_for_stage(waypoint_id2, jps.Transition.create_fixed_transition(exit2_id))
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
                # orientation=(-1,0)
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
                # orientation=(1,1)
            )
        )

# Class 1:
switch_point1 = (246, 34.9)
waypoints1 = [(242.45, 35.9),(242.45, 35.9)]
switch_id1, journey1_id1, journey2_id1 = create_journey(simulation_sfm, switch_point1, waypoints1, exit_1, exit_2)
start_positions1 = random.sample(c1_spawn_points, 50)
add_agents(simulation_sfm, start_positions1, switch_id1, journey1_id1, journey2_id1, journey1_percentage=10)

# Class 2:
switch_point2 = (232.1, 35)
waypoints2 = [(232.1, 35.5),(232.1, 35.5)]
switch_id2, journey1_id2, journey2_id2 = create_journey(simulation_sfm, switch_point2, waypoints2, exit_1, exit_2)
start_positions2 = random.sample(c2_spawn_points, 50)
add_agents(simulation_sfm, start_positions2, switch_id2, journey1_id2, journey2_id2, journey1_percentage=30)

# Class 3:
switch_point3 = (222, 35.2)
waypoints3 = [(222, 35.7),(222, 35.7)]
switch_id3, journey1_id3, journey2_id3 = create_journey(simulation_sfm, switch_point3, waypoints3, exit_1, exit_2)
start_positions3 = random.sample(c3_spawn_points, 25)
add_agents(simulation_sfm, start_positions3, switch_id3, journey1_id3, journey2_id3, journey1_percentage=50)

# Class 4:
switch_point4 = (210, 34.4)
waypoints4 = [(210, 34.9),(210, 34.9)]
switch_id4, journey1_id4, journey2_id4 = create_journey(simulation_sfm, switch_point4, waypoints4, exit_1, exit_2)
start_positions4 = random.sample(c4_spawn_points, 20)
add_agents(simulation_sfm, start_positions4, switch_id4, journey1_id4, journey2_id4, journey1_percentage=70)

# Class 5:
switch_point5 = (194.7, 35)
waypoints5 = [(194.7, 35.5),(194.7, 35.5)]
switch_id5, journey1_id5, journey2_id5 = create_journey(simulation_sfm, switch_point5, waypoints5, exit_1, exit_2)
start_positions5 = random.sample(c5_spawn_points, 25)
add_agents(simulation_sfm, start_positions5, switch_id5, journey1_id5, journey2_id5, journey1_percentage=90)

# Site 1:
switch_point6 = (208.6, 42.6)
waypoints6 = [(208.6, 39.2),(208.6, 39.2)]
switch_id6, journey1_id6, journey2_id6 = create_journey(simulation_sfm, switch_point6, waypoints6, exit_1, exit_2)
start_positions6 = random.sample(s1_spawn_points, 20)
add_agents(simulation_sfm, start_positions6, switch_id6, journey1_id6, journey2_id6, journey1_percentage=70)

# Site 2:
switch_point7 = (210.7, 42.6)
waypoints7 = [(210.7, 39.2),(210.7, 39.2)]
switch_id7, journey1_id7, journey2_id7 = create_journey(simulation_sfm, switch_point7, waypoints7, exit_1, exit_2)
start_positions7 = random.sample(s2_spawn_points, 50)
add_agents(simulation_sfm, start_positions7, switch_id7, journey1_id7, journey2_id7, journey1_percentage=50)


while (simulation_sfm.agent_count() > 0 and simulation_sfm.iteration_count() < 5000):
    simulation_sfm.iterate()


from jupedsim.internal.notebook_utils import animate, read_sqlite_file

trajectory_data, walkable_area = read_sqlite_file(trajectory_file)
speed = pedpy.compute_individual_speed(traj_data=trajectory_data, frame_step=5)
speed = speed.merge(trajectory_data.data, on=["id", "frame"], how="left")

animate(trajectory_data, walkable_area)
pedpy.plot_trajectories(
    traj=trajectory_data, walkable_area=pedpy.WalkableArea(walkable_to_plot)
)

import sqlite3
from matplotlib.animation import FuncAnimation

db_path = './Trajectories/Final18.sqlite'
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
anim = FuncAnimation(fig, animate, init_func=init, frames=num_frames, interval=10, blit=True)

plot_polygon(walkable_to_plot, color="grey", linewidth=0.5, add_points=False)
plot_polygon(exit_1, color="red")
plot_polygon(exit_2, color="red")

plt.show()

