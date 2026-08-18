from loadfiles import (
                    area,columns,wall_1,wall_2,c1_tables,c2_tables,c3_tables,c4_tables,
                    c5_tables,exit_1,exit_2,c1_spawn_points,c2_spawn_points,c3_spawn_points,
                    c4_spawn_points,c5_spawn_points,s1_spawn_points,s2_spawn_points,wall_1_plot,
                    wall_2_plot,s1_tables_plot,s2_tables_plot,c_tables_plot
                    )
import jupedsim as jps
from jupedsim.internal.notebook_utils import animate, read_sqlite_file
import pandas as pd
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import matplotlib.pyplot as plt
import pathlib, random, pedpy , shapely
import numpy as np
from datetime import datetime
from matplotlib.animation import FuncAnimation, PillowWriter
import sqlite3
from matplotlib.animation import FuncAnimation
import matplotlib.image as mpimg
from matplotlib.patches import Patch
from pedpy import (
    load_trajectory_from_jupedsim_sqlite, MeasurementArea, MeasurementLine, WalkableArea, Cutoff,
    plot_measurement_setup, compute_classic_density, plot_density, compute_individual_voronoi_polygons, 
    plot_voronoi_cells, compute_voronoi_density, compute_individual_speed, SpeedCalculation,
    compute_mean_speed_per_frame, plot_speed, compute_voronoi_speed, compute_n_t, plot_nt, compute_flow,
    plot_flow, compute_neighbors, plot_neighborhood, compute_time_distance_line, plot_time_distance,
    get_grid_cells, compute_grid_cell_polygon_intersection_area, compute_speed_profile, SpeedMethod,
    plot_profiles, compute_density_profile, DensityMethod
    )
from pedpy.column_identifier import DENSITY_COL, ID_COL, FRAME_COL
from config import *


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

# Plot and save geometry
plt.figure(figsize=(12, 8))
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
plt.title("Simulation Geometry")
plt.savefig(f'{output_dir}/plots/geometry_plot.png', dpi=300, bbox_inches='tight')
plt.close()

trajectory_file = "./Trajectories/Final19.sqlite"
simulation_sfm = jps.Simulation(
    model=jps.SocialForceModel(),
    geometry=walkable,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)



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
num_stu_c1 = 37
switch_point1 = (246, 34)
waypoints1 = [(242.45, 35.9),(242.45, 35.9)]
switch_id1, journey1_id1, journey2_id1 = create_journey(simulation_sfm, switch_point1, waypoints1, exit_1, exit_2)
start_positions1 = random.sample(c1_spawn_points, num_stu_c1)
add_agents(simulation_sfm, start_positions1, switch_id1, journey1_id1, journey2_id1, journey1_percentage=20)

# Class 2:
num_stu_c2 = 35
switch_point2 = (232.1, 34)
waypoints2 = [(232.1, 35.5),(232.1, 35.5)]
switch_id2, journey1_id2, journey2_id2 = create_journey(simulation_sfm, switch_point2, waypoints2, exit_1, exit_2)
start_positions2 = random.sample(c2_spawn_points, num_stu_c2)
add_agents(simulation_sfm, start_positions2, switch_id2, journey1_id2, journey2_id2, journey1_percentage=40)

# Class 3:
num_stu_c3 = 15
switch_point3 = (222, 35.2)
waypoints3 = [(222, 35.7),(222, 35.7)]
switch_id3, journey1_id3, journey2_id3 = create_journey(simulation_sfm, switch_point3, waypoints3, exit_1, exit_2)
start_positions3 = random.sample(c3_spawn_points, num_stu_c3)
add_agents(simulation_sfm, start_positions3, switch_id3, journey1_id3, journey2_id3, journey1_percentage=50)

# Class 4:
num_stu_c4 = 35
switch_point4 = (210, 34.4)
waypoints4 = [(210, 34.9),(210, 34.9)]
switch_id4, journey1_id4, journey2_id4 = create_journey(simulation_sfm, switch_point4, waypoints4, exit_1, exit_2)
start_positions4 = random.sample(c4_spawn_points, num_stu_c4)
add_agents(simulation_sfm, start_positions4, switch_id4, journey1_id4, journey2_id4, journey1_percentage=60)

# Class 5:
num_stu_c5 = 35
switch_point5 = (194.7, 34)
waypoints5 = [(194.7, 35.5),(194.7, 35.5)]
switch_id5, journey1_id5, journey2_id5 = create_journey(simulation_sfm, switch_point5, waypoints5, exit_1, exit_2)
start_positions5 = random.sample(c5_spawn_points, num_stu_c5)
add_agents(simulation_sfm, start_positions5, switch_id5, journey1_id5, journey2_id5, journey1_percentage=80)

