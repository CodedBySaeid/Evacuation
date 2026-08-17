# Pedestrian Evacuation Simulation

A pedestrian evacuation simulation of faculty classrooms and nearby sites using [JuPedSim](https://www.jupedsim.org/), the Social Force Model, [PedPy](https://pedpy.readthedocs.io/), Shapely, Pandas, NumPy, and Matplotlib.

The model represents pedestrians evacuating a faculty floor/building through two exits. Pedestrians are generated at predefined spawn locations for five classes and two additional sites, assigned to evacuation journeys, and simulated until everyone has left or the maximum number of iterations is reached.

## Overview

The simulation workflow is:

1. Load the building geometry, obstacles, exits, and pedestrian spawn points from `readcsv.py`.
2. Construct the walkable area as a Shapely polygon with holes for walls, columns, and furniture.
3. Create a JuPedSim simulation using the Social Force Model.
4. Define two possible evacuation journeys for each group:
   - a route through `exit_1`
   - a route through `exit_2`
5. Randomly select initial pedestrian positions from the configured spawn points.
6. Assign pedestrians to the two journeys according to a configurable percentage.
7. Run the simulation for up to 3000 iterations.
8. Save pedestrian trajectories to a SQLite database.
9. Visualize the trajectories and calculate pedestrian-flow characteristics with PedPy.

## Project structure

The code expects the following files/directories:

```text
project/
├── simulation.py              # Main simulation/analysis script
├── readcsv.py                 # Geometry, exits, tables, and spawn-point data
├── mappp-Model.png            # Background image used by the custom animation
└── Trajectories/
    └── Final19.sqlite         # Generated trajectory database
```

The exact name of the main Python script is up to you; the current code can be saved as, for example, `simulation.py`.

> **Important:** `readcsv.py` is required by the simulation because the geometry and spawn-point variables are imported from it. The code provided here does not contain those definitions.

## Requirements

The code uses Python and the following packages:

- `jupedsim`
- `pedpy`
- `shapely`
- `pandas`
- `numpy`
- `matplotlib`

It also uses Python's standard-library modules:

- `pathlib`
- `random`
- `sqlite3`

A convenient way to install the Python dependencies is:

```bash
pip install jupedsim pedpy shapely pandas numpy matplotlib
```

For reproducible development, using a virtual environment is recommended:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Then install the dependencies:

```bash
pip install jupedsim pedpy shapely pandas numpy matplotlib
```

## Input data

### `readcsv.py`

The simulation imports:

- `area` — outer boundary of the walkable area
- `columns` — column geometry
- `wall_1`, `wall_2` — wall/obstacle geometry
- `c1_tables` ... `c5_tables` — classroom table geometry
- `exit_1`, `exit_2` — evacuation exits
- `c1_spawn_points` ... `c5_spawn_points` — classroom pedestrian spawn points
- `s1_spawn_points`, `s2_spawn_points` — site spawn points
- plotting versions of several geometries

These values are used to construct the simulation geometry and to place pedestrians.

### Background map

The custom Matplotlib animation loads:

```text
mappp-Model.png
```

If this file is missing, the simulation itself can still produce the trajectory database, but the custom background-image animation will not work.

## Running the simulation

From the project directory, run:

```bash
python simulation.py
```

The script first builds the walkable area and visualizes the geometry, then creates the JuPedSim simulation and adds pedestrians.

The simulation is configured with:

```python
SWITCH_DISTANCE = 0.5
WAYPOINT_DISTANCE = 0.5
AGENT_RADIUS = 0.05
AGENT_COUNT = 25
```

`AGENT_RADIUS` is used when creating pedestrians. `AGENT_COUNT` is currently defined but is not used elsewhere in the provided code.

The trajectory database is written to:

```text
Trajectories/Final19.sqlite
```

Make sure the `Trajectories` directory exists before running the script.

## Pedestrian groups

The current configuration contains seven groups.

| Group | Spawn points sampled | Journey 1 percentage |
|---|---:|---:|
| Class 1 | 37 | 10% |
| Class 2 | 41 | 30% |
| Class 3 | 2 | 50% |
| Class 4 | 0 | 70% |
| Class 5 | 0 | 90% |
| Site 1 | 10 | 70% |
| Site 2 | 15 | 50% |

This corresponds to 105 pedestrians in the current configuration.

For each group, pedestrians are split between the two journeys using `journey1_percentage`.

For example:

```python
add_agents(
    simulation_sfm,
    start_positions1,
    switch_id1,
    journey1_id1,
    journey2_id1,
    journey1_percentage=10
)
```

means that approximately 10% of the selected Class 1 pedestrians are assigned to Journey 1 and the remainder to Journey 2.

## Evacuation journeys

Each group has:

1. a switch point,
2. two possible waypoints,
3. two exit stages.

The helper function:

```python
create_journey(...)
```

creates the two possible routes.

Conceptually, the routes are:

```text
Switch point
     |
     +----> Waypoint 1 ----> Exit 1
     |
     +----> Waypoint 2 ----> Exit 2
```

The transition between stages is fixed:

```python
jps.Transition.create_fixed_transition(...)
```

Therefore, pedestrians follow the journey assigned to them rather than dynamically selecting an exit during the simulation.

## Changing the evacuation scenario

The main scenario parameters are defined directly in the script.

### Number of pedestrians

The number of pedestrians sampled from each spawn-point set is controlled here:

```python
start_positions1 = random.sample(c1_spawn_points, 37)
start_positions2 = random.sample(c2_spawn_points, 41)
start_positions3 = random.sample(c3_spawn_points, 2)
start_positions4 = random.sample(c4_spawn_points, 0)
start_positions5 = random.sample(c5_spawn_points, 0)

start_positions6 = random.sample(s1_spawn_points, 10)
start_positions7 = random.sample(s2_spawn_points, 15)
```

To simulate a different population, change these values.

The requested sample size must not exceed the number of available spawn points.

### Exit distribution

Change `journey1_percentage` when calling `add_agents()`.

Examples:

```python
journey1_percentage=50
```

assigns half of the selected pedestrians to each journey.

```python
journey1_percentage=100
```

assigns all pedestrians to Journey 1.

```python
journey1_percentage=0
```

assigns all pedestrians to Journey 2.

### Randomness

The script sets:

```python
random.seed(1)
```

This makes the Python `random.sample()` selection reproducible between runs, provided the input data and execution environment remain unchanged.

If you want a different initial population distribution, change the seed:

```python
random.seed(42)
```

## Simulation termination

The simulation runs while both conditions are true:

```python
simulation_sfm.agent_count() > 0
```

and

```python
simulation_sfm.iteration_count() < 3000
```

In other words, the simulation stops when either:

- all pedestrians have evacuated, or
- 3000 simulation iterations have been reached.

To change the maximum number of iterations, modify:

```python
while (
    simulation_sfm.agent_count() > 0
    and simulation_sfm.iteration_count() < 3000
):
    simulation_sfm.iterate()
```

## Output

The main simulation output is a JuPedSim SQLite trajectory database:

```text
Trajectories/Final19.sqlite
```

The code later reads the trajectory data from this database for visualization and analysis.

The trajectory data contains pedestrian positions by frame and is used to calculate quantities such as speed, density, flow, neighborhood information, and time/distance relationships.

## Visualization

The script provides several visualization methods.

### JuPedSim animation

```python
animate(trajectory_data, walkable_area)
```

This displays the simulated pedestrian trajectories using JuPedSim's notebook utilities.

### PedPy trajectory plot

```python
pedpy.plot_trajectories(
    traj=trajectory_data,
    walkable_area=pedpy.WalkableArea(walkable_to_plot)
)
```

This plots pedestrian trajectories over the walkable area.

### Custom Matplotlib animation

The script also loads the SQLite database directly and overlays pedestrian positions on:

```text
mappp-Model.png
```

The animation updates the pedestrian positions frame by frame.

## Trajectory analysis

After the simulation, the script uses PedPy to analyze the resulting trajectories.

### Measurement area and measurement line

A measurement area and measurement line are defined near the bottleneck/exit region:

```python
measurement_area = MeasurementArea([
    (245.65, 34.79),
    (246.32, 34.79),
    (246.32, 34.37),
    (245.65, 34.37)
])

measurement_line = MeasurementLine([
    (245.69, 35.08),
    (246.38, 35.08)
])
```

These are subsequently used for density, speed, and flow calculations.

If the building geometry or coordinate system changes, these coordinates should be updated accordingly.

### Density

The script calculates classical density:

```python
classic_density = compute_classic_density(
    traj_data=traj,
    measurement_area=measurement_area
)
```

It also calculates Voronoi-based density using individual Voronoi polygons.

### Individual pedestrian speed

PedPy is used to calculate individual pedestrian speeds with different boundary-handling methods, including:

- `BORDER_EXCLUDE`
- `BORDER_SINGLE_SIDED`

The current analysis uses a frame step of 25 for some individual-speed calculations.

### Mean and Voronoi speed

The script calculates:

- mean speed in the measurement area
- Voronoi speed in the measurement area

These are plotted as time-dependent quantities.

### Flow

The script calculates pedestrian counts crossing the measurement line using:

```python
compute_n_t(...)
```

and then calculates flow using:

```python
compute_flow(...)
```

The resulting plots describe pedestrian throughput at the bottleneck.

### Neighborhood analysis

The code calculates pedestrian neighbors from Voronoi data and visualizes the neighborhood of a selected pedestrian at a selected frame.

The current example uses:

```python
pedestrian_id = 8
frame = 350
```

### Time-distance analysis

The script uses:

```python
compute_time_distance_line(...)
```

to analyze pedestrian distance/time relationships relative to the measurement line.

### Spatial profiles

Finally, the code calculates spatial profiles of:

- pedestrian speed
- pedestrian density

The current profile analysis uses a grid size of:

```python
grid_size = 0.4
```

and examines frames:

```python
min_frame_profiles = 250
max_frame_profiles = 300
```

The speed profile uses the Voronoi method, and the density profile also uses the Voronoi method.

## Important configuration points

The following values are especially relevant when adapting the model to another evacuation scenario:

| Parameter | Purpose |
|---|---|
| `AGENT_RADIUS` | Pedestrian radius used by the Social Force Model |
| `SWITCH_DISTANCE` | Distance threshold associated with the switch-point stage |
| `WAYPOINT_DISTANCE` | Distance threshold associated with waypoint stages |
| `journey1_percentage` | Percentage of pedestrians assigned to Journey 1 |
| `random.seed(...)` | Controls reproducibility of spawn-point sampling |
| `3000` | Maximum number of simulation iterations |
| `measurement_area` | Region used for density/speed measurements |
| `measurement_line` | Line used for pedestrian crossing/flow measurements |
| `frame_step` | Temporal step used in individual-speed calculations |
| `grid_size` | Spatial resolution for profile calculations |

Due to the proximity of the objects (tables), Social Force obstacleScale is reduced to 250.


## Notes and limitations

- The model uses the JuPedSim **Social Force Model**.
- The current journey assignment is predetermined through fixed transitions; it does not implement dynamic route choice based on congestion.
- The geometry is hard-coded through variables imported from `readcsv.py`.
- Several coordinates for switch points, waypoints, measurement areas, and measurement lines are hard-coded in the script.
- The trajectory output filename is currently fixed to `Final19.sqlite`.
- `AGENT_COUNT` is defined but is not used by the current simulation.
- The analysis section assumes that the trajectory database was successfully generated before it is executed.
- The custom animation assumes that `mappp-Model.png` uses the same coordinate system as the simulation geometry.
- The current code contains both simulation and post-processing/analysis in one script. For larger experiments, separating these into modules can make scenario management easier.

## Reproducibility

For reproducible experiments install the packages in requirements.txt, also python version used is 3.10.5.


## License

No license is specified in the current project. If this repository is intended for public distribution, add an appropriate `LICENSE` file and update this section.

## Author

This project was done by CodedBySaeid!
