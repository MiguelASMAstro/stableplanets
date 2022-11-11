import numpy as np
import rebound
import reboundx
from reboundx import constants

t_end = 1e4*2*np.pi

sim = rebound.Simulation()
sim.add("Sun")
sim.add("Mercury")
sim.add("Venus")
sim.add("Earth")
sim.add("Mars")
sim.add("Jupiter")
sim.add("Saturn")
sim.add("Uranus")
sim.add("Neptune")

sim.integrator = "WHCKL" 
sim.ri_whfast.safe_mode = False
sim.dt = 1e-2

sim.move_to_com()

rebx = reboundx.Extras(sim)
gr = rebx.load_force("gr")
gr.params["c"] = constants.C
rebx.add_force(gr)

a_initial = np.linspace(5,15,num=70)
phases = np.array([0,0.3,0.7,1.1,1.5,1.9])
letters = ['a','b','c','d','e','f']

surv_time = np.zeros(shape=(len(a_initial)*len(phases),4))

for i,a in enumerate(a_initial):
    for f,l in zip(phases,letters):
        sim.add(a=a,f=np.pi*f,hash=str(i)+l)

sim.N_active = 9

for i,part in enumerate(sim.particles[1:9]):
    part.r = part.calculate_orbit(primary=sim.particles[0]).a*part.m**0.4

for i,part in enumerate(sim.particles[9:]):
    surv_time[i,0] = part.hash.value
    surv_time[i,1] = part.a
    surv_time[i,2] = part.f
    surv_time[i,3] = t_end

def my_merge(sim_pointer, collided_particles_index):

    sim = sim_pointer.contents # retreive the standard simulation object
    ps = sim.particles # easy access to list of particles

    i = collided_particles_index.p1   # Note that p1 < p2 is not guaranteed.    
    j = collided_particles_index.p2

    time = sim.t
    sim.ri_whfast.recalculate_coordinates_this_timestep = 1
    if ps[j].m > 0:
        val = ps[i].hash.value
        idx = np.where(surv_time[:,0]==val)
        surv_time[idx,3] = time
        return 1 # remove particle with index i
    elif ps[i].m > 0:
        val = ps[j].hash.value
        idx = np.where(surv_time[:,0]==val)
        surv_time[idx,3] = time
        return 2 # remove particle with index j

sim.collision = "direct"
sim.collision_resolve = my_merge # user defined collision resolution function

while sim.t<t_end:
    print(sim.t,flush=True)
    sim.integrate(sim.t+0.01*t_end)

np.savetxt('survival_times.txt',surv_time)