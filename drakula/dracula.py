from .state import GameState

def list_moves(state: GameState, current_position: int, hours: int) -> tuple[float, int]:
    neighbours = state.graph[current_position]
    return [(1. / len(neighbours), i) for i in neighbours]
