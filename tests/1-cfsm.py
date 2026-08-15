import shapely
import shapely.plotting
import matplotlib.pyplot as plt
import jupedsim as jps 
import pathlib

geometry = shapely.Polygon(
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
        ][::-1],
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
        ][::-1],
    ],
)

exit = shapely.Polygon(
    [(-0.2, -1.9), (0.2, -1.9), (0.2, -1.7), (-0.2, -1.7)]
)


peds = jps.distribute_by_number(polygon=geometry, number_of_agents=20, distance_to_agents=0.2, distance_to_polygon=0.2, seed=2)
peds_poly = shapely.Polygon(peds)
shapely.plotting.plot_polygon(geometry)
shapely.plotting.plot_polygon(exit, color="red")
shapely.plotting.plot_points(peds_poly, color="yellow")
# print(peds_poly)

# introduce start positions to the simulation and set up output file
start_positions = peds
trajectory_file = "tests/bottleneck_cfsm.sqlite"
simulation_cfsm = jps.Simulation(
    model=jps.CollisionFreeSpeedModel(),
    geometry=geometry,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path(trajectory_file)
    ),
)

# introduce exit and journey to the simulation
exit_id = simulation_cfsm.add_exit_stage(exit)
journey = jps.JourneyDescription([exit_id])
journey_id = simulation_cfsm.add_journey(journey)

# add agents to the simulation
for position in start_positions:
    simulation_cfsm.add_agent(
        jps.CollisionFreeSpeedModelAgentParameters(
            journey_id=journey_id,
            stage_id=exit_id,
            position=position,
            radius=0.12,
        )
    )

# run simulation
while (
    simulation_cfsm.agent_count() > 0
    and simulation_cfsm.iteration_count() < 2000
):
    simulation_cfsm.iterate()


#simulation is done, let's view the result
import pedpy
from jupedsim.internal.notebook_utils import animate, read_sqlite_file

trajectory_data, walkable_area = read_sqlite_file(trajectory_file)
speed = pedpy.compute_individual_speed(traj_data=trajectory_data, frame_step=5)
speed = speed.merge(trajectory_data.data, on=["id", "frame"], how="left")

animate(trajectory_data, walkable_area)
pedpy.plot_trajectories(
    traj=trajectory_data, walkable_area=pedpy.WalkableArea(geometry)
)
plt.show()
