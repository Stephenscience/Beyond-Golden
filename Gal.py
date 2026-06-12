import math

# --- CORE AXIOMS (Extracted from your framework) ---
G_CONSTANT = 6.6743e-11  
CORE_MASS = 2.0e41        # Mass of a typical galactic core (e.g., ~100 billion solar masses)
STAR_MASS = 2.0e30        # Average mass of an individual star (1 solar mass)
TIME_STEP_YEARS = 1000.0  # Galactic scales require larger dt steps
DT = TIME_STEP_YEARS * 365.25 * 86400.0  # Convert to seconds

class GalacticObject:
    def __init__(self, name, mass, x, y, vx, vy):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class GalacticEngine:
    def __init__(self, fluid_density_scalar=1e9, interference_factor=1.0):
        self.objects = []
        self.scalar = fluid_density_scalar  # Your 10^9 scalar bridge
        self.interference = interference_factor

    def add_body(self, body):
        self.objects.append(body)

    def _compute_all_accelerations(self):
        """Calculates the intersecting vector sum of 1/r^2 and 1/r^3 fields 

        for every body in the simulation grid simultaneously.
        """
        accelerations = {obj.name: [0.0, 0.0] for obj in self.objects}
        
        # O(N^2) loop to calculate intersecting field interference
        for i in range(len(self.objects)):
            p1 = self.objects[i]
            for j in range(len(self.objects)):
                if i == j:
                    continue
                p2 = self.objects[j]
                
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r = math.sqrt(dx**2 + dy**2)
                
                if r < 1e10: # Prevent divide-by-zero at coordinate floors
                    continue
                
                # Your custom dual-flux rules running on the grid
                baseline_flux = (G_CONSTANT * p2.mass) / (r**2)
                field_stacking = (G_CONSTANT * p2.mass) / (r**3)
                
                # Combine fields using your scalar and medium interference factors
                total_flux = (baseline_flux + (field_stacking * self.scalar)) * self.interference
                
                # Decompose into directional coordinate vectors
                accelerations[p1.name][0] += total_flux * (dx / r)
                accelerations[p1.name][1] += total_flux * (dy / r)
                
        return accelerations

    def step(self):
        """Executes your stable Velocity Verlet routine across the entire cluster."""
        # Step 1: Current accelerations
        accel1 = self._compute_all_accelerations()
        
        # Step 2: Update positions for all bodies
        for obj in self.objects:
            ax, ay = accel1[obj.name]
            obj.x += obj.vx * DT + 0.5 * ax * (DT**2)
            obj.y += obj.vy * DT + 0.5 * ay * (DT**2)
            
        # Step 3: Compute new accelerations at updated coordinates
        accel2 = self._compute_all_accelerations()
        
        # Step 4: Average accelerations to lock in velocity updates
        for obj in self.objects:
            ax1, ay1 = accel1[obj.name]
            ax2, ay2 = accel2[obj.name]
            obj.vx += 0.5 * (ax1 + ax2) * DT
            obj.vy += 0.5 * (ay1 + ay2) * DT

# --- SIMULATION INITIALIZATION ---
if __name__ == "__main__":
    # Initialize the galactic matrix
    galaxy = GalacticEngine(fluid_density_scalar=1e20, interference_factor=1.0)
    
    # 1. Place a supermassive core at the coordinate origin
    galaxy.add_body(GalacticObject("Galactic_Core", CORE_MASS, 0.0, 0.0, 0.0, 0.0))
    
    # 2. Place a series of outer stars at increasing distances (R) 
    # to measure if their velocities drop off or flatline into an attractor loop
    # Distances mapped in meters (approx. light-years scale)
    galaxy.add_body(GalacticObject("Inner_Rim_Star", STAR_MASS, 1.0e19, 0.0, 0.0, 35000.0))
    galaxy.add_body(GalacticObject("Mid_Disk_Star",  STAR_MASS, 3.0e19, 0.0, 0.0, 30000.0))
    galaxy.add_body(GalacticObject("Outer_Rim_Star", STAR_MASS, 6.0e19, 0.0, 0.0, 25000.0))
    
    print("--- RUNNING GALACTIC FIELD INTERFERENCE SIMULATION ---")
    for year_step in range(11):
        galaxy.step()
        print(f"\nStep {year_step} ({year_step * TIME_STEP_YEARS:.0f} Years):")
        for obj in galaxy.objects:
            if obj.name == "Galactic_Core": continue
            speed = math.sqrt(obj.vx**2 + obj.vy**2)
            r = math.sqrt(obj.x**2 + obj.y**2)
            print(f" -> {obj.name} | Radius: {r:.2e}m | Rotational Speed: {speed:.1f} m/s")