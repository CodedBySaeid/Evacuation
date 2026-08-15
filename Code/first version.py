import pandas as pd
import pathlib
import shapely
from shapely.geometry import Polygon
from jupedsim.internal.notebook_utils import animate, read_sqlite_file
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import sqlite3
import jupedsim as jps 
from shapely.geometry import Polygon
from shapely.plotting import plot_polygon, plot_points
import pedpy 

def load_coordinates(file_path):
    data = pd.read_csv(file_path)
    return list(zip(data["x"], data["y"]))

def load_geometries(base_path, files):
    return [load_coordinates(f"{base_path}/{file}") for file in files]

def plot_geometries(walkable, exits, peds):
    plot_polygon(walkable, color="grey", linewidth=0.5)
    for exit in exits:
        plot_polygon(exit, color="red")
    for ped, color in peds:
        plot_points(shapely.Polygon(ped), color=color)

def setup_simulation(walkable, exits):
    trajectory_file = "./Trajectories/DM.sqlite"
    simulation = jps.Simulation(
        model=jps.SocialForceModel(),
        geometry=walkable,
        trajectory_writer=jps.SqliteTrajectoryWriter(
            output_file=pathlib.Path(trajectory_file)
        ),
    )
    
    journey_ids = []
    for exit in exits:
        exit_id = simulation.add_exit_stage(exit.exterior.coords[:-1])
        journey = jps.JourneyDescription([exit_id])
        journey_id = simulation.add_journey(journey)
        journey_ids.append((exit_id, journey_id))

    return simulation, journey_ids, trajectory_file

def add_agents(simulation, positions, journey_id, stage_id):
    for position in positions:
        simulation.add_agent(
            jps.SocialForceModelAgentParameters(
                journey_id=journey_id,
                stage_id=stage_id,
                position=position,
                radius=0.12,
            )
        )

def run_simulation(simulation, max_iterations=5000):
    while simulation.agent_count() > 0 and simulation.iteration_count() < max_iterations:
        simulation.iterate()

def load_and_plot_trajectory(trajectory_file, walkable_area):
    trajectory_data, _ = read_sqlite_file(trajectory_file)
    speed = pedpy.compute_individual_speed(traj_data=trajectory_data, frame_step=5)
    speed = speed.merge(trajectory_data.data, on=["id", "frame"], how="left")
    animate(trajectory_data, walkable_area)
    pedpy.plot_trajectories(traj=trajectory_data, walkable_area=pedpy.WalkableArea(walkable_area))

def plot_animation(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM trajectory_data;", conn)
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
    plt.show()

# Main script
base_path = "./Geometries"
files = ["Walkable.csv", "Walls1.csv", "Walls2.csv", "Column1.csv", "Column2.csv", "Column3.csv", "Exit1.csv", "Exit2.csv"]
[area, *walls_columns, exit1, exit2] = load_geometries(base_path, files)

walkable = Polygon(area, holes=[wc[::-1] for wc in walls_columns])
exits = [Polygon(exit1), Polygon(exit2)]
peds1 = jps.distribute_by_number(polygon=walkable, number_of_agents=10, distance_to_agents=0.2, distance_to_polygon=0.2, seed=1)
peds2 = jps.distribute_by_number(polygon=walkable, number_of_agents=40, distance_to_agents=0.2, distance_to_polygon=0.2, seed=3)

plot_geometries(walkable, exits, [(peds1, "yellow"), (peds2, "green")])

simulation, journey_ids, trajectory_file = setup_simulation(walkable, exits)
start_positions = [(peds1, journey_ids[0]), (peds2, journey_ids[1])]

for positions, (exit_id, journey_id) in start_positions:
    add_agents(simulation, positions, journey_id, exit_id)

run_simulation(simulation)
load_and_plot_trajectory(trajectory_file, walkable)
plot_animation(trajectory_file)
