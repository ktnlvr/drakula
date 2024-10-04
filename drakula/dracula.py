from .state import GameState, AirportStatus


class DraculaBrain:
    """
    A class having the logic behind the movement of the dracula

    Attributes:
    ----------
    visited: set
    An object of class set containing the moves the dracula has made so far.
    """
    def __init__(self):
        self.visited = set()

    def list_moves(self, state: GameState, location: int) -> list[tuple[float, int]]:
        """
        :param state: Takes the current state of the game
        :param location: The current index of the position of dracula in airport's list
        :return: A list of tuples in which elements consist of weight(float)
        and the index of the neighbouring airport
        """
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
