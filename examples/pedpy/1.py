from pedpy import load_trajectory, plot_trajectories, plot_measurement_setup, MeasurementLine, compute_n_t, plot_nt
import pathlib
import matplotlib.pyplot as plt

traj = load_trajectory(trajectory_file=pathlib.Path("demo-data/040_c_56_h-.txt"))

# print(traj)

fig1 = plt.figure()
# PLOT ONLY TRAJECTORIES
plot_trajectories(
    traj=traj,
    traj_alpha=0.5,
    traj_width=1,
).set_aspect("equal")
fig1.show()

# PLOT TRAJCTORIES WITH MEASUREMENT LINE
measurement_line = MeasurementLine([(0.25,0), (-0.25,0)])
ax = plot_measurement_setup(
    traj=traj,
    traj_alpha=0.5,
    traj_width=0.5,
    measurement_lines = [measurement_line],
    ml_width = 2).set_aspect("equal")

# PLOT NUMBER OF PASSING PEDS VS TIME
nt, _ = compute_n_t(
    traj_data=traj,
    measurement_line=measurement_line,
)
plot_nt(nt=nt)

plt.show()

