"""
Autor: Fernando Vela Hidalgo (https://github.com/fervh)
Asignatura: Simuladores de Robots
Universidad: Universidad Carlos III de Madrid (UC3M)
Fecha: Febrero 2024

Algoritmo Bug2 para el robot e-puck en Webots. La idea es que el robot se mueva hacia una meta evitando obstáculos.

PROS:
- Es un algoritmo simple y eficiente para la navegación de robots móviles.
- No requiere un mapa del entorno.

CONS:
- No garantiza la optimización de la ruta.
- No garantiza que el robot alcance la meta.

"""
from controller import Robot, Motor, DistanceSensor

import math

# Geometría de coordenadas
def obtener_recta(A, B):
    m = (B[1] - B[0]) / (A[1] - A[0])  # Calcula la pendiente de la recta
    c = B[0] - m*A[0]  # Calcula la constante de la recta
    return m, c

def distancia_entre(A, B):
    return math.sqrt((A[0] - B[0])**2 + (A[1] - B[1])**2)  # Calcula la distancia euclidiana entre dos puntos

def angulo_de(A, B):
    return math.degrees(math.atan2((B[1]-A[1]), (B[0]-A[0])) % 360) + 90  # Calcula el ángulo entre dos puntos

def distancia_desde_recta(x, A, B):
    longitud_AB = distancia_entre(A, B)
    distancia_desde_AB = abs((B[1]-A[1])*(A[0] - x[0]) - (B[0]-A[0])*(A[1]-x[1]))  # Calcula la distancia perpendicular desde un punto a una recta
    distancia_desde_AB /= longitud_AB
    return distancia_desde_AB
    
def distancia_desde_poligono(x, pares):
    distancias = []
    for (A, B) in pares:
        distancias.append(
            distancia_desde_recta(x, A, B)
        )
    return min(distancias)


# Para los algoritmos Bug
def en_recta(x, A, B, tolerancia=0.02):   
    dist = distancia_desde_recta(x, A, B)
    if dist > tolerancia:
        return False
    else:
        return True

def obtener_rumbo_en_grados(norte):
    rad = math.atan2(norte[0], norte[1])
    rumbo = (rad - 1.5708) / 3.14 * 180.0
    rumbo += 180
    if rumbo < 0.0:
        rumbo = rumbo + 360.0

    return rumbo

robot = Robot()

# Constantes    
TIEMPO_PASO = 64
VELOCIDAD_MAX = 6.28
POSICION_META = [11.6, 5.6, 0.0]
EPSILON_POS = 0.07  # distancia de la meta para detenerse
PROX_OBST = 100.0
EPSILON_ANGULO = 0.05

# Inicializar motores
motor_izquierdo = robot.getDevice('left wheel motor')
motor_derecho = robot.getDevice('right wheel motor')
motor_izquierdo.setPosition(float('inf'))  # número de radianes que el motor gira
motor_derecho.setPosition(float('inf'))
motor_izquierdo.setVelocity(0.0)
motor_derecho.setVelocity(0.0)

# Inicializar dispositivos
ps = []
nombres_ps = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]
for i in range(8):
    ps.append(robot.getDevice(nombres_ps[i]))
    ps[i].enable(TIEMPO_PASO)

valores_ps = [0 for i in range(8)]

gps = robot.getDevice('gps')
gps.enable(TIEMPO_PASO)

brujula = robot.getDevice('compass')
brujula.enable(TIEMPO_PASO)

estado = 'inicio'

