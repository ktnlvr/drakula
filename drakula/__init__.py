# import components
from types import NoneType

from .maths import angles_to_world_pos
from .db import Database, GameDatabaseFacade
from .game import MapScene
from .models import Airport
from .renderer import Renderer
from .state import GameState

import pygame

class Character:

    def __init__(self,initial_airport:Airport):
        self.current_airport = initial_airport
        self.input_text = ''
        self.font = pygame.font.Font(None, 22)
        self.input_rect = pygame.Rect(10, 0, 300, 40)
        self.input_rect.bottomleft = (5, pygame.display.get_surface().get_height() - 5)
        self.input_active = False
        self.cntd_airports = []
        print(f"Character initial airport: {initial_airport.ident}")

    def handle_input(self, event, airports):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = not self.input_active
            else:
                self.input_active = False

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_icao(airports)
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode.upper()

    def aftermove_airport(self, new_airport:Airport):
        self.current_airport = new_airport
        print(f"Character moved to airport: {new_airport.ident}")

    def input_icao(self, airports):
        icao_code = self.input_text.strip()
        new_airport = airport_icao(airports,icao_code)
        if new_airport:
            self.aftermove_airport(new_airport)
        self.input_text =""

    def get_cntd_airports(self ,cntd_airports):
        self.cntd_airports = cntd_airports

    #display character position and information
    def render(self, renderer: Renderer, airports):
        world_pos = angles_to_world_pos(*self.current_airport.position)
        renderer.draw_circle((0, 255, 0), world_pos, 0.004)

        #input box
        if self.input_active:
            bg_color = pygame.Color(230,200,200)
        else:
            bg_color = pygame.Color(200,200,200)

        pygame.draw.rect(renderer.surface,bg_color,self.input_rect)
        input_text = self.font.render(f'Enter ICAO: {self.input_text}', True, (0,0,0))
        renderer.surface.blit(input_text,(self.input_rect. x + 5, self.input_rect.y + 5))

        #information
        cntd_airports = ','.join(airport.ident for airport in self.cntd_airports)
        info_str = f' Airport: {self.current_airport.name}  |  ICAO: {self.current_airport.ident}  |  Position:{self.current_airport.position}  | Connected Airports:{cntd_airports}'
        info_text = self.font.render(info_str,True,(255,255,255))

        padding = 5
        bg_rect = pygame.Rect(0,0,renderer.surface.get_width(), info_text.get_height() + padding * 2)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0,0,0,76))#30% opacity
        renderer.surface.blit(bg_surface, bg_rect)
        renderer.surface.blit(info_text,(padding, padding))

def airport_icao(airports, icao_code):
    return next((airport for airport in airports if airport.ident == icao_code), None)
