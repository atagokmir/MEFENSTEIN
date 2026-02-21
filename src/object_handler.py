from sprite_object import *
from npc import *
from pickup import *
from random import choices, randrange


class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.pickup_list = []  # Toplanabilir eşyalar
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        add_pickup = self.add_pickup
        self.npc_positions = {}

        # spawn npc
        self.enemies = 20  # npc count
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()
        
        # Mermi ve sağlık paketleri spawn et
        self.spawn_pickups()

        # sprite map
        add_sprite(AnimatedSprite(game))
        add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
        add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
                npc = choices(self.npc_types, self.weights)[0]
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                    pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
                self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))
    
    def spawn_pickups(self):
        """Haritaya mermi ve sağlık paketleri yerleştir"""
        # Mermi paketleri
        ammo_positions = [
            (3.5, 3.5),
            (12.5, 19.5),
            (4.5, 12.5),
            (13.5, 2.5),
            (2.5, 28.5),
            (14.5, 15.5),
            (7.5, 8.5),
            (10.5, 25.5),
            (5.5, 20.5),
            (8.5, 13.5)
        ]
        
        for pos in ammo_positions:
            # Pozisyon boşsa ekle
            if (int(pos[0]), int(pos[1])) not in self.game.map.world_map:
                self.add_pickup(AmmoPickup(self.game, pos))
        
        # Sağlık paketleri
        health_positions = [
            (6.5, 4.5),
            (11.5, 11.5),
            (2.5, 15.5),
            (13.5, 28.5),
            (8.5, 22.5)
        ]
        
        for pos in health_positions:
            if (int(pos[0]), int(pos[1])) not in self.game.map.world_map:
                self.add_pickup(HealthPickup(self.game, pos))
    
    def spawn_random_ammo(self):
        """Düşman öldüğünde rastgele mermi spawn et"""
        # %50 şansla mermi düşür
        if randrange(2) == 0:
            # Rastgele boş bir pozisyon bul
            for _ in range(10):  # 10 deneme
                x = randrange(1, self.game.map.cols - 1)
                y = randrange(1, self.game.map.rows - 1)
                if (x, y) not in self.game.map.world_map:
                    self.add_pickup(AmmoPickup(self.game, (x + 0.5, y + 0.5)))
                    break

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        [pickup.update() for pickup in self.pickup_list if pickup.active]
        
        # Aktif olmayan pickup'ları temizle
        self.pickup_list = [p for p in self.pickup_list if p.active]
        
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)
    
    def add_pickup(self, pickup):
        self.pickup_list.append(pickup)