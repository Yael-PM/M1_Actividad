import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from matplotlib.animation import FuncAnimation
import random
import time

class CleaningModel:
    def __init__(self, width, height, num_agentes=5, porcentaje_sucio=0.3, max_steps=100):
        self.width = width
        self.height = height
        self.num_agentes = num_agentes
        self.porcentaje_sucio = porcentaje_sucio
        self.max_steps = max_steps
        self.grid = np.zeros((height, width))  # Crea la cuadrícula de celdas limpias (0) inicialmente
        self.agentes = [(1, 1)] * num_agentes  # Los agentes comienzan en la posición (1, 1)
        self.step_actual = 0
        self.movimientos = 0
        self.celdas_limpias = 0
        self.pocision_prev = [(1, 1)] * num_agentes  # Posiciones anteriores de los agentes

        # Inicializa las celdas sucias (1)
        num_celdas_sucias = int(self.width * self.height * self.porcentaje_sucio)
        celdas_sucias = np.random.choice(self.width * self.height, num_celdas_sucias, replace=False)
        for celda in celdas_sucias:
            row = celda // self.width
            col = celda % self.width
            self.grid[row][col] = 1  # Marca las celdas sucias

    def mover_agente(self, agent_idx):
        x, y = self.agentes[agent_idx]
        mov_posibles = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1),
            (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)
        ]
        # Filtra los movimientos posibles que estén dentro de los límites de la cuadrícula
        mov_posibles = [
            (nx, ny) for nx, ny in mov_posibles if 0 <= nx < self.height and 0 <= ny < self.width
        ]
        # Elige un nuevo movimiento aleatorio de los posibles
        nuevo_mov_x, nuevo_mov_y = mov_posibles[np.random.choice(len(mov_posibles))]
        self.pocision_prev[agent_idx] = self.agentes[agent_idx]  # Guarda la posición anterior
        self.agentes[agent_idx] = (nuevo_mov_x, nuevo_mov_y)
        self.movimientos += 1

    def step(self):
        for i in range(self.num_agentes):
            x, y = self.agentes[i]
            if self.grid[x][y] == 1:  # Si la celda está sucia, la limpia
                self.grid[x][y] = 0
                self.celdas_limpias += 1
            else:
                self.mover_agente(i)
        self.step_actual += 1

    def is_clean(self):
        # Verifica si no hay celdas sucias
        return np.all(self.grid == 0)

def actualizar_vista(model, grid_display, progress_bar, ax, stats_text):
    grid_display.set_array(model.grid)
    
    for prev_x, prev_y in model.pocision_prev:
        if model.grid[prev_x, prev_y] == 0:
            ax.plot(prev_y, prev_x, "ws")
    
    for agente in model.agentes:
        ax.plot(agente[1], agente[0], "ro")

    progress_bar.set_val(model.step_actual)
    
    total_celdas_sucias = int(model.width * model.height * model.porcentaje_sucio)
    porcentaje_limpio = (model.celdas_limpias / total_celdas_sucias) * 100
    stats_text.set_text(f"Pasos: {model.step_actual}/{model.max_steps} "
                        f"Celdas limpias: {model.celdas_limpias}/{total_celdas_sucias} ({porcentaje_limpio:.2f}%)"
                        f"Movimientos: {model.movimientos}")

    
    stats_text.set_position((-0.60, -0.25))  # Ajusta la posición justo debajo de la barra de progreso
    plt.draw()

def next_step(model, grid_display, progress_bar, ax, stats_text):
    if model.step_actual < model.max_steps and not model.is_clean():
        model.step()
        actualizar_vista(model, grid_display, progress_bar, ax, stats_text)
    elif model.is_clean():
        animar(model, grid_display, progress_bar, ax, stats_text)  # Detiene la animación si ya está limpio

# Definir globalmente el modelo y la animación
model = None
ani = None
is_playing = False  # Variable global para controlar la animación

def prev_step(event=None):
    global model  # Acceder a model globalmente
    if model.step_actual > 0:
        model.step_actual -= 1
        actualizar_vista(model)

def toggle_play(event=None):
    global is_playing
    if model is None:
        print("El modelo no está inicializado.")
        return
    if model.is_clean():
        print("¡La cuadrícula está completamente limpia!")
        ani.event_source.stop()
        is_playing = False
    else:
        is_playing = not is_playing
        if is_playing:
            ani.event_source.start()
        else:
            ani.event_source.stop()

def animar(model, grid_display, progress_bar, ax, stats_text):
    if model.is_clean() or model.step_actual >= model.max_steps:
        resultados(model)
        ani.event_source.stop()  # Detiene la animación si se cumple alguna de las condiciones
    elif is_playing and model.step_actual < model.max_steps:
        next_step(model, grid_display, progress_bar, ax, stats_text)

def resultados(model):
    total_celdas_sucias = int(model.width * model.height * model.porcentaje_sucio)
    porcentaje_limpio = (model.celdas_limpias / total_celdas_sucias) * 100
    print(f"Tiempo necesario: {model.step_actual} pasos")
    print(f"Porcentaje de celdas limpias: {porcentaje_limpio:.2f}%")
    print(f"Número de movimientos realizados: {model.movimientos}")
    if model.celdas_limpias == total_celdas_sucias:
        print("¡La cuadrícula está completamente limpia!")
        plt.close()
    
    time.sleep(2)
    plt.close()

def run_simulation():
    global model  # Asegúrate de usar la variable global `model`
    agentes = random.randint(5, 30)
    model = CleaningModel(10, 10, num_agentes=agentes)
    
    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.25, top=0.75)
    grid_display = ax.imshow(model.grid, cmap="Blues", interpolation="nearest")

    progress_ax = plt.axes([0.1, 0.15, 0.8, 0.03])
    progress_bar = Slider(progress_ax, 'Step', 0, model.max_steps, valinit=0, valstep=1)

    stats_text = ax.text(0.85, 0.05, "", transform=ax.transAxes, fontsize=12, verticalalignment='top', horizontalalignment='left')

    axplay = plt.axes([0.7, 0.025, 0.1, 0.04])
    axnext = plt.axes([0.81, 0.025, 0.1, 0.04])
    btn_next = Button(axnext, 'Next')
    btn_play = Button(axplay, 'Play')

    btn_next.on_clicked(lambda event: next_step(model, grid_display, progress_bar, ax, stats_text))
    btn_play.on_clicked(toggle_play)

    global ani  # Hacemos global la variable `ani`
    ani = FuncAnimation(fig, lambda frame: animar(model, grid_display, progress_bar, ax, stats_text), interval=150)

    plt.show()

    return model.step_actual, model.num_agentes

def main():
    results = []
    for _ in range(15):
        time, agentes = run_simulation()
        results.append((time, agentes))

    # Ahora que tenemos los resultados, generamos la gráfica
    iteraciones = [result[0] for result in results]
    agentes = [result[1] for result in results]

    plt.figure()
    plt.scatter(agentes, iteraciones)
    plt.title('Tiempo vs Número de Agentes')
    plt.xlabel('Número de Agentes')
    plt.ylabel('Tiempo (pasos)')
    plt.show()

# Ejecutar la función principal
main()
