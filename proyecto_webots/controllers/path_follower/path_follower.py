"""
Autor: Fernando Vela Hidalgo (https://github.com/fervh)
Asignatura: Simuladores de Robots
Universidad: Universidad Carlos III de Madrid (UC3M)
Fecha: Febrero 2024

Algoritmo A* para el robot e-puck en Webots. El robot se mueve a la meta con una ruta óptima.

PROS:
- Garantiza la optimización de la ruta.
- Garantiza que el robot alcance la meta.

CONS:
- Requiere un mapa del entorno.

"""
import csv
import heapq
import math
from controller import Robot, Motor, DistanceSensor, GPS, InertialUnit, Compass

# Función para cargar el laberinto desde el archivo CSV
def load_map(file_path):
    maze = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            maze.append([int(cell) for cell in row])
    return maze

# Definición de acciones posibles (moverse hacia arriba, abajo, izquierda, derecha)
actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# Función para obtener vecinos válidos de una celda
def get_neighbors(maze, cell):
    neighbors = []
    rows = len(maze)
    cols = len(maze[0])
    for action in actions:
        neighbor_row = cell[0] + action[0]
        neighbor_col = cell[1] + action[1]
        if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols and maze[neighbor_row][neighbor_col] == 0:
            neighbors.append((neighbor_row, neighbor_col))
    return neighbors

# Función de heurística (distancia Manhattan)
def heuristic(cell, goal):
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

# Función para encontrar la ruta óptima usando A*
def astar(maze, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while frontier:
        current_cost, current_cell = heapq.heappop(frontier)
        
        if current_cell == goal:
            break
        
        for next_cell in get_neighbors(maze, current_cell):
            new_cost = cost_so_far[current_cell] + 1
            if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                cost_so_far[next_cell] = new_cost
                priority = new_cost + heuristic(next_cell, goal)
                heapq.heappush(frontier, (priority, next_cell))
                came_from[next_cell] = current_cell
    
    # Reconstruir el camino
    path = []
    current_cell = goal
    while current_cell != start:
        path.append(current_cell)
        current_cell = came_from[current_cell]
    path.append(start)
    path.reverse()
    
    return path

# Función para mostrar el laberinto con el camino
def print_maze_with_path(maze, path):
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            if (i, j) in path:
                print('X', end=' ')
            elif cell == 1:
                print('#', end=' ')
            elif (i, j) == path[0]:
                print('S', end=' ')
            elif (i, j) == path[-1]:
                print('M', end=' ')
            else:
                print(' ', end=' ')
        print()
        
def print_maze_with_path_completed(maze, path,path_completed):
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            if (i, j) in path:
                print('X', end=' ')
            elif (i, j) in path_completed:
                print('O', end=' ')
            elif cell == 1:
                print('#', end=' ')
            else:
                print(' ', end=' ')
        print()

def get_world_angle(compass_values):
    rad = math.atan2(compass_values[0], compass_values[1])
    bearing = (rad  + 1.5708) / math.pi * 180.0 - 90.0
    if bearing < 0.0:
        bearing += 360.0
    angle = bearing 
    return bearing

def get_all_values():
    gps_values = gps.getValues()
    compass_values = compass.getValues()
    angle = get_world_angle(compass_values)

def rotate_left(speed):
    
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_speed = -speed
    right_speed = speed
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

def rotate_right(speed):
    
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_speed = speed
    right_speed = -speed
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

def move_forward(speed):
    
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_speed = speed
    right_speed = speed
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)

def stop():
    
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

