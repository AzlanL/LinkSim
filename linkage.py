"""
LinkSim: kinematic analysis of a planar four-bar linkage.

Solves the vector loop equation for a four-bar mechanism to find
the coupler and rocker angles as the crank rotates through a full
cycle, then analyzes motion and mechanical performance.
"""

# Link lengths (arbitrary units, e.g. cm)
GROUND = 4.0   # O2 to O4, fixed
CRANK = 1.0    # O2 to A, rotates fully — this is your input
COUPLER = 3.5  # A to B, the floating link
ROCKER = 3.0   # B to O4, swings back and forth

# Sanity check: Grashof's condition — shortest + longest <= sum of
# the other two. If this holds, the crank can rotate a full 360°.
lengths = [GROUND, CRANK, COUPLER, ROCKER]
if min(lengths) + max(lengths) > sum(lengths) - min(lengths) - max(lengths):
    print("Warning: this linkage may not satisfy Grashof's condition — "
          "the crank might not be able to fully rotate.")
else:
    print("Grashof condition satisfied — crank can fully rotate.")

#--------------------------------------------------------------------------

import numpy as np #library for working with arrays
from scipy.optimize import fsolve #finding the roots of a function


def loop_equations(unknowns, theta2): #function defined named loop equations, and takes two inputs, unknowns and theta2. Unknowns are the guesses we make for 03 and 04, and 02 is known
    """
    The two vector loop equations that must both equal zero.
    unknowns = [theta3, theta4] -- what we're solving for.
    theta2 -- the crank angle we've chosen (input, in radians).
    """
    theta3, theta4 = unknowns
    eq1 = CRANK * np.cos(theta2) + COUPLER * np.cos(theta3) - ROCKER * np.cos(theta4) - GROUND #vector equation of X lengths crank + coupler - rocker - ground = 0
    eq2 = CRANK * np.sin(theta2) + COUPLER * np.sin(theta3) - ROCKER * np.sin(theta4) #vector equation of Y lengths crank + coupler - rocker = 0
    return [eq1, eq2] #outputted when we use this function, the two equations must equal zero for the loop to close, otherwise will keep adjusting 03 and 04


def solve_position(theta2, initial_guess=(1.0, 2.0)): #numerical methods approach to find 03 and 04, given 02 and an initial guess for 03 and 04
    """
    Given a crank angle theta2 (radians), find the coupler angle (theta3)
    and rocker angle (theta4) that close the loop.
    """
    theta3, theta4 = fsolve(loop_equations, initial_guess, args=(theta2,)) #solve for 0
    return theta3, theta4 #function outputs the values of 03 and 04 that give 0, given 02

#------------------------------------------------------------------------------------------------------------------

def get_joint_positions(theta2, theta3, theta4): #get the x,y coordintes of the four joints in the linkage, given the angles of the three moving links
    O2 = (0, 0) #O2 is our initial crank so stays at the origin
    O4 = (GROUND, 0) #O4 depends on the length of our ground linkage but is completely horizontal from O2
    A = (CRANK * np.cos(theta2), CRANK * np.sin(theta2)) #Using basic trig to find x,y coordinates of A, which is the point where crank and coupler meet
    B = (O4[0] + ROCKER * np.cos(theta4), O4[1] + ROCKER * np.sin(theta4)) #Using basic trig to find x,y coordinates of B, which is the point where coupler and rocker meet
    return O2, A, B, O4 #Output the coordinates of the four joints in the linkage, which can be used to draw the linkage

def transmission_angle(theta3, theta4): #function to calculate the transmission angle, which is the angle between the coupler and rocker
    angle_diff = np.degrees(theta4 - theta3)
    return abs(angle_diff) % 180

def sweep_crank(num_steps=100): #function to sweep the crank through a full rotation, and find the corresponding angles of the coupler and rocker
    theta2_values = np.linspace(0, 2 * np.pi, num_steps) #create an array of crank angles from 0 to 2pi radians (linspace means evenly spaced values)
    return theta2_values

def solve_full_rotation(num_steps=100): #function to sweep the crank through a full rotation, and find the corresponding angles of the coupler and rocker
    theta2_values = sweep_crank(num_steps) #get the array of crank angles from 0 to 2pi radians
    results = [] #empty list called results to store 03 and 04angles

    guess = (1.0, 2.0) #initial guess for 03 and 04
    for theta2 in theta2_values: #for each value of 02, find the corresponding 03 and 04
        theta3, theta4 = solve_position(theta2, initial_guess=guess) #solves the position of 04 and 03 for whichever value of 02 we are currently on, using the previous values of 03 and 04 as the initial guess for the next iteratio
        results.append((theta2, theta3, theta4)) #saves the angle's results as a bundle of three values, 02, 03, and 04, and appends (adds to the end) it to the results list
        guess = (theta3, theta4) #makes the solver faster using the previous solution as the initial guess for the next iteration, since the angles will not change drastically from one step to the next
    return results #returns the list of all the angles of 02, 03, and 04 for the full rotation of the crank

