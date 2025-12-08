# scene_graph_test.py
# Pequeno teste estrutural do grafo de cena (sem OpenGL)

class Node:
    def __init__(self, name, geom=None, transform=None, updater=None, state=None):
        self.name = name
        self.geom = geom          # pode ser string ou função
        self.transform = transform
        self.updater = updater
        self.state = state or {}
        self.children = []

    def add(self, *children):
        self.children.extend(children)

    def __repr__(self):
        return f"Node({self.name})"


# ===== HELPER FUNCTIONS DE TRANSFORMAÇÃO (PLACEHOLDERS) =====

def tf_translate(x, y, z):
    return ("translate", (x, y, z))

def tf_translate_dynamic(px, py, pz):
    # aqui só guardamos os nomes dos parâmetros
    return ("translate_dynamic", (px, py, pz))

def tf_rotate_dynamic(param_name, x, y, z):
    # rotação dependente de um parâmetro de estado
    return ("rotate_dynamic", param_name, (x, y, z))


# ===== “GEOMETRIAS” E UPDATERS COMO PLACEHOLDERS =====

# Em vez de funções de desenho reais, usamos apenas strings
geom_floor            = "geom_floor"
geom_garage_walls     = "geom_garage_walls"
geom_garage_door      = "geom_garage_door"
geom_car_body         = "geom_car_body"
geom_door             = "geom_door"
geom_wheel            = "geom_wheel"
geom_steering_wheel   = "geom_steering_wheel"
geom_tree             = "geom_tree"

# Updaters vazios, só para existir a referência
def updater_garage_door_animation(node, dt):
    pass

def updater_vehicle_movement(node, dt):
    pass

def updater_door_animation(node, dt):
    pass


# ===== FUNÇÃO QUE CONSTROI O GRAFO DE CENA =====

def build_scene():
    """Constrói o grafo de cena completo"""

    # Nó raiz (mundo)
    world = Node("World")

    # ===== CHÃO =====
    floor = Node(
        "Floor",
        geom=geom_floor,
        transform=tf_translate(0, -0.05, 0)
    )

    # ===== GARAGEM =====
    garage = Node("Garage", transform=tf_translate(0, 0, -12))

    # Estrutura da garagem
    garage_walls = Node("GarageWalls", geom=geom_garage_walls)

    # Porta da garagem
    garage_door = Node(
        "GarageDoor",
        geom=geom_garage_door,
        transform=tf_rotate_dynamic('garage_door_open', 1, 0, 0),
        updater=updater_garage_door_animation,
        state={'garage_door_open': 0.0, 'garage_door_target': 0.0}
    )

    garage.add(garage_walls, garage_door)

    # ===== VEÍCULO =====
    vehicle = Node(
        "Vehicle",
        transform=tf_translate_dynamic('x', 'y', 'z'),
        updater=updater_vehicle_movement,
        state={
            'x': 0.0, 'y': 0.0, 'z': 0.0,
            'angle': 0.0, 'speed': 0.0,
            'wheel_rotation': 0.0,
            'steering_angle': 0.0
        }
    )

    # Transformação global do veículo (rotação)
    vehicle_rotation = Node(
        "VehicleRotation",
        transform=tf_rotate_dynamic('angle', 0, 1, 0)
    )

    # Carroçaria
    car_body = Node("CarBody", geom=geom_car_body)

    # Portas
    left_door = Node(
        "LeftDoor",
        geom=geom_door,
        transform=tf_rotate_dynamic('door_open', 0, 1, 0),
        updater=updater_door_animation,
        state={'door_open': 0.0, 'door_target': 0.0}
    )

    right_door = Node(
        "RightDoor",
        geom=geom_door,
        transform=tf_rotate_dynamic('door_open', 0, 1, 0),
        updater=updater_door_animation,
        state={'door_open': 0.0, 'door_target': 0.0}
    )

    # Rodas (com diferentes estados)
    front_left_wheel = Node(
        "FrontLeftWheel",
        geom=geom_wheel,
        transform=tf_rotate_dynamic('wheel_rotation', 1, 0, 0),
        state={'radius': 0.22, 'width': 0.18}
    )

    front_right_wheel = Node(
        "FrontRightWheel",
        geom=geom_wheel,
        transform=tf_rotate_dynamic('wheel_rotation', 1, 0, 0),
        state={'radius': 0.22, 'width': 0.18}
    )

    rear_left_wheel = Node(
        "RearLeftWheel",
        geom=geom_wheel,
        transform=tf_rotate_dynamic('wheel_rotation', 1, 0, 0),
        state={'radius': 0.28, 'width': 0.22}
    )

    rear_right_wheel = Node(
        "RearRightWheel",
        geom=geom_wheel,
        transform=tf_rotate_dynamic('wheel_rotation', 1, 0, 0),
        state={'radius': 0.28, 'width': 0.22}
    )

    # Volante
    steering_wheel = Node(
        "SteeringWheel",
        geom=geom_steering_wheel,
        transform=tf_rotate_dynamic('steering_angle', 0, 0, 1)
    )

    # Montar hierarquia do veículo
    vehicle_rotation.add(
        car_body,
        left_door,
        right_door,
        front_left_wheel,
        front_right_wheel,
        rear_left_wheel,
        rear_right_wheel,
        steering_wheel
    )

    vehicle.add(vehicle_rotation)

    # ===== ÁRVORES =====
    tree1 = Node(
        "Tree1",
        geom=geom_tree,
        transform=tf_translate(4, 0.5, -7)
    )

    tree2 = Node(
        "Tree2",
        geom=geom_tree,
        transform=tf_translate(-4, 0.5, -7)
    )

    # ===== MONTAR CENA COMPLETA =====
    world.add(
        floor,
        garage,
        vehicle,
        tree1,
        tree2
    )

    return world


# ===== FUNÇÃO PARA IMPRIMIR O GRAFO =====

def print_graph(node, indent=0):
    pad = "  " * indent
    print(f"{pad}- {node.name}")
    if node.geom is not None:
        print(f"{pad}    geom: {node.geom}")
    if node.transform is not None:
        print(f"{pad}    transform: {node.transform}")
    if node.state:
        print(f"{pad}    state: {node.state}")
    for child in node.children:
        print_graph(child, indent + 1)


if __name__ == "__main__":
    world = build_scene()
    print_graph(world)