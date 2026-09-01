"""
LinkSim Interactive: adjustable four-bar linkage with sliders for
link lengths and manual/auto crank angle control.
"""

import numpy as np #numpy lets us do math on arrays
from scipy.optimize import fsolve #fsolve lets us solve equations numerically to find solutions


def loop_equations(unknowns, theta2, lengths): #function takes crank angle and lengths variables and returns the loop equations for the four-bar linkage
    ground, crank, coupler, rocker = lengths
    theta3, theta4 = unknowns
    eq1 = crank * np.cos(theta2) + coupler * np.cos(theta3) - rocker * np.cos(theta4) - ground #x vectors
    eq2 = crank * np.sin(theta2) + coupler * np.sin(theta3) - rocker * np.sin(theta4) #y vectors
    return [eq1, eq2] #gives x and y vectors which should then be solved for 0


def solve_position(theta2, lengths, initial_guess=(1.0, 2.0)):
    theta3, theta4 = fsolve(loop_equations, initial_guess, args=(theta2, lengths)) #using fsolve and loop equations to solve to 0 for x and y equation
    return theta3, theta4 #found the angles for the coupler and rocker links


def get_joint_positions(theta2, theta3, theta4, lengths): #using trig to find positions of the joints based on the angles and lengths of the links
    ground, crank, coupler, rocker = lengths
    O2 = (0, 0)
    O4 = (ground, 0)
    A = (crank * np.cos(theta2), crank * np.sin(theta2))
    B = (O4[0] + rocker * np.cos(theta4), O4[1] + rocker * np.sin(theta4))
    return O2, A, B, O4


def transmission_angle(theta3, theta4): #calculates the transmission angle between the coupler and rocker links using geometry
    angle_diff = np.degrees(theta4 - theta3)
    return abs(angle_diff) % 180 #returns the absolute value of the angle difference modulo 180 to ensure it is within the range of 0 to 180 degrees

def check_grashof(lengths): #check if grashof condition is satisfied for the given lengths of the four-bar linkage
    ground, crank, coupler, rocker = lengths
    values = [ground, crank, coupler, rocker]
    shortest = min(values)
    longest = max(values)
    others_sum = sum(values) - shortest - longest
    return (shortest + longest) <= others_sum

def compute_wave(lengths, num_points=72): #computes the wave of the coupler point as the crank rotates through 360 degrees, returning the angles and y values of the coupler point
    ground, crank, coupler, rocker = lengths
    angles_deg = np.linspace(0, 360, num_points) #angles_deg is an array of angles from 0 to 360 degrees, divided into num_points intervals
    y_values = [] #will store the point's height at each angle, to be plotted as a wave
    guess = (1.0, 2.0)
    for deg in angles_deg:
        theta2 = np.radians(deg)
        A_x = crank * np.cos(theta2)
        A_y = crank * np.sin(theta2)
        dist_A_to_O4 = np.sqrt((A_x - ground) ** 2 + A_y ** 2) #distance from A (end of crank) to O4 (fixed rocker pivot) at this crank angle
        if dist_A_to_O4 > coupler + rocker or dist_A_to_O4 < abs(coupler - rocker):
            y_values.append(np.nan)  # geometrically impossible here, leave a gap in the wave
            continue
        theta3, theta4 = solve_position(theta2, lengths, initial_guess=guess) #solve for the coupler and rocker angles at this crank angle, using the previous solution as an initial guess for fsolve to improve convergence
        guess = (theta3, theta4) #use previous solution as initial guess for next iteration to improve convergence
        _, _, B, _ = get_joint_positions(theta2, theta3, theta4, lengths) #use function but only return the value for point B, which is the coupler point
        y_values.append(B[1]) #add the point to the list of y values for the wave plot
    return angles_deg, np.array(y_values) #returns list of angles and list of corresponsing y values for the coupler point, which can be plotted as a wave


#Above we have found all the angles and positions. The next step is to make the sliders

import matplotlib.pyplot as plt #allows us to plot the linkage and create sliders for user interaction
from matplotlib.widgets import Slider, Button #slider and button features

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6)) #two plots, one for the linkage and one for the transmission graph, side by side
plt.subplots_adjust(bottom=0.4)  # more room now, for five sliders total
ax.set_aspect('equal')
ax.grid(True)
ax.set_xlim(-4, 12)
ax.set_ylim(-4, 8)

ground_line, = ax.plot([], [], '--', color='gray', linewidth=2)
crank_line, = ax.plot([], [], 'o-', color='#378ADD', linewidth=3, markersize=8)
coupler_line, = ax.plot([], [], 'o-', color='#1D9E75', linewidth=3, markersize=8)
rocker_line, = ax.plot([], [], 'o-', color='#D85A30', linewidth=3, markersize=8)

# Sliders: positioned as [left, bottom, width, height], all as fractions of the figure
# Stacked vertically, one above the other
crank_angle_ax = plt.axes([0.25, 0.30, 0.5, 0.03])
ground_len_ax = plt.axes([0.25, 0.24, 0.5, 0.03])
crank_len_ax = plt.axes([0.25, 0.18, 0.5, 0.03])
coupler_len_ax = plt.axes([0.25, 0.12, 0.5, 0.03])
rocker_len_ax = plt.axes([0.25, 0.06, 0.5, 0.03]) #positions of sliders for the crank angle and lengths of the links, positioned vertically below the plot

