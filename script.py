import math as m
import numpy as np
import scipy.optimize as o
from pprint import pprint 

### PARAM: Initial player or pearl position
s_x0 = 0
s_y0 = 4
s_z0 = 0
s_y0 = s_y0 + 1.62 - 0.1

### PARAM: Initial player velocity
v_py = 0.42
v_pz = 0.2

### Component-wise initial velocity function given a pitch and axis. Yaw is kept constant to 360 degrees. 
def v_0(axis:str, pitch:float) -> float:
    pitch = m.radians(pitch)
    return {
        "x": 0,
        "y": v_py + -1.5 * m.sin(pitch),
        "z": v_pz + 1.5 * m.cos(pitch)
    }[axis]

### Component-wise position function given a pitch and axis. We keep yaw constant at 360 degrees (hence, zeroing every sin(yaw))
def s(t:int, axis:str, pitch:float) -> float:
    return {
        "x": s_x0,
        "y": s_y0 + (v_0("y", pitch) + 3) * (100 - 100*0.99**t) - 3*t ,
        "z": s_z0 + v_0("z", pitch) * (100 - 100*0.99**t)
    }[axis]

### Passed into root_scalar to find where the position function for y, ie s_y, intersects the even ground y=s_y0. This helper transforms the root found by root_scalar to be the solution to s_y = s_y0 (where s_y0 is adjusted for the 1.62 and -0.1 offsets applied its initialization). 
def helper_s_y(t:int, pitch:float) -> float:
    return s(t, "y", pitch) - (s_y0 - (1.62-0.1))

### Compute when the pearl hits the ground, ASSUMING the landing spot is level with the player's standing spot 
# upper bound seems to be at least 90 ticks, as produced by angle -89 to -84 (angle -83 produced 89 ticks). Hence, 300 as an upper bound on root-finding is more than enough.  
def compute_landing_time(pitch:float) -> float:
    return m.floor(o.root_scalar(helper_s_y, args=(pitch), bracket=[0, 300], method="bisect").root)

### Convert a given pitch to its significant angle equivalent
# I observed that the raw pitch always gets rounded up to the lower significant angle: -45 is exactly a signif angle, and you can test -45.00001 and -44.99999 -- the former achieves 51.425 and latter achieves 51.430. Crazy!
def convert_pitch(pitch:float) -> float:
    return m.floor(pitch / (360/65536)) * 360/65536 

landing_times = {}
landing_distances = {}
desired_angles = np.arange(-90, 90, 360/65536)
for pitch in desired_angles:
    converted_pitch = convert_pitch(pitch)
    landing_times[converted_pitch] = compute_landing_time(converted_pitch)
    landing_distances[converted_pitch] = s(landing_times[converted_pitch], "z", converted_pitch)

top_entries = dict(sorted(landing_distances.items(), key=lambda item: item[1], reverse=True)[:10])
pprint(top_entries)