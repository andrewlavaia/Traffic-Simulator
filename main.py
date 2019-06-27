import pdb
import time
import sys

from graphics import GraphWin, GraphicsError, Text, Point
from menu import MainMenu
from graphs import Graph, ShortestPaths
from maps import RoadMap
from cars import Car, CarShape, CarFactory
from gps import GPS
from info_window import InfoWindow
from collision import CollisionSystem
from latlon import LatLonConverter
from openstreetmap import query_roads_by_lat_lon, save_raw_json_map_data


def main():
    window.setBackground('white')
    window.clear()
    window.resetView()
    secondary_window.setBackground('white')
    secondary_window.clear()

    # S, W, N, E = "40.9946", "-73.8817", "41.0174", "-73.8281"  # lower westchester
    S, W, N, E = "40.73489", "-73.99264", "40.74020", "-73.97923"  # NYC lower east side
    # overpass_query = query_roads_by_lat_lon(S, W, N, E)
    # save_raw_json_map_data(overpass_query, "map_data.txt")

    llc = LatLonConverter(window, S, W, N, E)

    graph = Graph()
    graph.loadOpenStreetMapData("map_data.txt", llc)

    road_map = RoadMap(graph, window)
    road_map.draw()

    gps = GPS(graph, road_map)

    cars = []
    car_shapes = []
    car_factory = CarFactory(window, gps, cars, car_shapes)

    num_cars = 50
    for i in range(num_cars):
        car_factory.create()

    for car_shape in car_shapes:
        car_shape.draw()

    collision_system = CollisionSystem(window, cars)

    info = InfoWindow(secondary_window)
    info.setSelectedCar(cars[0])
    car_shapes[info.selected_car.index].shape.setFill("yellow")

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 60
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND
    nextLogicTick = TIME_PER_TICK
    lastFrameTime = time.time()
    lag = 0.0

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime
        lag += elapsed
        simTime += elapsed

        # process events
        try:
            last_pressed_key = window.checkKey() or secondary_window.checkKey()
            if last_pressed_key is not None:
                if last_pressed_key == "space":
                    pause()
                    lastFrameTime = time.time()
                elif last_pressed_key == "p":
                    window.zoomIn()
                elif last_pressed_key == "o":
                    window.zoomOut()
                elif last_pressed_key == "d":
                    print(road_map.getRoadsWithinView())

            last_clicked_pt = window.checkMouse()
            if last_clicked_pt is not None:
                for car_shape in car_shapes:
                    if car_shape.clicked(last_clicked_pt):
                        car_shapes[info.selected_car.index].shape.setFill("white")
                        info.setSelectedCar(cars[car_shape.index])
                        car_shapes[info.selected_car.index].shape.setFill("yellow")
                        continue

                for intersection in road_map.intersections.values():
                    if intersection.clicked(last_clicked_pt):
                        road_map.showInfo(intersection)
                        continue

            last_clicked_pt = secondary_window.checkMouse()
            if last_clicked_pt is not None:
                for button in info.buttons:
                    button.clicked(last_clicked_pt)
                    continue

        except GraphicsError:
            pass

        # update simulation logic
        while lag > TIME_PER_TICK:
            collision_system.processCollisions(cars)
            for car in cars:
                car.moveTowardsDest(TIME_PER_TICK)
                car_shape = car_shapes[car.index]
                car_shape.x = cars[car.index].x
                car_shape.y = cars[car.index].y
            collision_system.updateCells(cars)

            nextLogicTick += TIME_PER_TICK
            lag -= TIME_PER_TICK

        # render updates to window
        road_map.drawRoadNames()
        road_map.drawRoute(info.selected_car.route, info.show_route)
        for car_shape in car_shapes:
            car_shape.render()
        info.updateTable()

        if info.follow_car:
            pxy = Point(info.selected_car.x, info.selected_car.y)
            window.centerScreenOnPoint(pxy)

    window.close


def pause():
    """pause until user hits space again"""
    cx, cy = window.getCenterScreenPoint()
    message = Text(Point(cx, cy), 'Paused')
    message.setSize(24)
    message.draw(window)
    while window.checkKey() != "space" and secondary_window.checkKey() != "space":
        pass
    message.undraw()


def cleanup():
    """free resources and close window"""
    window.close()
    sys.exit()


if __name__ == '__main__':
    window = GraphWin('Traffic Simulation', 1024, 768, autoflush=False)
    main_menu = MainMenu(window, main)
    menu_options = {"Menu": main_menu.run, "Restart": main, "Exit": cleanup}
    window.addMenu(menu_options)

    secondary_window = GraphWin('Info Window', 512, 512, autoflush=False, scrollable=False)

    main()

# TODO
# Identify proper set of road tags that includes all main roads without too much noise
# Add road names to map in an elegant manner
# Add a follow car method so that a selected car stays in center of screen at all times
# AI so cars can change lanes without crashing and adjust route based on existing traffic conditions
    # fix movement of cars on two way roads
    # add roads that can support more than 1 lane in each direction
    # add ability for cars to change lanes
# create gui menu so that settings can be changed in the simulation (# of cars, lane closures, etc)
# optimize until # of cars that can be drawn on the screen at once is: 50 | 100 | 200 | 500 | 1000
    # create a way to limit # of collision checks that each car needs to do
# dynamically load additional map data when zooming out or moving camera
