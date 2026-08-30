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


if __name__ == "__main__":
    print(f"Ground: {GROUND}, Crank: {CRANK}, Coupler: {COUPLER}, Rocker: {ROCKER}")