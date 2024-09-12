from .state import GameState


class DraculaBrain:
    def __init__(self):
        self.visited = set()

    def list_moves(self, state: GameState, location: int) -> list[tuple[float, int]]:
        c = location
        neighbours = state.graph[location]
        return [
            (1.0 / len(neighbours), i)
            for i in neighbours
            if (max(c, i), min(c, i)) not in self.visited
        ]