crank_angle_slider = Slider(crank_angle_ax, 'Crank angle (°)', 0, 360, valinit=45)
ground_len_slider = Slider(ground_len_ax, 'Ground', 1, 8, valinit=4.0)
crank_len_slider = Slider(crank_len_ax, 'Crank', 0.5, 4, valinit=1.0)
coupler_len_slider = Slider(coupler_len_ax, 'Coupler', 1, 8, valinit=3.5)
rocker_len_slider = Slider(rocker_len_ax, 'Rocker', 1, 8, valinit=3.0) #sliders for the crank angle and lengths of the links, with initial values set
grashof_text = fig.text(0.25, 0.36, '', fontsize=10, weight='bold') #grashof condition warning


ax2.set_xlabel('Crank angle (°)')
ax2.set_ylabel('Point B height (y)')
ax2.set_title('Coupler-rocker joint height over rotation') #labelling the wave
ax2.grid(True)

initial_lengths = ( #reads slider values to get the initial lengths of the links for the wave plot
    ground_len_slider.val,
    crank_len_slider.val,
    coupler_len_slider.val,
    rocker_len_slider.val,
)
wave_angles, wave_y = compute_wave(initial_lengths) #gets the starting curve
wave_line, = ax2.plot(wave_angles, wave_y, color='#1D9E75', linewidth=2) #draws the wave of the coupler point as the crank rotates through 360 degrees
wave_point, = ax2.plot([], [], 'o', color='#7A4FE0', markersize=10) #live dot tracking


# Play/pause state and button
is_playing = False

play_ax = plt.axes([0.025, 0.5, 0.12, 0.05])
play_button = Button(play_ax, 'Play') #creating button and locating it on the left side of the figure

def toggle_play(event): #when button pressed, toggle the play/pause state and update the button label accordingly
    global is_playing
    is_playing = not is_playing
    play_button.label.set_text('Pause' if is_playing else 'Play')


play_button.on_clicked(toggle_play) #when button clicked, call the toggle_play function to change the play/pause state


def redraw(_): #function to redraw the linkage; ignores its argument, always re-reads all five sliders' current values instead
    lengths = (
        ground_len_slider.val,
        crank_len_slider.val,
        coupler_len_slider.val,
        rocker_len_slider.val,
    )  #build lengths fresh from whatever the sliders currently say
    theta2 = np.radians(crank_angle_slider.val)  #read crank angle from its slider too, instead of a passed-in argument
    ground, crank, coupler, rocker = lengths  #unpack lengths tuple into named variables, needed below for the feasibility check

    if check_grashof(lengths): #grashof check to see if it needs to display a warning or not, and change the color of the text accordingly
        grashof_text.set_text("✓ Grashof condition satisfied — crank can fully rotate")
        grashof_text.set_color('#1D9E75')
    else:
        grashof_text.set_text("⚠ Grashof condition NOT satisfied — crank may not fully rotate")
        grashof_text.set_color('red')

    
    # distance from A (end of crank) to O4 (fixed rocker pivot) at this crank angle
    A_x = crank * np.cos(theta2)
    A_y = crank * np.sin(theta2)
    dist_A_to_O4 = np.sqrt((A_x - ground)**2 + A_y**2)
    # geometrically impossible if coupler+rocker can't reach, or are too long and overlap
    if dist_A_to_O4 > coupler + rocker or dist_A_to_O4 < abs(coupler - rocker):
        fig.suptitle("⚠ Invalid geometry at this crank angle — adjust sliders", color='red')
        fig.canvas.draw_idle()
        return  # skip solving entirely, leave the linkage at its last valid position
    else:
        fig.suptitle("")  # clear any previous warning
    theta3, theta4 = solve_position(theta2, lengths)
    O2, A, B, O4 = get_joint_positions(theta2, theta3, theta4, lengths)

    ground_line.set_data([O2[0], O4[0]], [O2[1], O4[1]])
    crank_line.set_data([O2[0], A[0]], [O2[1], A[1]])
    coupler_line.set_data([A[0], B[0]], [A[1], B[1]])
    rocker_line.set_data([B[0], O4[0]], [B[1], O4[1]]) #update the linkage drawing based on the current crank angle and lengths, using the computed joint positions
    wave_angles, wave_y = compute_wave(lengths) #reculates waves using current slider lengths
    wave_line.set_data(wave_angles, wave_y) #updates existing curve data
    wave_point.set_data([crank_angle_slider.val], [B[1]]) #draws the live dot on the wave plot at the current crank angle and coupler point height
    ax2.relim() #rescale the axis in case the wave shape dramatically changes
    ax2.autoscale_view()
    fig.canvas.draw_idle() #redraws the figure to update but the idle part means it will wait until the GUI is idle to do the redraw, which can help with performance when many updates are happening quickly


crank_angle_slider.on_changed(redraw)
ground_len_slider.on_changed(redraw)
crank_len_slider.on_changed(redraw)
coupler_len_slider.on_changed(redraw)
rocker_len_slider.on_changed(redraw) #when changes are made to any of the sliders, redraw() is called to update the linkage drawing

redraw(None)  # draw the initial position; argument is ignored, sliders' initial starting values are used

def on_timer(): #called every 50 ms by the timer; if the play button is active, increment the crank angle slider by 3 degrees and wrap around at 360
    if is_playing:
        new_angle = (crank_angle_slider.val + 3) % 360 #makes a variable called new_angle that is the current value of the crank angle slider plus 3 degrees, wrapped around at 360 degrees
        crank_angle_slider.set_val(new_angle) #sets the crank angle slider to the new value, which will trigger redraw() to update the linkage drawing


timer = fig.canvas.new_timer(interval=50) #create a timer that will call on_timer every 50 milliseconds
timer.add_callback(on_timer) #every 50 ms call the function on_timer() to update the crank angle if the play button is active
timer.start() #start the timer so that it begins calling on_timer every 50 ms




plt.show()