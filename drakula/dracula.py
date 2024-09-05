from .state import GameState

class DraculaBrain:
    def __init__(self):
        self.visited = set()

    def list_moves(self, state: GameState, current_position: int) -> tuple[float, int]:
        c = current_position
        neighbours = state.graph[current_position]
        return [(1. / len(neighbours), i) for i in neighbours if (max(c, i), min(c, i)) not in self.visited]    
