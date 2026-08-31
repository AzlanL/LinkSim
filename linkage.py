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





if __name__ == "__main__":
    print(f"Ground: {GROUND}, Crank: {CRANK}, Coupler: {COUPLER}, Rocker: {ROCKER}")

    theta2_rad = np.radians(45) #convert 45 degrees to radians
    theta3, theta4 = solve_position(theta2_rad) #using solve position function to find 03 and 04 given 02 = 45 degrees
    print(f"\nAt crank angle 45°:")
    print(f"Coupler angle: {np.degrees(theta3):.2f}°")
    print(f"Rocker angle: {np.degrees(theta4):.2f}°") #converts output from radians to degrees and prints it out
    print(f"Joint positions: {get_joint_positions(theta2_rad, theta3, theta4)}") #output x,y positions of all joints

    full_results = solve_full_rotation(num_steps=10) #find all angles of 02, 03, and 04 for a full rotation of the crank, using 10 steps
    print(f"\nFirst result: {full_results[0]}")
    print(f"Last result: {full_results[-1]}")
    print(f"Total steps solved: {len(full_results)}")