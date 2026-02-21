import pygame as pg
import sys
import math
import random
from settings import *


class Menu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.render_surface = pg.Surface((WIDTH, HEIGHT))
        self.font_title = pg.font.Font(None, 120)
        self.font_menu = pg.font.Font(None, 60)
        self.font_small = pg.font.Font(None, 40)
        
        # Scale değerlerini başlat
        self.scale = 1
        self.scaled_width = WIDTH
        self.scaled_height = HEIGHT
        self.offset_x = 0
        self.offset_y = 0
        
        # Menü öğeleri
        self.menu_items = [
            {"text": "YENİ OYUN", "action": "new_game"},
            {"text": "AYARLAR", "action": "settings"},
            {"text": "HİKAYE", "action": "story"},
            {"text": "ÇIKIŞ", "action": "quit"}
        ]
        
        self.selected_index = 0
        self.menu_active = True
        self.current_menu = "main"  # main, settings, story
        
        # Ayarlar
        self.sound_enabled = True
        self.fullscreen = False
        
        # Animasyon değişkenleri
        self.title_offset = 0
        self.title_glow = 0
        self.bg_offset = 0
        
        # Arka plan efekti için
        self.stars = self.create_stars()
        self.lightning_timer = 0
        self.lightning_active = False
        
        # Ses efektleri
        try:
            self.menu_select = pg.mixer.Sound('resources/sound/menu_select.wav')
            self.menu_move = pg.mixer.Sound('resources/sound/menu_move.wav')
        except:
            self.menu_select = None
            self.menu_move = None

    def create_stars(self):
        """Arka plan için yıldızlar oluştur"""
        import random
        stars = []
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.randint(1, 3)
            size = random.randint(1, 3)
            stars.append({"x": x, "y": y, "speed": speed, "size": size})
        return stars

    def draw_background(self):
        """Animasyonlu arka plan çiz"""
        # Gradient arka plan
        for i in range(HEIGHT):
            color_value = int(20 + (i / HEIGHT) * 30)
            color = (color_value // 3, 0, color_value // 2)
            pg.draw.line(self.render_surface, color, (0, i), (WIDTH, i))
        
        # Hareketli yıldızlar
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] > HEIGHT:
                star["y"] = -10
                star["x"] = random.randint(0, WIDTH)
            
            brightness = int(100 + (math.sin(pg.time.get_ticks() * 0.001 + star["x"]) * 50))
            brightness = max(0, min(255, brightness))  # 0-255 arasında sınırla
            color = (brightness, brightness, min(255, int(brightness * 1.2)))
            pg.draw.circle(self.render_surface, color, (int(star["x"]), int(star["y"])), star["size"])
        
        # Periyodik yıldırım efekti
        self.lightning_timer += 1
        if self.lightning_timer > 300:
            self.lightning_active = True
            self.lightning_timer = 0
        
        if self.lightning_active:
            flash_alpha = max(0, 255 - (self.lightning_timer * 10))
            if flash_alpha > 0:
                flash_surface = pg.Surface((WIDTH, HEIGHT))
                flash_surface.fill((200, 200, 255))
                flash_surface.set_alpha(flash_alpha)
                self.render_surface.blit(flash_surface, (0, 0))
            else:
                self.lightning_active = False

    def draw_title(self):
        """Animasyonlu başlık çiz"""
        # Başlık animasyonu
        self.title_offset = math.sin(pg.time.get_ticks() * 0.002) * 10
        self.title_glow = abs(math.sin(pg.time.get_ticks() * 0.003)) * 55
        
        # Kan efekti için zaman bazlı değişim
        blood_factor = abs(math.sin(pg.time.get_ticks() * 0.001))
        
        # Gölge efekti
        shadow_text = self.font_title.render("MEFENSTEIN", True, (50, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 5, 150 + self.title_offset + 5))
        self.render_surface.blit(shadow_text, shadow_rect)
        
        # Başlığı ortala
        title_text = "MEFENSTEIN"
        text_width = self.font_title.size(title_text)[0]
        title_x = (WIDTH - text_width) // 2
        title_y = 150 + self.title_offset
        
        # MEF harflerinin pozisyonlarını hesapla
        m_width = self.font_title.size("M")[0]
        e_width = self.font_title.size("E")[0]
        f_width = self.font_title.size("F")[0]
        
        # M - Beyazdan kırmızıya geçiş
        m_red = int(255 * blood_factor)
        m_green = int(255 * (1 - blood_factor))
        m_blue = int(255 * (1 - blood_factor))
        m_text = self.font_title.render("M", True, (255, m_green, m_blue))
        self.render_surface.blit(m_text, (title_x, title_y))
        
        # E - Maviden kırmızıya geçiş
        e_red = int(255 * blood_factor)
        e_green = int(150 * (1 - blood_factor))
        e_blue = int(255 * (1 - blood_factor))
        e_text = self.font_title.render("E", True, (e_red, e_green, e_blue))
        self.render_surface.blit(e_text, (title_x + m_width, title_y))
        
        # F - Zaten kırmızı ama daha da koyulaşsın
        f_red = 255
        f_green = int(50 * (1 - blood_factor))
        f_blue = int(50 * (1 - blood_factor))
        f_text = self.font_title.render("F", True, (f_red, f_green, f_blue))
        self.render_surface.blit(f_text, (title_x + m_width + e_width, title_y))
        
        # ENSTEIN - Normal kırmızı
        red_value = min(255, int(200 + self.title_glow))
        enstein_x = title_x + m_width + e_width + f_width
        enstein_text = self.font_title.render("ENSTEIN", True, (red_value, 50, 50))
        self.render_surface.blit(enstein_text, (enstein_x, title_y))
        
        # Alt başlık
        subtitle = self.font_small.render("Cehennemden Kaçış", True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 220))
        self.render_surface.blit(subtitle, subtitle_rect)

    def draw_menu_items(self):
        """Menü öğelerini çiz"""
        menu_y = 350
        
        for i, item in enumerate(self.menu_items):
            # Seçili öğe animasyonu
            if i == self.selected_index:
                # Parlayan çerçeve
                glow_alpha = abs(math.sin(pg.time.get_ticks() * 0.005)) * 100 + 155
                border_color = (glow_alpha, 0, 0)
                pg.draw.rect(self.render_surface, border_color, 
                           (WIDTH // 2 - 200, menu_y + i * 80 - 35, 400, 70), 3)
                
                # Seçili öğe için büyütme efekti
                scale = 1.1 + math.sin(pg.time.get_ticks() * 0.003) * 0.05
                font = pg.font.Font(None, int(60 * scale))
                color = (255, 100, 100)
            else:
                font = self.font_menu
                color = (150, 150, 150)
            
            text = font.render(item["text"], True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, menu_y + i * 80))
            self.render_surface.blit(text, text_rect)

    def draw_settings_menu(self):
        """Ayarlar menüsünü çiz"""
        # Başlık
        title_text = self.font_title.render("AYARLAR", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        self.render_surface.blit(title_text, title_rect)
        
        # Ses ayarı
        sound_text = f"SES: {'AÇIK' if self.sound_enabled else 'KAPALI'}"
        sound_color = (0, 255, 0) if self.sound_enabled else (255, 0, 0)
        sound_render = self.font_menu.render(sound_text, True, sound_color)
        sound_rect = sound_render.get_rect(center=(WIDTH // 2, 300))
        self.render_surface.blit(sound_render, sound_rect)
        
        # Ekran modu
        screen_text = f"EKRAN: {'TAM EKRAN' if self.fullscreen else 'PENCERE'}"
        screen_render = self.font_menu.render(screen_text, True, (255, 255, 255))
        screen_rect = screen_render.get_rect(center=(WIDTH // 2, 400))
        self.render_surface.blit(screen_render, screen_rect)
        
        # Kontroller
        controls = [
            "SPACE - Ses Aç/Kapa",
            "F - Tam Ekran/Pencere", 
            "ESC - Geri Dön"
        ]
        
        y_pos = 550
        for control in controls:
            control_text = self.font_small.render(control, True, (150, 150, 150))
            control_rect = control_text.get_rect(center=(WIDTH // 2, y_pos))
            self.render_surface.blit(control_text, control_rect)
            y_pos += 40

    def draw_story_menu(self):
        """Hikaye menüsünü çiz"""
        # Başlık
        title_text = self.font_title.render("HİKAYE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        self.render_surface.blit(title_text, title_rect)
        
        # Hikaye metni
        story_lines = [
            "Yıl 2045. MEF Üniversitesi'nin gizli laboratuvarında",
            "yapılan deneyler kontrolden çıktı.",
            "",
            "Boyutlar arası portal açan deney, üniversiteyi",
            "cehennemin kendisine dönüştürdü.",
            "",
            "Şeytani yaratıklar kampüsü ele geçirdi.",
            "Hayatta kalan tek kişi sensin.",
            "",
            "Görevin: MEF'ten kaç ve dünyayı uyar!",
            "",
            "Ama önce... hayatta kalmalısın."
        ]
        
        y_pos = 200
        for line in story_lines:
            if line == "":
                y_pos += 20
                continue
                
            # MEF kelimesini renkli yap
            if "MEF" in line:
                parts = line.split("MEF")
                x_pos = WIDTH // 2 - 300
                
                # İlk kısım
                if parts[0]:
                    text1 = self.font_small.render(parts[0], True, (200, 200, 200))
                    self.render_surface.blit(text1, (x_pos, y_pos))
                    x_pos += text1.get_width()
                
                # MEF - renkli
                m_text = self.font_small.render("M", True, (255, 255, 255))
                self.render_surface.blit(m_text, (x_pos, y_pos))
                x_pos += m_text.get_width()
                
                e_text = self.font_small.render("E", True, (0, 150, 255))
                self.render_surface.blit(e_text, (x_pos, y_pos))
                x_pos += e_text.get_width()
                
                f_text = self.font_small.render("F", True, (255, 50, 50))
                self.render_surface.blit(f_text, (x_pos, y_pos))
                x_pos += f_text.get_width()
                
                # Son kısım
                if len(parts) > 1 and parts[1]:
                    text2 = self.font_small.render(parts[1], True, (200, 200, 200))
                    self.render_surface.blit(text2, (x_pos, y_pos))
            else:
                story_text = self.font_small.render(line, True, (200, 200, 200))
                story_rect = story_text.get_rect(center=(WIDTH // 2, y_pos))
                self.render_surface.blit(story_text, story_rect)
            
            y_pos += 35
        
        # Geri dön
        back_text = self.font_small.render("ESC - Ana Menüye Dön", True, (150, 150, 150))
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.render_surface.blit(back_text, back_rect)

    def draw_footer(self):
        """Alt bilgi çiz"""
        if self.current_menu == "main":
            footer_text = self.font_small.render("↑↓ Seç    ENTER Onayla    ESC Çık", True, (100, 100, 100))
            footer_rect = footer_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.render_surface.blit(footer_text, footer_rect)
        
        # Versiyon
        version_text = self.font_small.render("v1.0 - MEF Edition", True, (80, 80, 80))
        version_rect = version_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
        self.render_surface.blit(version_text, version_rect)

    def toggle_sound(self):
        """Ses ayarını değiştir"""
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            pg.mixer.music.unpause()
        else:
            pg.mixer.music.pause()

    def toggle_fullscreen(self):
        """Tam ekran modunu değiştir"""
        self.game.toggle_fullscreen()
        self.fullscreen = self.game.fullscreen

    def handle_input(self):
        """Kullanıcı girişlerini işle"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.current_menu != "main":
                        self.current_menu = "main"
                    else:
                        return "quit"
                
                # Ana menü kontrolleri
                if self.current_menu == "main":
                    if event.key == pg.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                        if self.menu_move and self.sound_enabled:
                            self.menu_move.play()
                    
                    elif event.key == pg.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                        if self.menu_move and self.sound_enabled:
                            self.menu_move.play()
                    
                    elif event.key == pg.K_RETURN:
                        if self.menu_select and self.sound_enabled:
                            self.menu_select.play()
                        action = self.menu_items[self.selected_index]["action"]
                        
                        if action == "settings":
                            self.current_menu = "settings"
                        elif action == "story":
                            self.current_menu = "story"
                        else:
                            return action
                
                # Ayarlar menüsü kontrolleri
                elif self.current_menu == "settings":
                    if event.key == pg.K_SPACE:
                        self.toggle_sound()
                    elif event.key == pg.K_f:
                        self.toggle_fullscreen()
        
        return None

    def run(self):
        """Ana menü döngüsü"""
        pg.mixer.music.pause()  # Oyun müziğini duraklat
        
        # Menü müziği başlat (varsa)
        try:
            pg.mixer.music.load('resources/sound/menu_theme.mp3')
            pg.mixer.music.set_volume(0.5)
            if self.sound_enabled:
                pg.mixer.music.play(-1)
        except:
            pass
        
        while self.menu_active:
            action = self.handle_input()
            
            if action == "quit":
                pg.quit()
                sys.exit()
            elif action == "new_game":
                self.menu_active = False
                pg.mixer.music.stop()
                return "new_game"
            
            # Menüyü çiz
            self.render_surface.fill((0, 0, 0))
            self.draw_background()
            
            if self.current_menu == "main":
                self.draw_title()
                self.draw_menu_items()
                self.draw_footer()
            elif self.current_menu == "settings":
                self.draw_settings_menu()
            elif self.current_menu == "story":
                self.draw_story_menu()
            
            self.screen = self.game.screen
            self.screen.fill((0, 0, 0))
            sw, sh = self.game.monitor_size
            if (sw, sh) != RES:
                scaled = pg.transform.smoothscale(self.render_surface, (sw, sh))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.blit(self.render_surface, (0, 0))
            
            pg.display.flip()
            self.clock.tick(60)


class PauseMenu:
    """Oyun içi duraklatma menüsü"""
    def __init__(self, game):
        self.game = game
        self.font = pg.font.Font(None, 80)
        self.font_small = pg.font.Font(None, 50)
        
    def draw(self):
        screen = self.game.screen
        sw, sh = self.game.monitor_size

        # Yarı saydam arka plan
        overlay = pg.Surface((sw, sh))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # PAUSED yazısı
        pause_text = self.font.render("DURAKLADI", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(sw // 2, sh // 2 - 50))
        screen.blit(pause_text, pause_rect)

        # İpucu
        hint_text = self.font_small.render("ESC - Devam Et    Q - Ana Menüye Dön", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(sw // 2, sh // 2 + 50))
        screen.blit(hint_text, hint_rect)