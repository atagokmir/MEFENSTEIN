import pygame as pg
from settings import *
import math


class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen  # Direkt game.screen'e render et
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        self.digit_size = 90
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_ammo_counter()  # Mermi sayacı
        self.draw_minimap()  # Mini harita

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def draw_ammo_counter(self):
        """Mermi sayacını çiz"""
        # Ammo yazısı
        ammo_font = pg.font.Font(None, 60)
        ammo_text = ammo_font.render("AMMO:", True, (255, 200, 0))
        self.screen.blit(ammo_text, (WIDTH - 300, 20))
        
        # Mermi sayısı
        ammo = str(self.game.player.ammo).zfill(2)  # 01, 02, ... 99 formatında
        x_offset = WIDTH - 180
        for i, digit in enumerate(ammo):
            if digit.isdigit():
                self.screen.blit(self.digits[digit], (x_offset + i * self.digit_size, 10))
        
        # Mermi yok uyarısı
        if self.game.player.ammo == 0:
            warning_font = pg.font.Font(None, 40)
            warning_text = warning_font.render("NO AMMO!", True, (255, 0, 0))
            warning_rect = warning_text.get_rect(center=(WIDTH // 2, 100))
            
            # Yanıp sönen efekt
            if pg.time.get_ticks() % 500 < 250:
                self.screen.blit(warning_text, warning_rect)

    def draw_minimap(self):
        """Mini haritayı çiz"""
        # Mini harita ayarları
        minimap_size = 200
        minimap_scale = minimap_size / max(self.game.map.cols, self.game.map.rows)
        minimap_x = WIDTH - minimap_size - 20
        minimap_y = HEIGHT - minimap_size - 20
        
        # Arka plan
        minimap_surface = pg.Surface((minimap_size, minimap_size))
        minimap_surface.fill((20, 20, 20))
        minimap_surface.set_alpha(180)
        
        # Duvarları çiz
        for (x, y), value in self.game.map.world_map.items():
            rect_x = int(x * minimap_scale)
            rect_y = int(y * minimap_scale)
            rect_size = int(minimap_scale)
            color = (80, 80, 80) if value < 3 else (100, 60, 60)
            pg.draw.rect(minimap_surface, color, (rect_x, rect_y, rect_size, rect_size))
        
        # Düşmanları çiz
        for npc in self.game.object_handler.npc_list:
            if npc.alive:
                npc_x = int(npc.x * minimap_scale)
                npc_y = int(npc.y * minimap_scale)
                pg.draw.circle(minimap_surface, (255, 0, 0), (npc_x, npc_y), 3)
        
        # Pickup'ları çiz
        for pickup in self.game.object_handler.pickup_list:
            if pickup.active:
                pickup_x = int(pickup.x * minimap_scale)
                pickup_y = int(pickup.y * minimap_scale)
                # Mermi = sarı, Sağlık = yeşil
                if hasattr(pickup, 'ammo_amount'):
                    color = (255, 255, 0)
                else:
                    color = (0, 255, 0)
                pg.draw.circle(minimap_surface, color, (pickup_x, pickup_y), 2)
        
        # Oyuncuyu çiz
        player_x = int(self.game.player.x * minimap_scale)
        player_y = int(self.game.player.y * minimap_scale)
        pg.draw.circle(minimap_surface, (0, 255, 255), (player_x, player_y), 4)
        
        # Oyuncunun baktığı yönü göster
        end_x = player_x + math.cos(self.game.player.angle) * 15
        end_y = player_y + math.sin(self.game.player.angle) * 15
        pg.draw.line(minimap_surface, (0, 255, 255), (player_x, player_y), (end_x, end_y), 2)
        
        # Mini haritayı ekrana çiz
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
        
        # Çerçeve
        pg.draw.rect(self.screen, (100, 100, 100), (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Etiket
        minimap_font = pg.font.Font(None, 20)
        minimap_text = minimap_font.render("RADAR", True, (150, 150, 150))
        self.screen.blit(minimap_text, (minimap_x + 5, minimap_y - 20))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }