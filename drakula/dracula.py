from .state import GameState, AirportStatus


class DraculaBrain:
    def __init__(self):
        self.visited = set()

    def list_moves(self, state: GameState, location: int) -> list[tuple[float, int]]:
        c = location
        neighbours = [idx for idx in state.graph[location] if state.states[idx].status != AirportStatus.DESTROYED]

        return [
            (1.0 / len(neighbours), i)
            for i in neighbours
            if (max(c, i), min(c, i)) not in self.visited
        ]
