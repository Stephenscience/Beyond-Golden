import math

# --- CORE AXIOMS (From your framework) ---
G_CONSTANT = 6.6743e-11  
C_SPEED = 299792458.0      # The absolute structural speed limit of bonded matter
SMBH_MASS = 8.0e36         # Supermassive Black Hole (~4 Million Solar Masses)
STAR_MASS = 2.0e30         # Average mass of an individual star (1 solar mass)

# For a black hole event horizon, things move incredibly fast. 
# We need a smaller time step to prevent clipping through the coordinate grid.
DT = 100.0                 # 100-second simulation steps

class BHObject:
    def __init__(self, name, mass, x, y, vx, vy):
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.annihilated = False  # Track if the 2=1 bond has been broken

class BlackHoleEngine:
    def __init__(self, fluid_density_scalar=5e11, interference_factor=1.0):
        self.objects = []
        self.scalar = fluid_density_scalar  # Scales the 1/r^3 stacking field
        self.interference = interference_factor

    def add_body(self, body):
        self.objects.append(body)

    def _compute_all_accelerations(self):
        """Calculates intersecting vector sum of 1/r^2 and 1/r^3 fields"""
        accelerations = {obj.name: [0.0, 0.0] for obj in self.objects}
        
        for i in range(len(self.objects)):
            p1 = self.objects[i]
            # Un-bonded (annihilated) matter no longer interacts with the EM grid
            if p1.annihilated: 
                continue
            
            for j in range(len(self.objects)):
                if i == j: continue
                p2 = self.objects[j]
                if p2.annihilated: continue
                
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                r = math.sqrt(dx**2 + dy**2)
                
                # Coordinate floor (prevents divide-by-zero singularities)
                if r < 1000.0: 
                    continue
                
                # Your exact Dual-Flux Rules
                baseline_flux = (G_CONSTANT * p2.mass) / (r**2)
                field_stacking = (G_CONSTANT * p2.mass) / (r**3)
                
                total_flux = (baseline_flux + (field_stacking * self.scalar)) * self.interference
                
                accelerations[p1.name][0] += total_flux * (dx / r)
                accelerations[p1.name][1] += total_flux * (dy / r)
                
        return accelerations

    def step(self):
        """Executes the stable Velocity Verlet routine"""
        accel1 = self._compute_all_accelerations()
        
        # Position Update
        for obj in self.objects:
            if obj.annihilated or obj.name == "Singularity_Core": continue
            ax, ay = accel1[obj.name]
            obj.x += obj.vx * DT + 0.5 * ax * (DT**2)
            obj.y += obj.vy * DT + 0.5 * ay * (DT**2)
            
        accel2 = self._compute_all_accelerations()
        
        # Velocity Update & Axiom Checking
        for obj in self.objects:
            if obj.annihilated or obj.name == "Singularity_Core": continue
            ax1, ay1 = accel1[obj.name]
            ax2, ay2 = accel2[obj.name]
            obj.vx += 0.5 * (ax1 + ax2) * DT
            obj.vy += 0.5 * (ay1 + ay2) * DT
            
            # --- THE BLACK HOLE THRESHOLD TEST (Section 13.1) ---
            # Measure if the object has exceeded the structural energy limit
            speed = math.sqrt(obj.vx**2 + obj.vy**2)
            if speed >= C_SPEED:
                obj.annihilated = True
                obj.vx = 0.0
                obj.vy = 0.0

# --- SIMULATION INITIALIZATION ---
if __name__ == "__main__":
    universe = BlackHoleEngine(fluid_density_scalar=5e11)
    
    # 1. The Supermassive Core
    universe.add_body(BHObject("Singularity_Core", SMBH_MASS, 0.0, 0.0, 0.0, 0.0))
    
    # 2. Safe_Star: Far out, 1/r^2 dominant, should maintain a stable orbit
    universe.add_body(BHObject("Safe_Star", STAR_MASS, 1.0e13, 0.0, 0.0, 7300000.0))
    
    # 3. Grazing_Star: Dips close to the 1/r^3 field stacking zone, should experience extreme precession/wobble
    universe.add_body(BHObject("Grazing_Star", STAR_MASS, 1.0e12, 0.0, 0.0, 18000000.0))
    
    # 4. Doomed_Star: Inside the Innermost Stable Circular Orbit. The 1/r^3 stacking will overwhelm it.
    universe.add_body(BHObject("Doomed_Star", STAR_MASS, 5.0e10, 0.0, 0.0, 30000000.0))
    
    print("--- RUNNING SUPERMASSIVE BLACK HOLE SIMULATION ---")
    
    for step_num in range(101):
        universe.step()
        
        # Print telemetry every 10 steps
        if step_num % 10 == 0:
            print(f"\nTime: {step_num * DT} Seconds")
            for obj in universe.objects:
                if obj.name == "Singularity_Core": continue
                
                if obj.annihilated:
                    print(f" -> [X] {obj.name} HAS EXPERIENCED AXIAL ANNIHILATION. Bond Broken. Reverted to Substrate.")
                else:
                    speed = math.sqrt(obj.vx**2 + obj.vy**2)
                    r = math.sqrt(obj.x**2 + obj.y**2)
                    print(f" -> {obj.name} | Radius: {r:.2e} m | Speed: {speed:.1f} m/s")