# Site 1:
num_stu_s1 = 25
switch_point6 = (208.6, 42.6)
waypoints6 = [(208.6, 39.2),(208.6, 39.2)]
switch_id6, journey1_id6, journey2_id6 = create_journey(simulation_sfm, switch_point6, waypoints6, exit_1, exit_2)
start_positions6 = random.sample(s1_spawn_points, num_stu_s1)
add_agents(simulation_sfm, start_positions6, switch_id6, journey1_id6, journey2_id6, journey1_percentage=70)

# Site 2:
num_stu_s2 = 25
switch_point7 = (210.7, 42.6)
waypoints7 = [(210.7, 39.2),(210.7, 39.2)]
switch_id7, journey1_id7, journey2_id7 = create_journey(simulation_sfm, switch_point7, waypoints7, exit_1, exit_2)
start_positions7 = random.sample(s2_spawn_points, num_stu_s2)
add_agents(simulation_sfm, start_positions7, switch_id7, journey1_id7, journey2_id7, journey1_percentage=50)


while (simulation_sfm.agent_count() > 0 and simulation_sfm.iteration_count() < 5000):
    simulation_sfm.iterate()

###############################################################

trajectory_data, walkable_area = read_sqlite_file(trajectory_file)
speed = pedpy.compute_individual_speed(traj_data=trajectory_data, frame_step=5)
speed = speed.merge(trajectory_data.data, on=["id", "frame"], how="left")

# Save the pedpy trajectory plot
plt.figure(figsize=(12, 8))
pedpy.plot_trajectories(
    traj=trajectory_data, walkable_area=pedpy.WalkableArea(walkable_to_plot)
)
plt.title("Pedestrian Trajectories")
plt.savefig(f'{output_dir}/plots/trajectories_plot.png', dpi=300, bbox_inches='tight')
plt.close()


db_path = './Trajectories/Final19.sqlite'
conn = sqlite3.connect(db_path)

query = "SELECT * FROM trajectory_data;"
df = pd.read_sql_query(query, conn)
conn.close()


spawn_points_dict = {
    1: c1_spawn_points,
    2: c2_spawn_points,
    3: c3_spawn_points,
    4: c4_spawn_points,
    5: c5_spawn_points,
    6: s1_spawn_points,
    7: s2_spawn_points
}

