def transform(x,y,angle,points):
    res = []
    rotation = np.matrix([[np.cos(angle), np.sin(angle)],[-np.sin(angle), np.cos(angle)]])
    translation = np.matrix([[x], [y]])
    for p in points:
        p_mat = np.matrix([[p[0]], [p[1]]])
        this_point = (rotation.dot(p_mat) + translation).flatten().tolist()[0]
        this_point.extend(p[2:])
        res.append(this_point)
    return res