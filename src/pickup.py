from sprite_object import *
import math


class Pickup(AnimatedSprite):
    def __init__(self, game, path, pos=(10.5, 10.5), scale=0.4, shift=0.5, animation_time=120):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.pickup_radius = 0.5  # Toplama mesafesi
        self.active = True
        self.bob_offset = 0  # Yukarı aşağı hareket için
        
    def update(self):
        if not self.active:
            return
            
        # Animasyon güncelle
        super().update()
        
        # Yukarı aşağı hareket
        self.bob_offset = math.sin(pg.time.get_ticks() * 0.005) * 0.1
        
        # Oyuncuya olan mesafeyi kontrol et
        dx = self.x - self.game.player.x
        dy = self.y - self.game.player.y
        distance = math.hypot(dx, dy)
        
        if distance < self.pickup_radius:
            self.on_pickup()
            self.active = False
    
    def on_pickup(self):
        """Alt sınıflarda override edilecek"""
        pass
        
    def get_sprite_projection(self):
        if not self.active:
            return
            
        # Bob efekti ekle
        original_shift = self.SPRITE_HEIGHT_SHIFT
        self.SPRITE_HEIGHT_SHIFT = original_shift + self.bob_offset
        
        super().get_sprite_projection()
        
        # Shift'i geri al
        self.SPRITE_HEIGHT_SHIFT = original_shift


class AmmoPickup(Pickup):
    def __init__(self, game, pos=(10.5, 10.5)):
        # Mermi kutusu sprite'ı (yoksa basit bir sprite kullan)
        path = 'resources/sprites/pickups/ammo/0.png'            
        super().__init__(game, path, pos, scale=0.3, shift=0.6)
        self.ammo_amount = 10  # Verilecek mermi sayısı
        
    def on_pickup(self):
        """Mermi toplandığında"""
        if self.game.player.ammo < PLAYER_MAX_AMMO:
            self.game.player.add_ammo(self.ammo_amount)
            # Kendini listeden kaldır
            if self in self.game.object_handler.pickup_list:
                self.game.object_handler.pickup_list.remove(self)


class HealthPickup(Pickup):
    def __init__(self, game, pos=(10.5, 10.5)):
        # Sağlık paketi sprite'ı
        path = 'resources/sprites/pickups/health/0.png'
            
        super().__init__(game, path, pos, scale=0.3, shift=0.6)
        self.health_amount = 25  # Verilecek can miktarı
        
    def on_pickup(self):
        """Sağlık toplandığında"""
        if self.game.player.health < PLAYER_MAX_HEALTH:
            self.game.player.health = min(self.game.player.health + self.health_amount, PLAYER_MAX_HEALTH)
            try:
                self.game.sound.health_pickup.play()
            except:
                pass
            # Kendini listeden kaldır
            if self in self.game.object_handler.pickup_list:
                self.game.object_handler.pickup_list.remove(self)