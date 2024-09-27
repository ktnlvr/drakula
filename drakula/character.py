from enum import Enum

import pygame

from .state import GameState, AirportStatus


class CharacterInputResult(Enum):
    Ignored = 0
    Moved = 1
    Accepted = 2


class Character:
    def __init__(self, location: int):
        self.current_location = location
        self.input_text = ""

    def handle_input(
            self, event: pygame.event.Event, game_state: GameState, scene
    ) -> CharacterInputResult:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.input_text = self.input_text.strip()

                idx = game_state.get_index(self.input_text)
                self.input_text = ""
                if (
                        idx not in game_state.graph
                        or idx not in game_state.graph[self.current_location]
                ):
                    return CharacterInputResult.Accepted
                if (scene.state.states[idx].status != AirportStatus.AVAILABLE):
                    return CharacterInputResult.Accepted
                self.current_location = idx
                return CharacterInputResult.Moved
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return CharacterInputResult.Accepted
            elif event.key == pygame.K_KP_ENTER:
                game_state.trap_location(self.current_location)
            else:
                if not event.unicode.isspace():
                    self.input_text += event.unicode.upper()
                    return CharacterInputResult.Accepted
        return CharacterInputResult.Ignored
