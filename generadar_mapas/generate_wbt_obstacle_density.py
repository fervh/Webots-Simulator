"""
Autor: Fernando Vela Hidalgo (https://github.com/fervh)
Asignatura: Simuladores de Robots
Universidad: Universidad Carlos III de Madrid (UC3M)
Fecha: Febrero 2024

Generador de laberintos para Webots.
"""

import argparse
import random
import csv
from numpy import genfromtxt

# VARIABLES
altura_caja_píxel = 0.5
resolution = 4  # Just to make similar to MATLAB [pixel/meter]
metro_por_píxel = 1 / resolution  # [meter/pixel]

# Función para generar un laberinto con las dimensiones basadas en el nombre y apellido dados.
def generate_maze(name, surname, obstacle_density, multiplication):
    rows = len(name) * multiplication - 2
    cols = len(surname) * multiplication - 2
    maze = []
    maze.append([1] * (cols + 2))
    for _ in range(rows):
        row = [1]
        for _ in range(cols):
            if random.random() < obstacle_density:
                row.append(1)  # Obstacle
            else:
                row.append(0)  # Empty space
        row.append(1)
        maze.append(row)
    maze.append([1] * (cols + 2))
    return maze

# Función para guardar el laberinto en un archivo CSV.
def save_maze_to_csv(maze, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in maze:
            writer.writerow(row)

def generar_mapa_webots(archivo_entrada):
    # This function is made by: Author: Juan G Victores
    # CopyPolicy: released under the terms of the LGPLv2.1
    # URL: <https://github.com/roboticslab-uc3m/webots-tools>

    # Cargar datos del archivo CSV
    datos_entrada = genfromtxt(archivo_entrada, delimiter=',')
    print(datos_entrada)

    # Obtener dimensiones del mapa
    num_filas = datos_entrada.shape[0]
    num_columnas = datos_entrada.shape[1]
    print("líneas (NOMBRE)= X =", datos_entrada.shape[0])
    print("columnas (APELLIDO)= Y =", datos_entrada.shape[1])

    altura_caja = altura_caja_píxel

    longitud_unidad_x = metro_por_píxel
    longitud_unidad_y = metro_por_píxel

    # Cadena de texto con las definiciones de los elementos del mundo
    cadena_mundo = '#VRML_SIM R2022b utf8\n\
    EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/backgrounds/protos/TexturedBackground.proto"\n\
    EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"\n\
    EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/floors/protos/Floor.proto"\n\
    EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2023a/projects/objects/solids/protos/SolidBox.proto"\n\
    WorldInfo {\n\
    coordinateSystem "ENU"\n\
    }\n\
    Viewpoint {\n\
    orientation -0.181 0.103 0.978 2.15\n\
    position 14.5 -11.1 7.31\n\
    }\n\
    TexturedBackground {\n\
    }\n\
    TexturedBackgroundLight {\n\
    }\n'

    # Crear el suelo
    longitud_suelo_x = metro_por_píxel * num_filas
    longitud_suelo_y = metro_por_píxel * num_columnas

    cadena_suelo = 'Floor {\n\
    translation $posicion_x $posicion_y 0\n\
    size $longitud_x $longitud_y\n\
    }\n'

    cadena_suelo = cadena_suelo.replace('$posicion_x', str(longitud_suelo_x / 2.0))
    cadena_suelo = cadena_suelo.replace('$posicion_y', str(longitud_suelo_y / 2.0))
    cadena_suelo = cadena_suelo.replace('$longitud_x', str(longitud_suelo_x))
    cadena_suelo = cadena_suelo.replace('$longitud_y', str(longitud_suelo_y))
    cadena_mundo += cadena_suelo

    # Crear las paredes
    cadena_caja = 'SolidBox {\n\
    name "$nombre"\n\
    translation $x $y $z\n\
    size $longitud_unidad_x $longitud_unidad_y $altura_caja\n\
    }\n'

    for i_x in range(num_filas):
        for i_y in range(num_columnas):

            # Saltar si el valor es 0
            if datos_entrada[i_x][i_y] == 0:
                continue

            # Calcular la posición de la caja
            x = longitud_unidad_x / 2.0 + i_x * metro_por_píxel
            y = longitud_unidad_y / 2.0 + i_y * metro_por_píxel
            z = altura_caja / 2.0

            # Crear la caja
            nombre_caja = 'caja_' + str(i_x) + '_' + str(i_y)
            cadena_tmp_caja = cadena_caja.replace('$nombre', nombre_caja)
            cadena_tmp_caja = cadena_tmp_caja.replace('$x', str(x))
            cadena_tmp_caja = cadena_tmp_caja.replace('$y', str(y))
            cadena_tmp_caja = cadena_tmp_caja.replace('$z', str(z))
            cadena_tmp_caja = cadena_tmp_caja.replace('$longitud_unidad_x', str(longitud_unidad_x))
            cadena_tmp_caja = cadena_tmp_caja.replace('$longitud_unidad_y', str(longitud_unidad_y))
            cadena_tmp_caja = cadena_tmp_caja.replace('$altura_caja', str(altura_caja))
            cadena_mundo += cadena_tmp_caja

    # Escribir el archivo de salida
    name = archivo_entrada.split('.')[0]
    archivo_salida = open(name + '.wbt', 'w')
    archivo_salida.write(cadena_mundo)
    archivo_salida.close()

# Función principal del programa.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=str, required=True, help="Nombre del archivo CSV del laberinto")
    parser.add_argument("--name", type=str, required=True, help="Tu nombre para determinar las dimensiones del laberinto")
    parser.add_argument("--surname", type=str, required=True, help="Tu apellido para determinar las dimensiones del laberinto")
    parser.add_argument("--obstacle-density", type=float, default=0.2, help="Densidad de obstáculos en el laberinto (valor entre 0 y 1)")
    parser.add_argument("--multiplication", type=int, default=1, help="Factor de multiplicación para el laberinto")
    args = parser.parse_args()
    if not 0 <= args.obstacle_density <= 1:
        print("Error: La densidad de obstáculos debe estar entre 0 y 1.")
        return
    maze = generate_maze(args.name, args.surname, args.obstacle_density, args.multiplication)
    save_maze_to_csv(maze, args.map)

    print(f"Laberinto generado con dimensiones: {len(maze)}x{len(maze[0])}")
    generar_mapa_webots(args.map)

if __name__ == "__main__":
    main()
