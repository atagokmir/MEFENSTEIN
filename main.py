import pygame as pg
import sys
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
        
        # Pencere modunda başlat ve ortala
        self.screen = pg.display.set_mode(RES)
        self.render_surface = pg.Surface(RES)  # Sabit boyutlu render surface
        self.center_window()
        
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.paused = False
        self.pause_menu = PauseMenu(self)
        
        # Tam ekran flag'i
        self.fullscreen = False
        
        # Ana menüyü göster
        self.show_menu()
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'
        pg.display.set_caption('MEFENSTEIN - Cehennemden Kaçış')

    def show_menu(self):
        """Ana menüyü göster"""
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
        self.weapon = Weapon(self, 'shotgun')  # Başlangıç silahı
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def toggle_fullscreen(self):
        """Tam ekran modunu değiştir"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Monitör bilgilerini al ve debug et
            info = pg.display.Info()
            print(f"Monitor boyutu: {info.current_w}x{info.current_h}")
            
            # Tam ekran modu
            self.screen = pg.display.set_mode((info.current_w, info.current_h), pg.FULLSCREEN)
            
            # Debug - ekranı test renkle doldur
            self.screen.fill((255, 0, 0))  # Kırmızı
            pg.display.flip()
            pg.time.wait(500)  # 0.5 saniye bekle
            
        else:
            # Pencere moduna dön
            self.screen = pg.display.set_mode(RES)
            self.center_window()

    def update(self):
        if not self.paused:
            self.player.update()
            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()
        
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'MEFENSTEIN - FPS: {self.clock.get_fps() :.1f}')

    def draw(self):
        # Render surface'e çiz
        self.render_surface.fill((0, 0, 0))
        
        # Geçici olarak screen'i değiştir
        original_screen = self.object_renderer.screen
        self.object_renderer.screen = self.render_surface
        
        if not self.paused:
            self.object_renderer.draw()
            # Weapon için de
            self.render_surface.blit(self.weapon.images[0], self.weapon.weapon_pos)
        
        # Screen'i geri al
        self.object_renderer.screen = original_screen
        
        # Tam ekran modunda scale et
        if self.fullscreen:
            # Monitör boyutunu al
            info = pg.display.Info()
            monitor_w = info.current_w
            monitor_h = info.current_h
            
            # Tam ekranı dolduracak şekilde scale et (crop)
            scale_x = monitor_w / WIDTH
            scale_y = monitor_h / HEIGHT
            
            # En büyük scale'i kullan - böylece tüm ekran dolar
            scale = max(scale_x, scale_y)
            
            new_width = int(WIDTH * scale)
            new_height = int(HEIGHT * scale)
            
            # Ortala (bazı kısımlar kırpılabilir)
            x_offset = (monitor_w - new_width) // 2
            y_offset = (monitor_h - new_height) // 2
            
            # Scale et ve çiz
            scaled = pg.transform.smoothscale(self.render_surface, (new_width, new_height))
            self.screen.blit(scaled, (x_offset, y_offset))
        else:
            # Pencere modunda direkt kopyala
            self.screen.blit(self.render_surface, (0, 0))
        
        if self.paused:
            self.pause_menu.draw()
        
        pg.display.flip()

    def toggle_pause(self):
        """Oyunu duraklat/devam ettir"""
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
                    if not self.paused:
                        self.toggle_pause()
                    else:
                        self.toggle_pause()
                
                elif event.key == pg.K_q and self.paused:
                    # Ana menüye dön
                    self.paused = False
                    self.show_menu()
                    
                elif event.key == pg.K_F11:
                    # F11 ile de tam ekran geçişi
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