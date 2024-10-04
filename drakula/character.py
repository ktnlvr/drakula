from enum import Enum
from string import ascii_letters, digits

import pygame

from .state import GameState, AirportStatus
from .logging import logger


class CharacterInputResult(Enum):
    Ignored = 0
    Moved = 1
    Accepted = 2

    def __bool__(self):
        return self != CharacterInputResult.Ignored


class Character:
    def __init__(self, location: int):
        self.current_location = location
        self.trap_count = 4
        self.input_text = ""

    def handle_input(
        self, event: pygame.event.Event, game_state: GameState, scene
    ) -> CharacterInputResult:
        if event.type != pygame.KEYDOWN or event.unicode == "":
            return CharacterInputResult.Ignored

        if event.key == pygame.K_RETURN:
            self.input_text = self.input_text.strip()

            idx = game_state.get_index(self.input_text)
            self.input_text = ""
            if (
                idx not in game_state.graph
                or idx not in game_state.graph[self.current_location]
            ):
                return CharacterInputResult.Accepted
            if (
                scene.state.states[idx].status != AirportStatus.AVAILABLE
                and idx != game_state.dracula_location
            ):
                return CharacterInputResult.Accepted
            self.current_location = idx
            return CharacterInputResult.Moved
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            return CharacterInputResult.Accepted
        elif event.key == pygame.K_KP_ENTER:
            if self.trap_count == 0:
                logger.info(f"Trapping rejected {self.current_location}, 0 traps left")
            elif (
                game_state.states[self.current_location].status != AirportStatus.TRAPPED
            ):
                self.trap_count -= 1
                game_state.trap_location(self.current_location)
                logger.info(
                    f"Trapped {self.current_location} successful, {self.trap_count} traps left"
                )
            else:
                logger.info(f"May not trap {self.current_location}, already trapped")
        else:
            char = event.unicode
            if char in digits + ascii_letters + "-":
                self.input_text += event.unicode.upper()
                return CharacterInputResult.Accepted
        return CharacterInputResult.Ignored
