import math
import json

# --- CORE AXIOMS & CONSTANTS ---
FLOOR_LIMIT = 0.5  # Rule A: Structural Lower Bound

# Real-world astronomical parameters
SUN_MASS = 1.989e30       
MERCURY_MASS = 3.301e23   
G_CONSTANT = 6.6743e-11  

class CelestialObject:
    def __init__(self, name, mass, x, y, vx, vy, heat=0.0, spin=0.0):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.heat = heat  # Rule C Variable
        self.spin = spin  # Rule C Variable

class FluidMonopoleUniverse:
    def __init__(self, time_step_days=1.0):
        # 1 day time-steps (86400 seconds) gives a clean, smooth orbital trajectory
        self.dt = time_step_days * 86400.0 
        self.objects = []
        
    def add_object(self, obj):
        self.objects.append(obj)

    def _get_acceleration(self, sun, planet):
        """Calculates acceleration vectors using the fluid/monopole axioms."""
        # 1. Spatial Substrate Distance
        dx = sun.x - planet.x
        dy = sun.y - planet.y
        r = math.sqrt(dx**2 + dy**2)

        # Rule A: Structural lower bound floor to prevent divide-by-zero
        if r < FLOOR_LIMIT: 
            r = FLOOR_LIMIT  

        # Rule B: Inverse-Square Baseline (1/r^2) + Compounding Field Stacking (1/r^3)
        baseline_flux = sun.mass / (r**2)  
        field_stacking = sun.mass / (r**3) 
        
        # Rule C: Localized Interference Patterns (Speed and Heat)
        planet_speed = math.sqrt(planet.vx**2 + planet.vy**2)
        # Toned down scaling factors to keep the orbit tightly stabilized over long cycles
        interference = 1.0 + (planet.heat * 1e-6) + (planet_speed * 1e-25) 
        
        # Combine into total effective flux density
        # The 1e9 multiplier balances the physical geometric drop-off of the field lines
        total_flux_density = (baseline_flux + (field_stacking * 1e9)) * interference

        # Rule B: Vector Inversion (Strict Inward Attractiveness)
        accel_magnitude = total_flux_density * G_CONSTANT
        ax = accel_magnitude * (dx / r)
        ay = accel_magnitude * (dy / r)
        
        return ax, ay

    def calculate_forward_cycle(self):
        """Executes a stable forward Velocity Verlet loop."""
        sun = self.objects[0]
        mercury = self.objects[1]

        # Step 1: Calculate current acceleration
        ax1, ay1 = self._get_acceleration(sun, mercury)

        # Step 2: Update position using current velocity and half-step acceleration
        mercury.x += mercury.vx * self.dt + 0.5 * ax1 * (self.dt**2)
        mercury.y += mercury.vy * self.dt + 0.5 * ay1 * (self.dt**2)

        # Step 3: Calculate new acceleration at the new position
        ax2, ay2 = self._get_acceleration(sun, mercury)

        # Step 4: Update velocity using the average of the two accelerations
        mercury.vx += 0.5 * (ax1 + ax2) * self.dt
        mercury.vy += 0.5 * (ay1 + ay2) * self.dt


# --- TEST EXECUTION ---
if __name__ == "__main__":
    # Initialize the engine
    universe = FluidMonopoleUniverse(time_step_days=1.0)

    # Initialize Mercury at Perihelion with its real-world velocity (~59,000 m/s)
    sun = CelestialObject("Sun", SUN_MASS, 0.0, 0.0, 0.0, 0.0, heat=5778.0, spin=1.0)
    mercury = CelestialObject("Mercury", MERCURY_MASS, 4.6e10, 0.0, 0.0, 59000.0, heat=700.0, spin=0.01)

    universe.add_object(sun)
    universe.add_object(mercury)

    print("--- RUNNING STABLE ORBITAL PREDICTION (50000000 DAYS) ---")
    
    # We loop for 50000000 days (Mercury's full year is roughly 88 days, so it will complete a full loop!)
    for day in range(50000000):
        universe.calculate_forward_cycle()
        
        # Printing out the coordinates so you can see it orbit through the quadrants
        if day % 5 == 0 or day < 10:  # Print early steps, then every 5 days to keep terminal clean
            print(f"Day {day:02d} -> Pos X: {mercury.x:16,.2f} | Pos Y: {mercury.y:16,.2f} | Speed: {math.sqrt(mercury.vx**2 + mercury.vy**2):,.1f} m/s")