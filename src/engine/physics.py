from typing import TypedDict


class Rect(TypedDict):
    x: float
    y: float
    w: float
    h: float


class Collider(TypedDict):
    """Tile de colisão com tipo.

    one_way=True → plataforma passável por baixo e pelos lados.
    Só colide quando a entidade está *descendo* (vy > 0) e vem de cima.
    """
    x: float
    y: float
    w: float
    h: float
    one_way: bool


def check_collision(rect1: Rect, rect2: Rect) -> bool:
    return (
        rect1["x"] < rect2["x"] + rect2["w"]
        and rect1["x"] + rect1["w"] > rect2["x"]
        and rect1["y"] < rect2["y"] + rect2["h"]
        and rect1["y"] + rect1["h"] > rect2["y"]
    )
