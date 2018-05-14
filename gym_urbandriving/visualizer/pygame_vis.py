from gym_urbandriving.assets.car import Car
from gym_urbandriving.assets.primitives import Rectangle, Circle, Polygon
import sys
import pygame
import pygame.transform
import time
import numpy as np
import shapely
import cv2
import six

COLORS = [(255, 0, 0),
          (0, 255, 0),
          (0, 0, 255),
          (255, 255, 0),
          (255, 0, 255),
          (0, 255, 255),
          (128, 0, 0),
          (0, 128, 0),
          (0, 0, 128),
          (128, 128, 0),
          (128, 0, 128),
          (0, 128, 128)]

class PyGameVisualizer:

    """
    Py Game Visualizer.

    """

    def __init__(self, config, screen_dim):
        """
        Initializes pygame and its drawing surface.

        Parameters
        ----------
        screen_dim:
            Size of the window display.

        """

        pygame.init()
        self.config = config
        self.screen_dim = screen_dim
        self.surface = pygame.display.set_mode(screen_dim)
        self.drawfns = {Rectangle:self.draw_rectangle,
                        Circle:self.draw_circle,
                        Polygon:self.draw_polygon
        }
        self.static_surface = None

    def get_bitmap(self):
        """
        Returns the current displayed visualization as a bitmap array
        """
        return pygame.surfarray.pixels3d(self.surface)
    def render_statics(self, state, valid_area):
        """
        Renders the static objects of the state such as sidewalks and streets.

        Parameters
        ----------
        state: PositionState
            State object of the environment to be rendered. Should contain static and dynamic objects as well as collision checking information.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        """
        if self.static_surface:
            self.surface.blit(self.static_surface, (0, 0))
            return

        self.static_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                              valid_area[3] - valid_area[2]))
        for obj in state.static_objects:
            self.drawfns[obj.primitive](obj, self.static_surface)

        self.static_surface = pygame.transform.scale(self.static_surface,
                                                     (self.screen_dim))

        self.surface.blit(self.static_surface, (0, 0))
        return

    def render_dynamics(self, state, valid_area):
        """
        Renders dynamic objects of the state such as pedestrians and cars.

        Parameters
        ----------
        state: PositionState
            State object of the environment to be rendered. Should contain static and dynamic objects as well as collision checking information.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        """
        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)
        for key in state.dynamic_objects.keys():
            for index,obj in state.dynamic_objects[key].items():
                self.drawfns[obj.primitive](obj, new_surface)

        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)
        return


    def render_collisions(self, state, valid_area):
        """
        Renders a small circle on colliding cars for visual inspection of collisions.

        Parameters
        ----------
        state: PositionState
            State object of the environment to be rendered. Should contain static and dynamic objects as well as collision checking information.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        """
        dynamic_collisions, static_collisions, _ = state.get_collisions()

        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)


        for obj1id, obj2id, k1, k2 in dynamic_collisions:
            obj1 = state.dynamic_objects[k1][str(obj1id)]
            obj2 = state.dynamic_objects[k2][str(obj2id)]
            pygame.draw.circle(new_surface, (255, 0, 255), obj1.get_pos().astype(int), 5)
            pygame.draw.circle(new_surface, (255, 0, 255), obj2.get_pos().astype(int), 5)
        for obj1id, obj2id, k, _ in static_collisions:
            obj1id, obj2id = str(obj1id), obj2id
            obj1 = state.dynamic_objects[k][obj1id]
            obj2 = state.static_objects[obj2id]
            pygame.draw.circle(new_surface, (255, 0, 255), obj1.get_pos().astype(int), 5)
            pygame.draw.circle(new_surface, (255, 0, 255), obj2.get_pos().astype(int), 5)
        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)
        return


    def render_waypoints(self, waypoints, valid_area, index=0):
        """
        Renders dynamic objects of the state such as pedestrians and cars.

        Parameters
        ----------
        waypoints: list
            A list of [x, y] points that can be marked on the visualizer to use as guides.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        """
        index = int(index) % len(COLORS)
        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)
      
        for w in waypoints[1:]:
            pygame.draw.circle(new_surface, COLORS[index], [(int)(w[0]), (int)(w[1])], 3)
            #new_surface.fill(COLORS[index], ((int(w[0]), int(w[1])), (1, 1)))

        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)
        return


    def render_transparent_surface(self,img):
        img = cv2.resize(img, (0,0), fx=0.8, fy=0.8)
        cv2.imwrite('surface_img.png',255*img)
        image = pygame.image.load("surface_img.png")

        image = image.convert()

        image.set_alpha(128)
        self.surface.blit(image,(0,0))

    def render_traffic_trajectories(self, waypoints, valid_area):
        """
        Renders dynamic objects of the state such as pedestrians and cars.

        Parameters
        ----------
        waypoints: list
            A list of [x, y] points that can be marked on the visualizer to use as guides.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        """
        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)

        for w in waypoints:
            point, color = w
            pygame.draw.circle(new_surface, color, [(int)(point[0]), (int)(point[1])], 5)

        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)
        return


    def render(self, state, valid_area,
               rerender_statics=False, waypoints=[],traffic_trajectories = [], transparent_surface = None,
               lidar_points=[]):
        """
        Renders the state and waypoints with lazy re-rerendering of static objects as needed.

        Parameters
        ----------
        state: PositionState
            State object of the environment to be rendered. Should contain static and dynamic objects as well as collision checking information.

        valid_area: list
            Two points in the form [x_1, x_2, y_1, y_2] that define the viewing window of the state.

        rerender_statics: bool
            Whether to re-render static objects.

        waypoints: list
            Waypoints to add into the visualizer
        """
        if (rerender_statics):
            self.static_surface = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()


        self.render_statics(state, valid_area)
        self.render_dynamics(state, valid_area)
        self.render_collisions(state, valid_area)

        if len(traffic_trajectories) > 0:
            self.render_traffic_trajectories(traffic_trajectories, valid_area)

        
        for key in state.dynamic_objects.keys():
            for index,dobj in state.dynamic_objects[key].items():
                if not dobj.trajectory is None and ('x' in dobj.trajectory.mode and 'y' in dobj.trajectory.mode):
                    self.render_waypoints(dobj.trajectory.get_renderable_points(), valid_area, index)

        if lidar_points:
            self.render_lidar(state, valid_area, lidar_points)

        pygame.display.flip()

    def render_lidar(self, state, valid_area, lidar_points):
        new_surface = pygame.Surface((valid_area[1] - valid_area[0],
                                      valid_area[3] - valid_area[2]),
                                     pygame.SRCALPHA)

        for k, p in six.iteritems(lidar_points):
            if self.config['agents']['state_space_config']['goal_position']:
                rays = p[4:-2]
            else:
                rays = p[1:-2]
            n_rays = int(len(rays) / 4)
            angle = -np.pi / 2
            car = state.dynamic_objects['controlled_cars'][k]
            x, y, ca, vel = car.get_state()
            if self.config['agents']['state_space_config']['goal_position']:
                ga = np.arctan2(p[1], p[2])
                dga = p[3]
                ga = (ga + ca)

                pygame.draw.line(new_surface, (255, 0, 0), (x, y), (x + dga * np.cos(ga),
                                                                    y - dga * np.sin(ga)), 2)
                

            for i in range(n_rays):
                ray = rays[i*4:i*4+4]


                arc_angle = ca + angle
                beam_distance = ray[0]
                pygame.draw.line(new_surface, (0, 255, 0), (x, y), (x + beam_distance * np.cos(arc_angle),
                                                                    y - beam_distance * np.sin(arc_angle)), 2)
                angle += np.pi / (n_rays - 1)
            tld = p[-2]
            tlc = p[-1]
            
            pygame.draw.circle(new_surface, {-1:(0, 0, 0),
                                             0:(0, 255, 0),
                                             0.5:(255, 255, 0),
                                             1:(255, 0, 0)}[tlc], car.get_pos().astype(int), 5)
        new_surface = pygame.transform.scale(new_surface, (self.screen_dim))
        self.surface.blit(new_surface, (0, 0), None)

    def draw_rectangle(self, rect, surface):
        obj = pygame.image.load(rect.get_sprite())
        obj = pygame.transform.scale(obj, (rect.xdim, rect.ydim))
        corners = rect.get_corners()
        if rect.angle == 0:
            pos = (rect.x - rect.xdim/2, rect.y - rect.ydim/2)
        else:
            x_off = min(corners[:,0])
            y_off = min(corners[:,1])
            pos = (x_off, y_off)
            obj = pygame.transform.rotate(obj, np.rad2deg(rect.angle))
        surface.blit(obj, pos)
        return

    def draw_circle(self, circ, surface):
        obj = pygame.image.load(circ.get_sprite())
        obj = pygame.transform.scale(obj, (circ.radius*2, circ.radius*2))
        obj = pygame.transform.rotate(obj, np.rad2deg(circ.angle))
        surface.blit(obj, (circ.x-circ.radius,circ.y-circ.radius))
        return

    def draw_polygon(self, poly, surface):
        pygame.draw.polygon(surface, poly.color, poly.points, 0)
        pygame.draw.polygon(surface, (0, 0, 0), poly.points, 4)
        return
