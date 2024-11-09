import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from matplotlib.animation import FuncAnimation

class CleaningModel:
    def __init__(self, width, height, num_agents=10, dirty_percentage=0.3, max_steps=100):
        self.width = width
        self.height = height
        self.num_agents = num_agents
        self.dirty_percentage = dirty_percentage
        self.max_steps = max_steps
        self.grid = np.zeros((height, width))
        self.agents = [(1, 1)] * num_agents  # Todos los agentes inician en (1, 1)
        self.current_step = 0
        self.movements = 0
        self.cleaned_cells = 0
        self.prev_positions = [(1, 1)] * num_agents  # Posiciones anteriores de los agentes

        # Inicializa las celdas sucias
        num_dirty_cells = int(self.width * self.height * self.dirty_percentage)
        dirty_cells = np.random.choice(self.width * self.height, num_dirty_cells, replace=False)
        for cell in dirty_cells:
            row = cell // self.width
            col = cell % self.width
            self.grid[row][col] = 1  # 1 significa "sucio"

    def move_agent(self, agent_idx):
        x, y = self.agents[agent_idx]
        possible_moves = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1),
            (x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)
        ]
        possible_moves = [
            (nx, ny) for nx, ny in possible_moves if 0 <= nx < self.height and 0 <= ny < self.width
        ]
        new_x, new_y = possible_moves[np.random.choice(len(possible_moves))]
        self.prev_positions[agent_idx] = self.agents[agent_idx]  # Guarda la posición anterior
        self.agents[agent_idx] = (new_x, new_y)
        self.movements += 1

    def step(self):
        for i in range(self.num_agents):
            x, y = self.agents[i]
            if self.grid[x][y] == 1:  # Si la celda está sucia, la limpia
                self.grid[x][y] = 0
                self.cleaned_cells += 1
            else:
                self.move_agent(i)
        self.current_step += 1

    def is_clean(self):
        return self.cleaned_cells == np.sum(self.grid == 0)

# Inicialización del modelo
model = CleaningModel(10, 10)

# Configuración de la figura
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
grid_display = ax.imshow(model.grid, cmap="Blues", interpolation="nearest")

# Barra de progreso
progress_ax = plt.axes([0.1, 0.1, 0.8, 0.03])
progress_bar = Slider(progress_ax, 'Step', 0, model.max_steps, valinit=0, valstep=1)

# Botones de control
axprev = plt.axes([0.7, 0.025, 0.1, 0.04])
axnext = plt.axes([0.81, 0.025, 0.1, 0.04])
axplay = plt.axes([0.59, 0.025, 0.1, 0.04])
btn_prev = Button(axprev, 'Back')
btn_next = Button(axnext, 'Next')
btn_play = Button(axplay, 'Play')

# Variables de control para la animación
is_playing = False

# Funciones para actualizar la visualización y la información de la simulación
def update_display():
    # Redibuja el grid restableciendo la visualización
    grid_display.set_array(model.grid)
    
    # Restablece las posiciones anteriores de los agentes
    for prev_x, prev_y in model.prev_positions:
        if model.grid[prev_x, prev_y] == 0:  # Si la celda estaba limpia
            ax.plot(prev_y, prev_x, "ws")  # ws: White square para limpiar visualmente
    
    # Dibuja los agentes en sus nuevas posiciones
    for agent in model.agents:
        ax.plot(agent[1], agent[0], "ro")
    
    progress_bar.set_val(model.current_step)
    plt.draw()

def next_step(event=None):
    if model.current_step < model.max_steps and not model.is_clean():
        model.step()
        update_display()

def prev_step(event):
    if model.current_step > 0:
        model.current_step -= 1
        update_display()

def toggle_play(event):
    global is_playing
    is_playing = not is_playing

# Conectar botones
btn_next.on_clicked(next_step)
btn_prev.on_clicked(prev_step)
btn_play.on_clicked(toggle_play)

# Función para animación
def animate(frame):
    if is_playing and model.current_step < model.max_steps and not model.is_clean():
        next_step()
    if model.is_clean() or model.current_step >= model.max_steps:
        is_playing = False
        show_results()

stats_text = ax.text(0.05, -0.1, "", transform=ax.transAxes, fontsize=12, verticalalignment='top')

# Función para actualizar la visualización y mostrar estadísticas en tiempo real
def update_display():
    # Redibuja el grid restableciendo la visualización
    grid_display.set_array(model.grid)

    # Restablece las posiciones anteriores de los agentes
    for prev_x, prev_y in model.prev_positions:
        if model.grid[prev_x, prev_y] == 0:  # Si la celda estaba limpia
            ax.plot(prev_y, prev_x, "ws")  # ws: White square para limpiar visualmente
    
    # Dibuja los agentes en sus nuevas posiciones
    for agent in model.agents:
        ax.plot(agent[1], agent[0], "ro")

    # Actualiza la barra de progreso
    progress_bar.set_val(model.current_step)

    # Actualiza el texto con los resultados
    total_dirty_cells = int(model.width * model.height * model.dirty_percentage)
    clean_percentage = (model.cleaned_cells / total_dirty_cells) * 100
    stats_text.set_text(f"Pasos: {model.current_step}/{model.max_steps}\n"
                        f"Celdas limpias: {model.cleaned_cells}/{total_dirty_cells} ({clean_percentage:.2f}%)\n"
                        f"Movimientos: {model.movements}")
    
    plt.draw()

def show_results():
    # Calcula y muestra las estadísticas de la simulación
    total_dirty_cells = int(model.width * model.height * model.dirty_percentage)
    clean_percentage = (model.cleaned_cells / total_dirty_cells) * 100
    print(f"Tiempo necesario: {model.current_step} pasos")
    print(f"Porcentaje de celdas limpias: {clean_percentage:.2f}%")
    print(f"Número de movimientos realizados: {model.movements}")

ani = FuncAnimation(fig, animate, interval=200)
plt.show()