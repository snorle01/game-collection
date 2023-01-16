import math

# returns a single point in a spline based on the prosent
# prosent must be between 0.0-1.0
def point(point_0, point_1, point_2, point_3, prosent) -> tuple[int, int]:
    prosent2 = prosent * prosent
    prosent3 = prosent2 * prosent

    q1 = -prosent3 + 2.0 * prosent2 - prosent
    q2 = 3.0 * prosent3 - 5.0 * prosent2 + 2.0
    q3 = -3.0 * prosent3 + 4.0 * prosent2 + prosent
    q4 = prosent3 - prosent2

    prosent_x = 0.5 * (point_0[0] * q1 + point_1[0] * q2 + point_2[0] * q3 + point_3[0] * q4)
    prosent_y = 0.5 * (point_0[1] * q1 + point_1[1] * q2 + point_2[1] * q3 + point_3[1] * q4)

    return prosent_x, prosent_y

# return a list with points that can be used to make a spline between two points
# quality deterens how many points the spline should have. if you have many points the spline will be smooth, if you have few the spline will have edges
# if quality is not an int auto generate the quality based on the distance between point_1 and point_2
def make_spline(point_0, point_1, point_2, point_3, quality=None) -> list[tuple[int, int]]:
    # auto generate the quality based on the distance between point_1 and point_2
    if type(quality) == int:
        num_of_points = quality
    else:
        lenght_x = point_1[0] - point_2[0]
        lenght_y = point_1[1] - point_2[1]
        num_of_points = math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

    prosent = 0.0
    prosent_incroment = 1 / num_of_points
    return_list = []
    for i in range(int(num_of_points)):
        return_list.append(point(point_0, point_1, point_2, point_3, prosent))
        prosent += prosent_incroment
    return return_list

# return a big list with points
# classes determens if you want to use classes or tuples.
# if you are using classes the class has to have a get_pos() function to work
# quality deterens how many points the spline should have. if you have many points the spline will be smooth, if you have few the spline will have edges
# if quality is not an int auto generate the quality based on the distance between point_1 and point_2
def make_splines(points, classes=False, quality=None) -> list[tuple[int, int]]:
    # 4 points are needed to make a spline. if lenght of list is less then 4 make an error
    if len(points) < 4:
        raise Exception('list of points is less then 4')

    return_list = []
    for index in range(1, len(points)-2):

        # gets the points
        if classes:
            point_0 = points[index-1].get_pos()
            point_1 = points[index].get_pos()
            point_2 = points[index+1].get_pos()
            point_3 = points[index+2].get_pos()
        else:
            point_0 = points[index-1]
            point_1 = points[index]
            point_2 = points[index+1]
            point_3 = points[index+2]

        for point in make_spline(point_0, point_1, point_2, point_3, quality):
            return_list.append(point)

    return return_list

# returns a list of points that goes in a loop
# classes determens if you want to use classes or tuples.
# if you are using classes the class has to have a get_pos() function to work
# quality deterens how many points the spline should have. if you have many points the spline will be smooth, if you have few the spline will have edges
# if quality is not an int auto generate the quality based on the distance between point_1 and point_2
def make_loop(points, classes=False, quality=None) -> list[tuple[int, int]]:
    # 4 points are needed to make a spline. if lenght of list is less then 4 make an error
    if len(points) < 4:
        raise Exception('list of points is less then 4')

    return_list = []
    for index in range(len(points)):
        # makes sure the indexes is not invalid
        point_0_index = index-1
        if point_0_index < 0:
            point_0_index += len(points)

        point_2_index = index+1
        if point_2_index > len(points)-1:
            point_2_index -= len(points)

        point_3_index = index+2
        if point_3_index > len(points)-1:
            point_3_index -= len(points)

        # gets the points
        if classes:
            point_0 = points[point_0_index].get_pos()
            point_1 = points[index].get_pos()
            point_2 = points[point_2_index].get_pos()
            point_3 = points[point_3_index].get_pos()
        else:
            point_0 = points[point_0_index]
            point_1 = points[index]
            point_2 = points[point_2_index]
            point_3 = points[point_3_index]

        for point in make_spline(point_0, point_1, point_2, point_3, quality):
            return_list.append(point)

    return return_list

# returns the lenght of a spline in int
# this is not 100% accurate but you can get closer to the accuracy by changing steps
def lenght_of_spline(point_0, point_1, point_2, point_3, steps=10) -> int:
    incroment = 1 / steps
    lenght = 0
    for i in range(steps):
        point_a = point(point_0, point_1, point_2, point_3, incroment * i)
        point_b = point(point_0, point_1, point_2, point_3, incroment * 2 * i)
        lenght_x = point_a[0] - point_b[0]
        lenght_y = point_a[1] - point_b[1]
        lenght += math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)
    return lenght