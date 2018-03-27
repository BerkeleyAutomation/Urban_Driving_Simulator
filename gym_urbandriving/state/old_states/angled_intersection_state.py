from gym_urbandriving.state.state import PositionState
from gym_urbandriving.assets import Terrain, Lane, Street, Sidewalk,\
    Pedestrian, Car, TrafficLight
import numpy as np

class AngledIntersectionState(PositionState):
    static_objects = [Terrain(0,0,0,0, points = [(0,0), (200,0), (400,400), (0,400)]),
                      Terrain(0,0,0,0, points = [(200+400/np.sqrt(3),0), (1000,0), (1000,400),  (400+400/np.sqrt(3),400)]),
                      Terrain(0,0,0,0, points = [(0,600), (750-400/np.sqrt(3),600), (950-400/np.sqrt(3),1000), (0,1000)]), 
                      Terrain(0,0,0,0, points = [(750,600), (1000,600), (1000,1000), (950,1000)]), 
                      Lane(200, 450, 400, 100, angle=-np.pi),
                      Lane(200, 550, 400, 100),
                      Lane(875, 450, 250, 100, angle=-np.pi),
                      Lane(875, 550, 250, 100),
                      Lane(0,0,0,0, angle=-np.radians(60), points = [(200,0), (200+200/np.sqrt(3),0), (400+200/np.sqrt(3),400), (400,400)]),
                      Lane(0,0,0,0, angle=np.radians(120), points = [(200+200/np.sqrt(3),0), (200+400/np.sqrt(3),0), (400+400/np.sqrt(3),400), (400+200/np.sqrt(3),400)]),
                      Lane(0,0,0,0, angle=-np.radians(60), points = [(750-400/np.sqrt(3),600), (750-200/np.sqrt(3),600), (950-200/np.sqrt(3),1000), (950-400/np.sqrt(3),1000)]),
                      Lane(0,0,0,0, angle=np.radians(120), points = [(750-200/np.sqrt(3),600), (750,600), (950,1000), (950-200/np.sqrt(3),1000)]),
                      Street(575, 500, 350, 200),

                      #Sidewalk(200, 400, 400, 50, angle=-np.pi),
                      #Sidewalk(200, 650, 400, 50),
                      #Sidewalk(875, 400, 250, 50, angle=-np.pi),
                      Sidewalk(0,0,0,0, angle=-np.radians(60), points = [(200-100/np.sqrt(3),0), (200,0), (400,400), (400-100/np.sqrt(3),400)]),
                      Sidewalk(0,0,0,0, angle=-np.pi, points = [(0,350), (400-50/np.sqrt(3),400-50), (400,400), (0,400)]),
                      Sidewalk(0,0,0,0, angle=np.radians(120), points = [(200+400/np.sqrt(3),0), (200+500/np.sqrt(3),0), (400+500/np.sqrt(3),400), (400+400/np.sqrt(3),400)]),
                      Sidewalk(0,0,0,0, points = [(400+350/np.sqrt(3),400-50), (1000,350), (1000,400), (400+400/np.sqrt(3),400)]),
                      Sidewalk(0,0,0,0, angle=-np.radians(60), points = [(750-500/np.sqrt(3),600), (750-400/np.sqrt(3),600), (950-400/np.sqrt(3),1000), (950-500/np.sqrt(3),1000)]),
                      Sidewalk(0,0,0,0, points = [(0,600), (750-400/np.sqrt(3),600), (750-350/np.sqrt(3),650), (0,650)]),
                      Sidewalk(0,0,0,0, angle=np.radians(120), points = [(750,600), (750+100/np.sqrt(3),600), (950+100/np.sqrt(3),1000), (950,1000)]),
                      Sidewalk(0,0,0,0, angle=-np.pi, points = [(750,600), (1000,600), (1000,650), (750+50/np.sqrt(3),650)])

                      ]
    def randomize(self):
        
        self.dynamic_objects = []
        while len(self.dynamic_objects) < self.ncars:
            lane = [
                      Lane(200, 550, 400, 100),
                      Lane(875, 450, 250, 100, angle=-np.pi),
                      Lane(0,0,0,0, angle=-np.radians(60), points = [(200,0), (200+200/np.sqrt(3),0), (400+200/np.sqrt(3),400), (400,400)]),
                      Lane(0,0,0,0, angle=np.radians(120), points = [(750-200/np.sqrt(3),600), (750,600), (950,1000), (950-200/np.sqrt(3),1000)]),

            ][np.random.random_integers(0, 3)]
            car = lane.generate_car()
            car.vel = 0
            if not any([car.collides(obj) for obj in self.static_objects+self.dynamic_objects]):
              self.dynamic_objects.append(car)
       
        if self.traffic_lights:
            self.dynamic_objects.append(TrafficLight(750, 440, 0))
            self.dynamic_objects.append(TrafficLight(400, 560, -np.pi))
            self.dynamic_objects.append(TrafficLight(580, 600, -(np.pi/2), initial_color="red"))
            self.dynamic_objects.append(TrafficLight(460, 400, (np.pi/2), initial_color="red"))
