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

if __name__ == "__main__":
    print(f"Ground: {GROUND}, Crank: {CRANK}, Coupler: {COUPLER}, Rocker: {ROCKER}")

    theta2_rad = np.radians(45) #convert 45 degrees to radians
    theta3, theta4 = solve_position(theta2_rad) #using solve position function to find 03 and 04 given 02 = 45 degrees
    print(f"\nAt crank angle 45°:")
    print(f"Coupler angle: {np.degrees(theta3):.2f}°")
    print(f"Rocker angle: {np.degrees(theta4):.2f}°") #converts output from radians to degrees and prints it out
    print(f"Joint positions: {get_joint_positions(theta2_rad, theta3, theta4)}") #output x,y positions of all joints

    #now that we can find the values of 03 and 04 given 02, we need to work on drawing them