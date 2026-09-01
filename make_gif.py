"""
One-off script to render linkage.py's animation to a GIF for the README.
"""

from linkage import solve_full_rotation, get_joint_positions, transmission_angle, GROUND, ROCKER, COUPLER #imports existing functions from linkage.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

num_steps = 100
results = solve_full_rotation(num_steps)
crank_angles_deg = [np.degrees(r[0]) for r in results]
trans_angles = [transmission_angle(r[1], r[2]) for r in results]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

ax1.set_aspect('equal')
ax1.grid(True)
ax1.set_xlim(-2, GROUND + ROCKER + 1)
ax1.set_ylim(-2, COUPLER + 1)
ground_line, = ax1.plot([], [], '--', color='gray', linewidth=2)
crank_line, = ax1.plot([], [], 'o-', color='#378ADD', linewidth=3, markersize=8)
coupler_line, = ax1.plot([], [], 'o-', color='#1D9E75', linewidth=3, markersize=8)
rocker_line, = ax1.plot([], [], 'o-', color='#D85A30', linewidth=3, markersize=8) #first screen which shows the four-bar linkage with the ground, crank, coupler, and rocker links

ax2.plot(crank_angles_deg, trans_angles, color='#1D9E75', linewidth=2)
ax2.axhline(40, color='red', linestyle='--', linewidth=1)
ax2.axhline(140, color='red', linestyle='--', linewidth=1)
ax2.set_xlabel('Crank angle (°)')
ax2.set_ylabel('Transmission angle (°)')
ax2.set_title('Transmission Angle')
ax2.grid(True)
point, = ax2.plot([], [], 'o', color='#7A4FE0', markersize=10) #second screen which shows the transmission angle plot with the crank angle on the x-axis and the transmission angle on the y-axis


def update(frame_num): #updates the animation for each frame
    theta2, theta3, theta4 = results[frame_num]
    O2, A, B, O4 = get_joint_positions(theta2, theta3, theta4)
    ground_line.set_data([O2[0], O4[0]], [O2[1], O4[1]])
    crank_line.set_data([O2[0], A[0]], [O2[1], A[1]])
    coupler_line.set_data([A[0], B[0]], [A[1], B[1]])
    rocker_line.set_data([B[0], O4[0]], [B[1], O4[1]])
    point.set_data([crank_angles_deg[frame_num]], [trans_angles[frame_num]])
    return ground_line, crank_line, coupler_line, rocker_line, point


anim = FuncAnimation(fig, update, frames=num_steps, interval=50, blit=True)
plt.tight_layout()

print("Saving GIF... this may take 10-30 seconds.")
anim.save('linkage_demo.gif', writer='pillow', fps=20) #gif file is saved as linkage_demo.gif with 20 frames per second
print("Saved as linkage_demo.gif")