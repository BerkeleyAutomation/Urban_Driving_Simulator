from six import iteritems
import numpy as np
import pygame
from fluids.assets.shape import Shape
from fluids.obs.obs import FluidsObs
from fluids.utils import rotation_array
from scipy.misc import imresize
from fluids.consts import *

class GridObservation(FluidsObs):
    """
    Grid observation type. 
    Observation is an occupancy grid over the detection region. 
    Observation has 11 dimensions: terrain, drivable regions, illegal drivable 
    regions, cars, pedestrians, traffic lights x 3, way points, point trajectory and edge trajectory.
    Array representation is (grid_size, grid_size, 11)
    """
    def __init__(self, car, obs_dim=500, shape=(500,500)):
        from fluids.assets import ALL_OBJS, TrafficLight, Lane, Terrain, Sidewalk, \
            PedCrossing, Street, Car, Waypoint, Pedestrian
        state = car.state
        self.car = car
        self.shape = shape
        self.grid_dim = obs_dim
        self.downsample = self.shape != (obs_dim, obs_dim)
        self.grid_square = Shape(x=car.x+obs_dim/3*np.cos(car.angle),
                                 y=car.y-obs_dim/3*np.sin(car.angle),
                                 xdim=obs_dim, ydim=obs_dim, angle=car.angle,
                                 color=None, border_color=(200,0,0))
        self.all_collideables = []
        collideable_map = {typ:[] for typ in ALL_OBJS}
        for k, obj in iteritems(state.objects):
            if (car.can_collide(obj) or type(obj) in {TrafficLight, Lane, Street}) and self.grid_square.intersects(obj):
                typ = type(obj)
                if typ == TrafficLight:
                    if obj.color == RED:
                        typ = "TrafficLight-Red"
                    elif obj.color == GREEN:
                        typ = "TrafficLight-Green"
                    elif obj.color == YELLOW:
                        typ = "TrafficLight-Yellow"
                if typ not in collideable_map:
                    collideable_map[typ] = []
                collideable_map[typ].append(obj)
                self.all_collideables.append(obj)
        for waypoint in car.waypoints:
            collideable_map[Waypoint].append(waypoint)
            self.all_collideables.append(waypoint)

        terrain_window    = pygame.Surface((self.grid_dim, self.grid_dim))
        drivable_window   = pygame.Surface((self.grid_dim, self.grid_dim))
        undrivable_window = pygame.Surface((self.grid_dim, self.grid_dim))
        car_window        = pygame.Surface((self.grid_dim, self.grid_dim))
        ped_window        = pygame.Surface((self.grid_dim, self.grid_dim))
        light_window_red  = pygame.Surface((self.grid_dim, self.grid_dim))
        light_window_green= pygame.Surface((self.grid_dim, self.grid_dim))
        light_window_yellow=pygame.Surface((self.grid_dim, self.grid_dim))
        direction_window  = pygame.Surface((self.grid_dim, self.grid_dim))
        direction_pixel_window \
                          = pygame.Surface((self.grid_dim, self.grid_dim))
        direction_edge_window \
                          = pygame.Surface((self.grid_dim, self.grid_dim))

        gd = self.grid_dim
        a0 = self.car.angle + np.pi / 2
        a1 = self.car.angle
        rel = (self.car.x+gd/2*np.cos(a0)-gd/6*np.cos(a1),
               self.car.y-gd/2*np.sin(a0)+gd/6*np.sin(a1),
               self.car.angle)

        for typ in [Terrain, Sidewalk, PedCrossing]:
            for obj in collideable_map[typ]:
                rel_obj = obj.get_relative(rel)
                rel_obj.render(terrain_window, border=None)

        for obj in collideable_map[Lane]:
            rel_obj = obj.get_relative(rel)
            if not car.can_collide(obj):
                rel_obj.render(drivable_window, border=None)
            else:
                rel_obj.render(undrivable_window, border=None)
        for obj in collideable_map[Street]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(drivable_window, border=None)

        for obj in collideable_map[Car]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(car_window, border=None)

        for obj in collideable_map[Pedestrian]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(ped_window, border=None)

        for obj in collideable_map["TrafficLight-Red"]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(light_window_red, border=None)

        for obj in collideable_map["TrafficLight-Green"]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(light_window_green, border=None)
        
        for obj in collideable_map["TrafficLight-Yellow"]:
            rel_obj = obj.get_relative(rel)
            rel_obj.render(light_window_green, border=None)

        point = (int(gd/6), int(gd/2))
        edge_point = None

        def is_on_screen(point, gd):
            return 0 <= point[0] < gd and 0 <= point[1] < gd
        
        line_width = 20
        for p in self.car.waypoints:
            relp = p.get_relative(rel)
            new_point = int(relp.x), int(relp.y)
            if not edge_point and is_on_screen(point, gd) and not is_on_screen(new_point, gd):
                edge_point = new_point

            pygame.draw.line(direction_window, (255, 255, 255), point, new_point, line_width)
            point = new_point
        
        if edge_point:
            edge_point = (min(gd - 1, max(0, edge_point[0])), min(gd - 1, max(0, edge_point[1])))
            pygame.draw.circle(direction_pixel_window, (255, 255, 255), edge_point, line_width)
        
        if edge_point:
            if edge_point[0] == 0:
                pygame.draw.line(direction_edge_window, (255, 255, 255), (0, 0), (0, gd - 1), line_width)
            if edge_point[0] == gd - 1:
                pygame.draw.line(direction_edge_window, (255, 255, 255), (gd - 1, 0), (gd - 1, gd - 1), line_width)
            if edge_point[1] == 0:
                pygame.draw.line(direction_edge_window, (255, 255, 255), (0, 0), (gd - 1, 0), line_width)
            if edge_point[1] == gd - 1:
                pygame.draw.line(direction_edge_window, (255, 255, 255), (0, gd - 1), (gd - 1, gd - 1), line_width)


        self.pygame_rep = [pygame.transform.rotate(window, 90) for window in [terrain_window,
                                                                              drivable_window,
                                                                              undrivable_window,
                                                                              car_window,
                                                                              ped_window,
                                                                              light_window_red,
                                                                              light_window_green,
                                                                              light_window_yellow,
                                                                              direction_window,
                                                                              direction_pixel_window,
                                                                              direction_edge_window
                                                                              ]]

    def render(self, surface):
        self.grid_square.render(surface, border=10)
        if self.car.vis_level > 3:

            if self.car.vis_level > 4:
                for obj in self.all_collideables:
                    obj.render_debug(surface)
            for y in range(4):
                for x in range(2):
                    i = y + x * 4
                    if i < len(self.pygame_rep):
                        surface.blit(self.pygame_rep[i], (surface.get_size()[0] - self.grid_dim * (x+1), self.grid_dim * y))
                        pygame.draw.rect(surface, (200, 0, 0),
                                         pygame.Rect((surface.get_size()[0] - self.grid_dim*(x+1)-5, 0-5+self.grid_dim*y),
                                                     (self.grid_dim+10, self.grid_dim+10)), 10)

    def get_array(self):
        arr = np.zeros((self.grid_dim, self.grid_dim, len(self.pygame_rep)))
        for i in range(len(self.pygame_rep)):
            arr[:,:,i] = pygame.surfarray.array2d(self.pygame_rep[i]) != 0
            # print(pygame.surfarray.array2d(self.pygame_rep[i]) != 0)
            
        if self.downsample:
            arr = self.sp_imresize(arr, self.shape)
        return arr
    
    def sp_imresize(self, arr, shape):
        return np.array([imresize(arr[:,:,i],shape) for i in range(arr.shape[2])]).T
            
    # def label_distribution_from_block(self, arr, start, end):
    #     """Returns the distribution of labels in a block from arr.

    #     If start or end are floats, the distribution includes weighted elements
    #     on the edge of the block.

    #     Args:
    #         arr (np.ndarray): 3D array from which to obtain the block where the
    #             3rd dimension is a one-hot encoded vector of labels.
    #         start (tuple of floats): top left corner of the block.
    #         end (tuple of floats): bottom right corner of block.

    #     Returns:
    #         Array containing the distribution of labels.
    #     """
    #     assert len(start) == len(end) == 2
    #     assert len(arr.shape) == 3
    #     start = np.array(start)
    #     end = np.array(end)

    #     start_idx = np.ceil(start).astype(np.int)
    #     end_idx = np.floor(end).astype(np.int)

    #     counts = np.sum(arr[start_idx[0]:end_idx[0], start_idx[1]:end_idx[1]],
    #                     axis=(0, 1))

    #     NUM_DECIMALS = 7    # Prevents floating point errors
    #     top_weight, left_weight = np.round(-start % 1, NUM_DECIMALS)
    #     bottom_weight, right_weight = np.round(end, NUM_DECIMALS) % 1

    #     counts = counts.astype(np.float)

    #     # Edges not including corners
    #     if top_weight > 1e-4:   # Tolerate floating point errors with small numbers
    #         counts += top_weight * \
    #                 np.sum(arr[start_idx[0] - 1, start_idx[1]:end_idx[1]], axis=0)
    #     if bottom_weight > 1e-4:
    #         counts += bottom_weight * \
    #                 np.sum(arr[end_idx[0], start_idx[1]:end_idx[1]], axis=0)
    #     if left_weight > 1e-4:
    #         counts += left_weight * \
    #                 np.sum(arr[start_idx[0]:end_idx[0], start_idx[1] - 1],
    #                        axis=0)
    #     if right_weight > 1e-4:
    #         counts += right_weight * \
    #                 np.sum(arr[start_idx[0]:end_idx[0], end_idx[1]],
    #                        axis=0)
    #     # Corners
    #     if top_weight and left_weight:
    #         counts += top_weight * left_weight * arr[start_idx[0], start_idx[1]]
    #     if top_weight and right_weight:
    #         counts += top_weight * right_weight * arr[start_idx[0], end_idx[1]]
    #     if bottom_weight and left_weight:
    #         counts += bottom_weight * left_weight * arr[end_idx[0], start_idx[1]]
    #     if bottom_weight and right_weight:
    #         counts += bottom_weight * right_weight * arr[end_idx[0], end_idx[1]]

    #     return counts / np.sum(counts)

    # def to_low_res_truth(self, labeled_img, shape, nsamples=None):
    #     """Calculates the distrubution of each region.

    #     Uses the area of intersection between each pixel and the larger low-res
    #     region to weight each label in order to construct the distribution.

    #     Args:
    #         labeled_img (np.ndarray): 3D array from which to obtain the block
    #             where the 3rd dimension is a one-hot encoded vector of labels.
    #         shape (tuple of length 2): output resolution.
    #         nsamples: dummy argument to mantain API consistency.

    #     Returns:
    #         Low resolution array where the 3rd dimension contains the distribution
    #         of labels present within the high resolution elements corresponding
    #         to the location in the low resolution array.
    #     """
    #     assert len(labeled_img.shape) == 3

    #     row_step, col_step = np.divide(labeled_img.shape[0:2], shape)

    #     low_res = np.array([[self.label_distribution_from_block(
    #                             labeled_img, (i, j), (i + row_step, j + col_step))
    #                          for j in np.arange(0, labeled_img.shape[1], col_step)]
    #                         for i in np.arange(0, labeled_img.shape[0], row_step)])

    #     return low_res