if __name__ == "__main__":
    # Cargar el laberinto
    maze = load_map('map.csv')

    # Definir el punto de inicio y el punto de meta
    start = (1, 1)
    goal = (len(maze) - 2, len(maze[0]) - 2)

    # Encontrar la ruta óptima
    path = astar(maze, start, goal)
    path_completed = []

    # Mostrar el laberinto con el camino
    print_maze_with_path(maze, path)

    # Mostrar el camino en orden
    print("Camino óptimo:")
    for i, cell in enumerate(path):
        if i > 0 and i < len(path) - 1:
            print(f"{i+1} -> {cell}")

    # Crear el robot
    robot = Robot()

    # Obtener el timestep del mundo
    timestep = int(robot.getBasicTimeStep())

    # Obtener los motores
    left_motor = robot.getDevice('left wheel motor')
    right_motor = robot.getDevice('right wheel motor')
    gps = robot.getDevice('gps')
    compass = robot.getDevice('compass')

    # Configurar los motores
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

    # Habilitar los dispositivos
    gps.enable(timestep)
    compass.enable(timestep)

    # Bucle principal.
    while robot.step(timestep) != -1:
        # Obtener la posición del robot
        gps_values = gps.getValues()
        compass_values = compass.getValues()
        angle = get_world_angle(compass_values)
        #print(f"Posición: {gps_values}, Ángulo: {angle}")
        actual_cell = (int(gps_values[0]*4), int(gps_values[1]*4))
        actual_cell_float = (gps_values[0]*4, gps_values[1]*4)

        Kp = 0.1
        max_speed = 6.28
        angle_variation = 1

        margin = 0.1


        # Mover el robot a lo largo del camino
        if len(path) > 1:
            print("Siguiente celda: ", path[1], "Celda actual: ", actual_cell)
            print_maze_with_path_completed(maze, path, path_completed)
            if path[1][1]+ 0.5 +margin > actual_cell_float[1] and path[1][1]+0.5 - margin < actual_cell_float[1] and path[1][0]+0.5 + margin > actual_cell_float[0] and path[1][0]+0.5 - margin < actual_cell_float[0]:
                print("pop")
                path_completed.append(path.pop(0))
            else:
                #print("Moviendo hacia la celda, celda x actual: ", actual_cell[0], "celda y actual: ", actual_cell[1], "celda x siguiente: ", path[1][0], "celda y siguiente: ", path[1][1], "ángulo: ", angle)
                if path[1][1] > actual_cell[1]: # Derecha
                    idle_angle = 90
                    if not(angle < idle_angle + angle_variation and angle > idle_angle - angle_variation):
                        
                        if abs(angle - idle_angle) < 20:
                            speed = 1
                        else:
                            speed = max_speed
                            
                        if angle - idle_angle < 0:
                            rotate_left(speed)
                        else:
                            rotate_right(speed)
                    else:
                        speed = max_speed
                        move_forward(speed)

                
                elif path[1][1] < actual_cell[1]: # Izquierda
                    idle_angle = 270
                    if not(angle < idle_angle + angle_variation and angle > idle_angle - angle_variation):
                        
                        if abs(angle - idle_angle) < 20:
                            speed = 1
                        else:
                            speed = max_speed
                            
                        if angle - idle_angle < 0:
                            rotate_left(speed)
                        else:
                            rotate_right(speed)
                    else:
                        speed = max_speed
                        move_forward(speed)
                
                elif path[1][0] < actual_cell[0]: # Arriba
                    idle_angle = 180
                    if not(angle < idle_angle + angle_variation and angle > idle_angle - angle_variation):
                        
                        if abs(angle - idle_angle) < 20:
                            speed = 1
                        else:
                            speed = max_speed
                            
                        if angle - idle_angle < 0:
                            rotate_left(speed)
                        else:
                            rotate_right(speed)
                    else:
                        speed = max_speed
                        move_forward(speed)

                
                elif path[1][0] > actual_cell[0]: # Abajo
                    idle_angle = 0
                    if not(angle < idle_angle + angle_variation and angle > idle_angle - angle_variation):
                        
                        if abs(angle - idle_angle) < 20:
                            speed = 1
                        else:
                            speed = max_speed
                            
                        if angle - idle_angle < 0:
                            rotate_left(speed)
                        else:
                            rotate_right(speed)
                    else:
                        speed = max_speed
                        move_forward(speed)
        else:
            print("Llegamos a la meta")
            stop()
            
            break

