import fluids
from fluids.utils import fluids_print
import argparse

key_help = """
Keyboard commands for when visualizer is running:
   .            Increases debug visualization
   ,            Decreases debug visualization
   o            Switches observation type
"""

parser = argparse.ArgumentParser(description='FLUIDS First Order Lightweight Urban Intersection Driving Simulator',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=key_help)
parser.add_argument('-b', metavar='N', type=int, default=10, 
                    help='Number of background cars')
parser.add_argument('-c', metavar='N', type=int, default=1, 
                    help='Number of controlled cars')
parser.add_argument('-p', metavar='N', type=int, default=5, 
                    help='Number of background pedestrians')
parser.add_argument('-v', metavar='N', type=int, default=1,
                    help='Visualization level')
parser.add_argument('-o', metavar='str', type=str, default="birdseye",
                    choices=["none", "birdseye", "grid"],
                    help='Observation type')
parser.add_argument('--time', metavar='N', type=int, default=0,
                    help="Max time to run simulation")
parser.add_argument('--state', metavar='file', type=str, default=fluids.STATE_CITY,
                    help='Layout file for state generation')

args = parser.parse_args()
fluids_print("Parameters: Num background cars : {}".format(args.b))
fluids_print("            Num controlled cars : {}".format(args.c))
fluids_print("            Num controlled peds : {}".format(args.p))
fluids_print("            Visualization level : {}".format(args.v))
fluids_print("            Observation type    : {}".format(args.o))
fluids_print("            Scene layout        : {}".format(args.state))
fluids_print("            Simulation time     : {}".format("unlimited" if not args.time else args.time))
fluids_print("")


obs = {"none"     :fluids.OBS_NONE,
       "birdseye" :fluids.OBS_BIRDSEYE,
       "grid"     :fluids.OBS_GRID}[args.o]
simulator = fluids.FluidSim(visualization_level=args.v,
                            state              =args.state,
                            background_cars    =args.b,
                            controlled_cars    =args.c,
                            background_peds    =args.p,
                            fps                =0,
                            obs_space          =obs,
                            background_control =fluids.BACKGROUND_CSP)

t = 0
while not args.time or t < args.time:
    actions = {k: fluids.KeyboardAction() for k in simulator.get_control_keys()}
    rew = simulator.step(actions)
    obs = simulator.get_observations(simulator.get_control_keys())
    simulator.render()
    t = t + 1

