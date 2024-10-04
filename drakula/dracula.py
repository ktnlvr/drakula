from .state import GameState, AirportStatus


class DraculaBrain:
    def __init__(self):
        self.visited = set()

    def list_moves(self, state: GameState, location: int) -> list[tuple[float, int]]:
        weighted = []
        neighbours = state.graph[location]
        for neighbour in neighbours:
            w = 1
            if state.states[neighbour].status == AirportStatus.DESTROYED:
                w = 0.4
            if state.states[neighbour].status == AirportStatus.TRAPPED:
                w = 1.2
            weighted.append(w)
        weight_total = sum(weighted)
        weighted = [w / weight_total for w in weighted]

        return list(zip(weighted, state.graph[location]))