#plotting functions below

import matplotlib.pyplot as plt #library for plotting

def plot_linkage(theta2): #function to plot the linkage at a given crank angle
    theta3, theta4 = solve_position(theta2) #find the corresponding angles of the coupler and rocker for the given crank angle
    O2, A, B, O4 = get_joint_positions(theta2, theta3, theta4) #find the x,y coordinates of the four joints in the linkage for the given angles

# Ground link (fixed, dashed)
    plt.plot([O2[0], O4[0]], [O2[1], O4[1]], '--', color='gray', linewidth=2) #plots the ground link as a dashed line between O2 and O4

    # Crank (blue)
    plt.plot([O2[0], A[0]], [O2[1], A[1]], 'o-', color='#378ADD', linewidth=3, markersize=8) #plots the crank as a solid line between O2 and A, with blue color, linewidth of 3, and markersize of 8

    # Coupler (green)
    plt.plot([A[0], B[0]], [A[1], B[1]], 'o-', color='#1D9E75', linewidth=3, markersize=8) #plots the coupler as a solid line between A and B, with green color, linewidth of 3, and markersize of 8

    # Rocker (orange)
    plt.plot([B[0], O4[0]], [B[1], O4[1]], 'o-', color='#D85A30', linewidth=3, markersize=8) #plots the rocker as a solid line between B and O4, with orange color, linewidth of 3, and markersize of 8


    plt.axis('equal') #x and y must use the same scale
    plt.grid(True) #adds a background grid to the plot
    plt.title(f"Linkage at crank angle {np.degrees(theta2):.0f}°") #labels the plot with the current crank angle in degrees
    plt.show() #opens window to display the plot

#---------------------------------------------------------------------------

from matplotlib.animation import FuncAnimation #library for creating animations

#function to animate both the linkage and the transmission angle curve together instead of just having a fixed image of the transmission angle curve
def animate_with_transmission(num_steps=100):
    results = solve_full_rotation(num_steps)
    crank_angles_deg = [np.degrees(r[0]) for r in results] #builds a list of crank angles in degrees from the results of the full rotation
    trans_angles = [transmission_angle(r[1], r[2]) for r in results] #builds a list of transmission angles from the results of the full rotation

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5)) #creates a window with two subplots, one for the linkage and one for the transmission angle curve

    # Left panel: the linkage
    ax1.set_aspect('equal')
    ax1.grid(True)
    ax1.set_xlim(-2, GROUND + ROCKER + 1)
    ax1.set_ylim(-2, COUPLER + 1)
    ground_line, = ax1.plot([], [], '--', color='gray', linewidth=2)
    crank_line, = ax1.plot([], [], 'o-', color='#378ADD', linewidth=3, markersize=8)
    coupler_line, = ax1.plot([], [], 'o-', color='#1D9E75', linewidth=3, markersize=8)
    rocker_line, = ax1.plot([], [], 'o-', color='#D85A30', linewidth=3, markersize=8)

    # Right panel: the transmission angle curve
    ax2.plot(crank_angles_deg, trans_angles, color='#1D9E75', linewidth=2)
    ax2.axhline(40, color='red', linestyle='--', linewidth=1)
    ax2.axhline(140, color='red', linestyle='--', linewidth=1)
    ax2.set_xlabel('Crank angle (°)')
    ax2.set_ylabel('Transmission angle (°)')
    ax2.set_title('Transmission Angle')
    ax2.grid(True)
    point, = ax2.plot([], [], 'o', color='#7A4FE0', markersize=10)

    def update(frame_num): #updats the plot for each frame of the animation
        theta2, theta3, theta4 = results[frame_num]
        O2, A, B, O4 = get_joint_positions(theta2, theta3, theta4) #gets the x,y coordinates of the four joints in the linkage for the given angles
        ground_line.set_data([O2[0], O4[0]], [O2[1], O4[1]])
        crank_line.set_data([O2[0], A[0]], [O2[1], A[1]])
        coupler_line.set_data([A[0], B[0]], [A[1], B[1]])
        rocker_line.set_data([B[0], O4[0]], [B[1], O4[1]])
        point.set_data([crank_angles_deg[frame_num]], [trans_angles[frame_num]]) #moves the dot to the xy position on the curve matching the frame number of the animation
        return ground_line, crank_line, coupler_line, rocker_line, point

    anim = FuncAnimation(fig, update, frames=num_steps, interval=50, blit=True) #creates the animation object, which will update the plot for each frame of the animation
    plt.tight_layout() #adjusts the spacing between the two subplots so that they don't overlap
    plt.show()
    return anim #returns the animation object so that it can be saved or manipulated later - prevents it from being cleared from memory while the window is open

#---------------------------------------------------------------------------


if __name__ == "__main__":
    print(f"Ground: {GROUND}, Crank: {CRANK}, Coupler: {COUPLER}, Rocker: {ROCKER}")
    anim = animate_with_transmission(100) #animates the linkage and transmission angle curve together, with 100 steps in the animation





    