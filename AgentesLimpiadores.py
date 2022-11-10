from typing import Optional
from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation


class DirtyCells(Agent):
    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
        self.current_state: Optional[str] = None
        self.next_state: Optional[str] = None

    def step(self):
        elementos_celda: int = len(
            self.model.grid.get_cell_list_contents(self.pos))
        if self.current_state == 'd' and elementos_celda > 1:
            self.next_state = 'c'  # c = clean
            self.model.clean_cells += 1
        else:
            self.next_state = self.current_state

    def advance(self):
        self.current_state = self.next_state


class CleanerAgent(Agent):
    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
        self.moves: int = 0
        self.current_state: str = 'l'  # l = limpiador
        self.next_state: Optional[str] = None

    def step(self):
        self.next_state = self.pos

        if self.pos in self.model.dirty_coords:
            self.model.dirty_coords.remove(self.pos)
        else:
            possible_pos = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
            new_position = self.random.choice(possible_pos)
            elementos_celda = self.model.grid.get_cell_list_contents(
                new_position)
            # Sólo se mueve si la posición está dentro de los límites,
            # y si no hay ya un agente limpiador en esa celda
            if (len(elementos_celda) <= 1 and
                    (new_position not in
                     self.model.cleaners_next_pos.values()) and
                    self.model.grid.out_of_bounds(new_position) is False):
                self.next_state = new_position
                self.model.cleaners_next_pos[self.unique_id] = self.next_state
                self.moves += 1
            else:
                self.next_state = self.pos
                self.model.cleaners_next_pos[self.unique_id] = self.next_state

    def advance(self):
        self.model.grid.move_agent(self, self.next_state)


class CleanerModel(Model):
    def __init__(self,
                 width: int,
                 height: int,
                 agents: int,
                 porcentaje: int,
                 step_limit: int) -> None:
        self.agents = agents
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.dirty_cells: int = int(width * height * (porcentaje / 100))
        self.time: int = step_limit
        self.max_time = step_limit
        self.dirty_coords: set = set()
        self.clean_cells: int = 0
        self.cleaners_next_pos: dict[int, tuple] = {}

        def assign_coords(w: int, h: int) -> tuple[int, int]:
            x = self.random.randrange(w)
            y = self.random.randrange(h)
            return x, y

        id = 0
        for _ in range(self.dirty_cells):
            x, y = assign_coords(width, height)
            while (x, y) in self.dirty_coords:
                x, y = assign_coords(width, height)
            self.dirty_coords.add((x, y))

            a = DirtyCells(id, self)
            a.current_state = 'd'  # d = dirty
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))
            id += 1

        for _ in range(self.agents):
            a = CleanerAgent(id, self)
            a.current_state = 'l'
            self.schedule.add(a)
            self.grid.place_agent(a, (width // 2, height // 2))
            id += 1

    def step(self):
        def print_stats() -> None:
            total_time = self.max_time - self.time
            perc = self.clean_cells * 100 / self.dirty_cells
            print(f'Grid de {self.grid.width} * {self.grid.height}')
            print(f'Límite de pasos: {self.max_time}')
            print(f'# de limpiadores: {self.agents}')
            print(f'# de celdas sucias iniciales: {self.dirty_cells}')
            print(f'# de steps realizados: {total_time}')
            print(f'# de celdas limpiadas: {self.clean_cells}')
            print(f'% de celdas limpiadas: {perc}')

        # Para la simulación cuando se hayan limpiado las celdas,
        # o se haya alcanzado el tiempo máximo
        if (len(self.dirty_coords) < 1 or self.time <= 0):
            self.running = False
            print_stats()
            return

        else:
            self.time = self.time - 1
            self.schedule.step()