while robot.step(TIEMPO_PASO) != -1:
    # Leer salidas de los sensores
    for i in range(8):
        valores_ps[i] = ps[i].getValue()    
    posicion_actual = gps.getValues()
    angulo_actual = obtener_rumbo_en_grados(brujula.getValues())
    
    # Inicializar velocidades de los motores al 50% de VELOCIDAD_MAX.
    velocidad_izquierda  = 0.5 * VELOCIDAD_MAX
    velocidad_derecha = 0.5 * VELOCIDAD_MAX
    
    # Al principio
    if estado == 'inicio':
        posicion_inicio = gps.getValues()
        alineado_con_meta = angulo_de(posicion_actual, POSICION_META) > 0.98*angulo_actual
        alineado_con_meta = alineado_con_meta and angulo_de(posicion_actual, POSICION_META) < 1.02*angulo_actual
        
        if not alineado_con_meta:
            print('Estado del robot: alineándose con la meta')
            velocidad_izquierda  = -0.50 * VELOCIDAD_MAX
            velocidad_derecha = 0.50 * VELOCIDAD_MAX
            estado = 'inicio'
        else:
            estado = 'mover_a_meta'

    elif estado == 'mover_a_meta':
        obstaculo_detectado = valores_ps[0] > PROX_OBST and valores_ps[7] > PROX_OBST
        if obstaculo_detectado:
            punto_impacto = gps.getValues()
            angulo_impacto = obtener_rumbo_en_grados(brujula.getValues())
            estado = 'seguir_obstaculo'
        elif distancia_entre(posicion_actual, POSICION_META) <= EPSILON_POS:
            estado = 'fin'
        elif not en_recta(posicion_actual, posicion_inicio, POSICION_META):
            # Retroceder a la línea
            angulo_cabeceo = angulo_actual
            angulo_meta = angulo_de(posicion_inicio, POSICION_META)
            
            if (angulo_cabeceo - angulo_meta) > EPSILON_ANGULO:
                print('Estado del robot: alineándose con la meta')
                velocidad_izquierda  = 0.5 * VELOCIDAD_MAX
                velocidad_derecha = 0.1 * VELOCIDAD_MAX
            elif (angulo_cabeceo - angulo_meta) < -EPSILON_ANGULO:
                print('Estado del robot: alineándose con la meta')
                velocidad_izquierda  = 0.1 * VELOCIDAD_MAX
                velocidad_derecha = 0.5 * VELOCIDAD_MAX
        else:
            print('Estado del robot: moviéndose hacia la meta')
            motor_izquierdo.setVelocity(velocidad_izquierda)
            motor_derecho.setVelocity(velocidad_derecha)
            
    elif estado == 'seguir_obstaculo':
        print('Estado del robot: siguiendo el límite del obstáculo')
        en_recta_nuevamente = en_recta(posicion_actual, posicion_inicio, POSICION_META,
                                tolerancia=EPSILON_POS)
        no_punto_impacto = distancia_entre(posicion_actual, punto_impacto) > 1.5*EPSILON_POS
        if en_recta_nuevamente and no_punto_impacto:
            print('Estado del robot: meta alcanzable')
            estado = 'mover_a_meta'
            velocidad_izquierda  = -0.50 * VELOCIDAD_MAX
            velocidad_derecha = 0.50 * VELOCIDAD_MAX
            posicion_inicio = posicion_actual
            continue
  
        lado_derecho_cubierto = valores_ps[2] > PROX_OBST
        if not lado_derecho_cubierto:
            velocidad_izquierda  = -0.5 * VELOCIDAD_MAX
            velocidad_derecha = 0.5 * VELOCIDAD_MAX
        else:
            valor_derecho = max(valores_ps[0:2])
            valor_izquierdo = max(valores_ps[5:7])
            if valor_derecho > 2.0*PROX_OBST:
                velocidad_izquierda  = 0.20 * VELOCIDAD_MAX
                velocidad_derecha = 0.50 * VELOCIDAD_MAX
            elif valor_derecho < PROX_OBST and valor_izquierdo < PROX_OBST:
                velocidad_izquierda  = 0.50 * VELOCIDAD_MAX
                velocidad_derecha = 0.20 * VELOCIDAD_MAX
            else:
                velocidad_izquierda  = 0.50 * VELOCIDAD_MAX
                velocidad_derecha = 0.50 * VELOCIDAD_MAX
                
    elif estado == 'fin':
        print('Estado del robot: meta alcanzada')
        motor_izquierdo.setVelocity(0)
        motor_derecho.setVelocity(0)
        break
        
    motor_izquierdo.setVelocity(velocidad_izquierda)
    motor_derecho.setVelocity(velocidad_derecha)
