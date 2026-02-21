from sprite_object import *


class Weapon(AnimatedSprite):
    def __init__(self, game, weapon_type='shotgun'):
        self.game = game
        self.weapon_type = weapon_type
        
        # Sabit hedef yükseklik — her silah aynı boyutta görünür
        self.weapons = {
            'shotgun': {
                'path': 'resources/sprites/weapon/shotgun/0.png',
                'target_height': 180,
                'animation_time': 90,
                'damage': 50,
                'ammo_cost': 1,
                'range': 5,
                'spread': True,
                'fire_rate': 90
            },
            'rifle': {
                'path': 'resources/sprites/weapon/rifle/0.png',
                'target_height': 180,
                'animation_time': 60,
                'damage': 25,
                'ammo_cost': 1,
                'range': 10,
                'spread': False,
                'fire_rate': 60
            }
        }
        
        # Mevcut silahı ayarla
        self.current_weapon = self.weapons[weapon_type]
        
        # Sprite'ı başlat
        super().__init__(
            game=game,
            path=self.current_weapon['path'],
            scale=1,
            animation_time=self.current_weapon['animation_time']
        )
        
        self.images = deque(
            [self._scale_image(img, self.current_weapon['target_height'])
             for img in self.images])
        
        self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
        self.reloading = False
        self.num_images = len(self.images)
        self.frame_counter = 0
        
        # Dinamik özellikler
        self.damage = self.current_weapon['damage']
        self.ammo_cost = self.current_weapon['ammo_cost']
        self.fire_rate = self.current_weapon['fire_rate']
        self.last_shot_time = 0

    def _scale_image(self, img, target_height):
        """Görseli hedef yüksekliğe orantılı scale et"""
        ratio = img.get_width() / img.get_height()
        target_width = int(target_height * ratio)
        return pg.transform.smoothscale(img, (target_width, target_height))

    def switch_weapon(self, weapon_type):
        """Silah değiştir"""
        if weapon_type in self.weapons and weapon_type != self.weapon_type:
            self.weapon_type = weapon_type
            self.current_weapon = self.weapons[weapon_type]
            
            # Özellikleri güncelle
            self.damage = self.current_weapon['damage']
            self.ammo_cost = self.current_weapon['ammo_cost']
            self.fire_rate = self.current_weapon['fire_rate']
            self.animation_time = self.current_weapon['animation_time']
            
            # Sprite'ları yeniden yükle
            self.path = self.current_weapon['path']
            self.images = self.get_images(self.path.rsplit('/', 1)[0])
            self.images = deque(
                [self._scale_image(img, self.current_weapon['target_height'])
                 for img in self.images])
            
            self.num_images = len(self.images)
            self.frame_counter = 0
            self.reloading = False
            
            self.weapon_pos = (HALF_WIDTH - self.images[0].get_width() // 2, HEIGHT - self.images[0].get_height())
            self.image = self.images[0]
            
            # Silah değiştirme sesi
            try:
                self.game.sound.weapon_switch.play()
            except:
                pass

    def can_shoot(self):
        """Ateş edebilir mi kontrolü"""
        current_time = pg.time.get_ticks()
        if current_time - self.last_shot_time >= self.fire_rate:
            return True
        return False

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0
                    self.last_shot_time = pg.time.get_ticks()

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)
        
        # Silah adını göster
        weapon_font = pg.font.Font(None, 30)
        weapon_text = weapon_font.render(self.weapon_type.upper(), True, (200, 200, 200))
        self.game.screen.blit(weapon_text, (WIDTH - 150, HEIGHT - 40))

    def update(self):
        self.check_animation_time()
        self.animate_shot()