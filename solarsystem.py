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

a_initial = np.linspace(5,15,num=110)

surv_time = np.zeros(shape=(len(a_initial),6))

for i,a in enumerate(a_initial):
    sim.add(a=a,f=2*np.pi*np.random.uniform(),hash=str(i)+'a')

sim.N_active = 9

for i,part in enumerate(sim.particles[1:9]):
    part.r = 1.32*part.calculate_orbit(primary=sim.particles[0]).a*part.m**0.4

for i,part in enumerate(sim.particles[9:]):
    surv_time[i,0] = part.hash.value
    surv_time[i,1] = part.a
    surv_time[i,2] = part.f
    surv_time[i,3] = np.nan
    surv_time[i,5] = 0

def my_merge(sim_pointer, collided_particles_index):

    sim = sim_pointer.contents # retreive the standard simulation object
    sim.integrator_synchronize()
    ps = sim.particles # easy access to list of particles

    i = collided_particles_index.p1   # Note that p1 < p2 is not guaranteed.    
    j = collided_particles_index.p2

    time = sim.t
    if ps[j].m > 0:
        val = ps[i].hash.value
        idx = np.where(surv_time[:,0]==val)
        surv_time[idx,3] = time
        surv_time[idx,4] = j
        return 1 # remove particle with index i
    elif ps[i].m > 0:
        val = ps[j].hash.value
        idx = np.where(surv_time[:,0]==val)
        surv_time[idx,3] = time
        surv_time[idx,4] = i
        return 2 # remove particle with index j

sim.collision = "line"
sim.collision_resolve = my_merge # user defined collision resolution function

for i,part in enumerate(sim.particles[1:9]):
    print(part.calculate_orbit(primary=sim.particles[0]))

times = np.linspace(0,t_end,num=51)
sim.exit_max_distance = 50.


for t in times:
    print(t/2/np.pi,flush=True)
    try:
        sim.integrate(t)
    except rebound.Escape as error:
        print(error)
        for j in range(sim.N):
            p = sim.particles[j]
            d2 = p.x*p.x + p.y*p.y + p.z*p.z
            if d2>sim.exit_max_distance**2:
                index=j # cache index rather than remove here since our loop would go beyond end of particles array
                val = p.hash.value
                idx = np.where(surv_time[:,0]==val)
                surv_time[idx,3] = sim.t
                surv_time[idx,4] = 0.5
        sim.remove(index=index)
surv_time = np.nan_to_num(surv_time,nan=sim.t)

for i,part in enumerate(sim.particles[1:9]):
    print(part.calculate_orbit(primary=sim.particles[0]))

for i,part in enumerate(sim.particles[9:]):
    val = part.hash.value
    idx = np.where(surv_time[:,0]==val)
    surv_time[idx,5] = part.a

np.savetxt('survival_times.txt',surv_time)