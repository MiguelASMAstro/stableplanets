import numpy as np
import rebound
import matplotlib.pyplot as plt
import time
import sys

dt = float(sys.argv[1])
runnum = int(sys.argv[2])
t_end = 1e7*2*np.pi
p2p1 = 1.8

sim = rebound.Simulation()
sim.add(m=1)
sim.add(m=0.00005149, P=2*np.pi,e=0.03,inc=0.01,f=np.pi)
sim.add(m=0.00005149, P=p2p1*2*np.pi,e=0.03,inc=0.01,f=0.75*np.pi)

sim.integrator = "whckl"
sim.dt = dt*2*np.pi
sim.ri_whfast.safe_mode = False

a1 = sim.particles[1].a + 1.5*0.00005149**(2/7)
a2 = sim.particles[2].a - 1.5*0.00005149**(2/7)

a_s = np.linspace(a1,a2,num=10)
a_initial = a_s[runnum]

for i,part in enumerate(sim.particles[1:3]):
    part.r = part.calculate_orbit(primary=sim.particles[0]).a*part.m**0.4

sim.add(a=a_initial,f=0.25*np.pi)
sim.N_active = 3

sim.move_to_com()

sim.collision = "line"
sim.collision_resolve = "halt" # user defined collision resolution function

sim.exit_max_distance = 50.

start = time.perf_counter()
try:
    sim.integrate(t_end)
    stop = time.perf_counter()
    print(a_initial,sim.t/2/np.pi,0,stop-start)
except rebound.Escape as esc:
    stop = time.perf_counter()
    print(a_initial,sim.t/2/np.pi,-1,stop-start)
except rebound.Collision as col:
    stop = time.perf_counter()
    for i,p in enumerate(sim.particles[1:3]):
        if p.lastcollision == sim.t:
            print(a_initial,sim.t/2/np.pi,i+1,stop-start)