agent_class_map = {}
for agent_id in df['id'].unique():
    agent_data = df[df['id'] == agent_id]
    if len(agent_data) > 0:
        initial_pos = (agent_data.iloc[0]['pos_x'], agent_data.iloc[0]['pos_y'])
        for class_id, spawn_points in spawn_points_dict.items():
            matched = False
            for sp in spawn_points:
                if abs(initial_pos[0] - sp[0]) < 0.001 and abs(initial_pos[1] - sp[1]) < 0.001:
                    agent_class_map[agent_id] = class_id
                    matched = True
                    break
            if matched:
                break
        if agent_id not in agent_class_map:
            min_dist = float('inf')
            assigned_class = None
            for class_id, spawn_points in spawn_points_dict.items():
                for sp in spawn_points:
                    dist = ((initial_pos[0] - sp[0])**2 + (initial_pos[1] - sp[1])**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        assigned_class = class_id
            agent_class_map[agent_id] = assigned_class


# Create figure with background
fig, ax = plt.subplots(figsize=(12, 8))
background_img = mpimg.imread("map.png")
ax.imshow(background_img, extent=[182.91, 258.49, 22.25, 64.77], aspect='auto')

# Create scatter plot
scat = ax.scatter([], [], s=30)

def init():
    ax.set_xlim(190, 250)
    ax.set_ylim(25, 55)
    return scat,

def animate_frame(i):
    current_frame = df[df['frame'] == i]
    if len(current_frame) > 0:
        positions = current_frame[['pos_x', 'pos_y']].values
        colors = [class_colors[agent_class_map[agent_id]] for agent_id in current_frame['id'].values]
        scat.set_offsets(positions)
        scat.set_color(colors)
    return scat,

num_frames = df['frame'].max()
anim = FuncAnimation(fig, animate_frame, init_func=init, frames=num_frames, interval=10, blit=True)

legend_elements = [
    Patch(facecolor='red', label=f'Class 1 ({num_stu_c1} students)'),
    Patch(facecolor='blue', label=f'Class 2 ({num_stu_c2} students)'),
    Patch(facecolor='green', label=f'Class 3 ({num_stu_c3} students)'),
    Patch(facecolor='orange', label=f'Class 4 ({num_stu_c4} students)'),
    Patch(facecolor='purple', label=f'Class 5 ({num_stu_c5} students)'),
    Patch(facecolor='cyan', label=f'Site 1 ({num_stu_s1} students)'),
    Patch(facecolor='magenta', label=f'Site 2 ({num_stu_s2} students)')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=8)

plot_polygon(walkable_to_plot, color="grey", linewidth=0.5, add_points=False)
plot_polygon(exit_1, color="red", linewidth=2)
plot_polygon(exit_2, color="red", linewidth=2)

plt.title("Pedestrian Movement", fontsize=14)

plt.show()
anim.save(f'{output_dir}/animation/pedestrian_movement.gif', writer=PillowWriter(fps=30), dpi=100)
plt.close()

# ========== CONTINUE WITH PEDPY ANALYSIS ==========
# ANALYSE THE TRAJECTORIES
traj = load_trajectory_from_jupedsim_sqlite(
    trajectory_file=pathlib.Path('./Trajectories/Final19.sqlite')
)
measurement_area = MeasurementArea([(245.65, 34.79), (246.32, 34.79), (246.32, 34.37), (245.65, 34.37)])
measurement_line = MeasurementLine([(245.69, 35.08), (246.38, 35.08)])
walkable_pedpy = WalkableArea(area, holes_to_plot)

# Save measurement setup
plot_measurement_setup(
    walkable_area=walkable_pedpy,
    traj=traj,
    traj_alpha=0.5,
    traj_width=1,
    measurement_areas=[measurement_area],
    measurement_lines=[measurement_line],
    ma_line_width=2,
).set_aspect("equal")
plt.savefig(f'{output_dir}/plots/measurement_setup.png', dpi=300, bbox_inches='tight')
plt.close()

################################## DENSITY ###################################
classic_density = compute_classic_density(
    traj_data=traj, measurement_area=measurement_area
)
plot_density(density=classic_density, title="Classic density over time")
plt.savefig(f'{output_dir}/plots/classic_density.png', dpi=300, bbox_inches='tight')
plt.close()

individual_cutoff = compute_individual_voronoi_polygons(
    traj_data=traj, 
    walkable_area=walkable_area, 
    cut_off=Cutoff(radius=1.0, quad_segments=3)
)
plot_voronoi_cells(
    voronoi_data=individual_cutoff,
    traj_data=traj,
    frame=300,
    walkable_area=walkable_pedpy,
    color_by_column=DENSITY_COL,
    vmin=0,
    vmax=10,
).set_aspect("equal")
plt.savefig(f'{output_dir}/plots/voronoi_cells.png', dpi=300, bbox_inches='tight')
plt.close()

density_voronoi, intersecting = compute_voronoi_density(
    individual_voronoi_data=individual_cutoff, measurement_area=measurement_area
)
plot_density(density=density_voronoi, title="Voronoi density over time")
plt.savefig(f'{output_dir}/plots/voronoi_density.png', dpi=300, bbox_inches='tight')
plt.close()

################################## SPEED ###################################
frame_step = 25
individual_speed_exclude = compute_individual_speed(
    traj_data=traj,
    frame_step=frame_step,
    compute_velocity=True,
    speed_calculation=SpeedCalculation.BORDER_EXCLUDE,
)
ped_id = 25
plt.figure()
plt.title(f"Speed time-series of a pedestrian {ped_id} (border excluded)")
single_individual_speed = individual_speed_exclude[
    individual_speed_exclude.id == ped_id
]
plt.plot(
    single_individual_speed.frame,
    single_individual_speed.speed,
)
plt.xlabel("frame")
plt.ylabel("v / m/s")
plt.savefig(f'{output_dir}/plots/speed_pedestrian_{ped_id}_excluded.png', dpi=300, bbox_inches='tight')
plt.close()

individual_speed_single_sided = compute_individual_speed(
    traj_data=traj,
    frame_step=frame_step,
    compute_velocity=True,
    speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED,
)
plt.figure()
plt.title(f"Speed time-series of an pedestrian {ped_id} (single sided)")
single_individual_speed = individual_speed_single_sided[
    individual_speed_single_sided.id == ped_id
]
plt.plot(
    single_individual_speed.frame,
    single_individual_speed.speed,
)
plt.xlabel("frame")
plt.ylabel("v / m/s")
plt.savefig(f'{output_dir}/plots/speed_pedestrian_{ped_id}_singlesided.png', dpi=300, bbox_inches='tight')
plt.close()

mean_speed = compute_mean_speed_per_frame(
    traj_data=traj,
    measurement_area=measurement_area,
    individual_speed=individual_speed_single_sided,
)
plot_speed(
    speed=mean_speed,
    title="Mean speed in front of the bottleneck",
)
plt.savefig(f'{output_dir}/plots/mean_speed.png', dpi=300, bbox_inches='tight')
plt.close()

voronoi_speed = compute_voronoi_speed(
    traj_data=traj,
    individual_voronoi_intersection=intersecting,
    individual_speed=individual_speed_single_sided,
    measurement_area=measurement_area,
)
plot_speed(
    speed=voronoi_speed,
    title="Voronoi speed in front of the bottleneck",
)
plt.savefig(f'{output_dir}/plots/voronoi_speed.png', dpi=300, bbox_inches='tight')
plt.close()

################################## FLOW ###################################
nt, crossing = compute_n_t(
    traj_data=traj,
    measurement_line=measurement_line,
)
plot_nt(nt=nt, title="N-t at bottleneck")
plt.savefig(f'{output_dir}/plots/nt_plot.png', dpi=300, bbox_inches='tight')
plt.close()

delta_frame = 100
flow = compute_flow(
    nt=nt,
    crossing_frames=crossing,
    individual_speed=individual_speed_single_sided,
    delta_frame=delta_frame,
    frame_rate=traj.frame_rate,
)
plot_flow(
    flow=flow,
    title="Crossing velocities at the corresponding flow at bottleneck",
)
plt.savefig(f'{output_dir}/plots/flow_plot.png', dpi=300, bbox_inches='tight')
plt.close()

################################## NEIGHBORHOOD ###################################
neighbors = compute_neighbors(individual_cutoff)
plot_neighborhood(
    pedestrian_id=8,
    voronoi_data=individual_cutoff,
    frame=350,
    neighbors=neighbors,
    walkable_area=walkable_area,
).set_aspect("equal")
plt.savefig(f'{output_dir}/plots/neighborhood_plot.png', dpi=300, bbox_inches='tight')
plt.close()

######################### DISTANCE TO ENTERANCE/TIME TO ENTERANCE ####################
df_time_distance = compute_time_distance_line(
    traj_data=traj, measurement_line=measurement_line
)
plot_time_distance(
    time_distance=df_time_distance,
    title="Distance to entrance/Time to entrance",
    frame_rate=traj.frame_rate,
)
plt.savefig(f'{output_dir}/plots/time_distance.png', dpi=300, bbox_inches='tight')
plt.close()

#################################### PROFILES ########################################
individual_cutoff = compute_individual_voronoi_polygons(
    traj_data=traj,
    walkable_area=walkable_area,
    cut_off=Cutoff(radius=0.8, quad_segments=3),
)

individual_speed = compute_individual_speed(
    traj_data=traj,
    frame_step=5,
    speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED,
)

profile_data = individual_speed.merge(individual_cutoff, on=[ID_COL, FRAME_COL])
profile_data = profile_data.merge(traj.data, on=[ID_COL, FRAME_COL])

grid_size = 0.4
grid_cells, _, _ = get_grid_cells(
    walkable_area=walkable_area, grid_size=grid_size
)

min_frame_profiles = 250
max_frame_profiles = 300

profile_data = profile_data[
    profile_data.frame.between(min_frame_profiles, max_frame_profiles)
]

(
    grid_cell_intersection_area,
    resorted_profile_data,
) = compute_grid_cell_polygon_intersection_area(
    data=profile_data, grid_cells=grid_cells
)

voronoi_speed_profile = compute_speed_profile(
    data=resorted_profile_data,
    walkable_area=walkable_area,
    grid_intersections_area=grid_cell_intersection_area,
    grid_size=grid_size,
    speed_method=SpeedMethod.VORONOI,
)
fig, (ax0) = plt.subplots(nrows=1, layout="constrained")
fig.set_size_inches(10, 5)
fig.suptitle("Speed profile")
cm = plot_profiles(
    walkable_area=walkable_area,
    profiles=voronoi_speed_profile,
    axes=ax0,
    label="v / m/s",
    vmin=0,
    vmax=1.5,
    title="Voronoi",
)
plt.savefig(f'{output_dir}/plots/speed_profile.png', dpi=300, bbox_inches='tight')
plt.close()

voronoi_density_profile = compute_density_profile(
    data=resorted_profile_data,
    walkable_area=walkable_area,
    grid_intersections_area=grid_cell_intersection_area,
    grid_size=grid_size,
    density_method=DensityMethod.VORONOI,
)
fig, (ax0) = plt.subplots(nrows=1, layout="constrained")
fig.set_size_inches(12, 5)
fig.suptitle("Density profile")
cm = plot_profiles(
    walkable_area=walkable_area,
    profiles=voronoi_density_profile,
    axes=ax0,
    label="$\\rho$ / 1/$m^2$",
    vmin=0,
    vmax=8,
    title="Voronoi",
)
plt.savefig(f'{output_dir}/plots/density_profile.png', dpi=300, bbox_inches='tight')
plt.close()

