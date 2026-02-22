import sys
import os

if getattr(sys, 'frozen', False):
    # PyInstaller bundle içinde çalışıyor
    base_path = sys._MEIPASS
else:
    # Normal Python
    base_path = os.path.dirname(os.path.abspath(__file__))

# Kaynak dosyalarının doğru yüklenmesi için CWD'yi ayarla
os.chdir(base_path)
sys.path.insert(0, os.path.join(base_path, 'src'))

import pygame as pg
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from menu import Menu, PauseMenu


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.render_surface = pg.Surface(RES)
        self.center_window()

        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.paused = False
        self.pause_menu = PauseMenu(self)
        self.fullscreen = False
        self.monitor_size = RES

        self.show_menu()

    def center_window(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'
        pg.display.set_caption('MEFENSTEIN - Cehennemden Kaçış')

    def show_menu(self):
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

        menu = Menu(self)
        action = menu.run()

        if action == "new_game":
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)
            self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self, 'shotgun')
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
            self.monitor_size = self.screen.get_size()
        else:
            self.monitor_size = RES
            self.screen = pg.display.set_mode(RES)
            self.center_window()

    def update(self):
        if not self.paused:
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()

        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'MEFENSTEIN - FPS: {self.clock.get_fps():.1f}')

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.render_surface.fill((0, 0, 0))

        self.object_renderer.screen = self.render_surface
        self.object_renderer.draw()
        self.render_surface.blit(self.weapon.images[0], self.weapon.weapon_pos)

        # render_surface'i ekrana scale et
        sw, sh = self.monitor_size
        if (sw, sh) != RES:
            scaled = pg.transform.smoothscale(self.render_surface, (sw, sh))
            self.screen.blit(scaled, (0, 0))
        else:
            self.screen.blit(self.render_surface, (0, 0))

        if self.paused:
            self.pause_menu.draw()

        pg.display.flip()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            pg.mouse.set_visible(True)
            pg.event.set_grab(False)
        else:
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.toggle_pause()

                elif event.key == pg.K_q and self.paused:
                    self.paused = False
                    self.show_menu()

                elif event.key == pg.K_F11:
                    self.toggle_fullscreen()

            elif event.type == self.global_event:
                self.global_trigger = True

            if not self.paused:
                self.player.single_fire_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    game = Game()
    game.run()