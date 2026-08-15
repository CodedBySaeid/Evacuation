import pandas as pd

def load_coordinates(file_path):
    data = pd.read_csv(file_path)
    return list(zip(data["x"], data["y"]))


###################### Simulation ######################
area = load_coordinates("./Geometries/Simulation/Area.csv")
columns = load_coordinates("./Geometries/Simulation/Columns.csv")
wall_1 = load_coordinates("./Geometries/Simulation/Wall_1.csv")
wall_2 = load_coordinates("./Geometries/Simulation/Wall_2.csv")
c1_tables = load_coordinates("./Geometries/Simulation/C1_tables.csv")
c2_tables = load_coordinates("./Geometries/Simulation/C2_tables.csv")
c3_tables = load_coordinates("./Geometries/Simulation/C3_tables.csv")
c4_tables = load_coordinates("./Geometries/Simulation/C4_tables.csv")
c5_tables = load_coordinates("./Geometries/Simulation/C5_tables.csv")
exit_1 = load_coordinates("./Geometries/Simulation/Exit1.csv")
exit_2 = load_coordinates("./Geometries/Simulation/Exit2.csv")
c1_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_c1.csv")
c2_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_c2.csv")
c3_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_c3.csv")
c4_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_c4.csv")
c5_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_c5.csv")
s1_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_s1.csv")
s2_spawn_points = load_coordinates("./Geometries/Simulation/Spawn_s2.csv")
####################### Plot #############################
wall_1_plot = load_coordinates("./Geometries/Plot/Walls1.csv")
wall_2_plot = load_coordinates("./Geometries/Plot/Walls2.csv")
s1_tables_plot = load_coordinates("./Geometries/Plot/SiteTables1.csv")
s2_tables_plot = load_coordinates("./Geometries/Plot/SiteTables2.csv")
c_tables_plot = load_coordinates("./Geometries/Plot/RoomDesks.csv")