from AgentesLimpiadores import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "gray",
                 "r": .1}

    if agent.current_state == 'd':
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
        portrayal["r"] = .2
    elif agent.current_state == 'c':
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 0
        portrayal["r"] = .1
    elif agent.current_state == 'l':
        portrayal["Color"] = "#9E97FA"
        portrayal["Layer"] = 1
        portrayal["r"] = .6
        portrayal["text"] = f"{agent.unique_id}: {agent.moves}"
        portrayal["text_color"] = "black"
    return portrayal


w, h = 10, 10
size = 400
grid = CanvasGrid(agent_portrayal, w, h, size, size)
server = ModularServer(CleanerModel,
                       [grid],
                       "Agentes Limpiadores",
                       {"width": w,
                        "height": h,
                        "agents": 25,
                        "porcentaje": 50,
                        "step_limit": 100})
server.port = 8521
server.launch()
