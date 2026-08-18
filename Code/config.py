import os
import random
output_dir = "./Output"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(f"{output_dir}/plots", exist_ok=True)
os.makedirs(f"{output_dir}/animation", exist_ok=True)

random.seed(42)


SWITCH_DISTANCE = 0.5
WAYPOINT_DISTANCE = 0.5
AGENT_RADIUS = 0.05
AGENT_COUNT = 25

# Define class colors
class_colors = {
    1: 'red',
    2: 'blue', 
    3: 'green',
    4: 'orange',
    5: 'purple',
    6: 'cyan',
    7: 'magenta'
}
