
def path_reward(state):
    controlled_cars = [state.objects[k] for k in state.controlled_cars.keys()]
    collisions = [-500 if state.is_in_collision(car) else 0 for car in controlled_cars]
    return sum([c.last_to_goal for c in controlled_cars]) + sum(collisions)

    
