import pygame
import random
import math
import sys

# Inizializzazione
pygame.init()
pygame.mixer.init()

# Costanti
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)

# Setup schermo
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOSS RUN - 6 Epic Battles")
clock = pygame.time.Clock()

# Font
title_font = pygame.font.Font(None, 80)
large_font = pygame.font.Font(None, 60)
medium_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

# Musica (suoni generati proceduralmente)
class SoundManager:
    def __init__(self):
        self.music_playing = False
        
    def play_menu_music(self):
        if not self.music_playing:
            self.music_playing = True
            
    def play_battle_music(self):
        pass
    
    def play_victory_sound(self):
        pass
    
    def play_hit_sound(self):
        pass

sound_manager = SoundManager()

# Particelle
class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 30
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# Proiettile
class Projectile:
    def __init__(self, x, y, target_x, target_y, color, speed, damage, size=8):
        self.x = x
        self.y = y
        angle = math.atan2(target_y - y, target_x - x)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.damage = damage
        self.size = size
        self.active = True
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
            
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size // 2)

# Player
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 150
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 6
        self.size = 20
        self.color = CYAN
        self.shoot_cooldown = 0
        self.shoot_delay = 15
        self.damage = 10
        
    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.size, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(WIDTH - self.size, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(HEIGHT // 2, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(HEIGHT - self.size, self.y + self.speed)
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def shoot(self, target_x, target_y):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = self.shoot_delay
            return Projectile(self.x, self.y, target_x, target_y, YELLOW, 12, self.damage)
        return None
        
    def draw(self, surface):
        # Corpo
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size - 5)
        # Occhi
        pygame.draw.circle(surface, BLACK, (int(self.x - 7), int(self.y - 5)), 3)
        pygame.draw.circle(surface, BLACK, (int(self.x + 7), int(self.y - 5)), 3)
        
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0

# Boss Base
class Boss:
    def __init__(self, name, hp, color):
        self.name = name
        self.x = WIDTH // 2
        self.y = 150
        self.max_hp = hp
        self.hp = hp
        self.color = color
        self.size = 50
        self.attack_cooldown = 0
        self.phase = 1
        self.movement_timer = 0
        
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        if self.hp <= self.max_hp // 2 and self.phase == 1:
            self.phase = 2
            self.on_phase_change()
        return self.hp <= 0
        
    def on_phase_change(self):
        pass
        
    def update(self):
        self.movement_timer += 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
    def attack(self, player):
        return []
        
    def draw(self, surface):
        pass

# Boss 1: The Orbiter - Spara proiettili orbitanti
class OrbiterBoss(Boss):
    def __init__(self):
        super().__init__("THE ORBITER", 300, BLUE)
        self.orbit_angle = 0
        self.satellites = []
        
    def update(self):
        super().update()
        self.orbit_angle += 2
        # Movimento ondulatorio
        self.x = WIDTH // 2 + math.sin(self.movement_timer * 0.02) * 200
        
    def attack(self, player):
        projectiles = []
        if self.attack_cooldown == 0:
            if self.phase == 1:
                # Fase 1: 4 proiettili in direzioni cardinali
                for angle in [0, 90, 180, 270]:
                    rad = math.radians(angle)
                    target_x = self.x + math.cos(rad) * 500
                    target_y = self.y + math.sin(rad) * 500
                    projectiles.append(Projectile(self.x, self.y, target_x, target_y, BLUE, 5, 8))
                self.attack_cooldown = 60
            else:
                # Fase 2: 8 proiettili in tutte le direzioni
                for i in range(8):
                    angle = i * 45
                    rad = math.radians(angle)
                    target_x = self.x + math.cos(rad) * 500
                    target_y = self.y + math.sin(rad) * 500
                    projectiles.append(Projectile(self.x, self.y, target_x, target_y, CYAN, 6, 10))
                self.attack_cooldown = 45
        return projectiles
        
    def draw(self, surface):
        # Orbite
        for i in range(3):
            radius = 40 + i * 20
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius, 2)
        # Corpo centrale
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size - 10)
        # Satelliti
        for i in range(4):
            angle = self.orbit_angle + i * 90
            sat_x = self.x + math.cos(math.radians(angle)) * 60
            sat_y = self.y + math.sin(math.radians(angle)) * 60
            pygame.draw.circle(surface, YELLOW, (int(sat_x), int(sat_y)), 8)

# Boss 2: The Swarm - Evoca minion
class SwarmBoss(Boss):
    def __init__(self):
        super().__init__("THE SWARM", 250, GREEN)
        self.minions = []
        
    def update(self):
        super().update()
        # Movimento circolare
        self.x = WIDTH // 2 + math.cos(self.movement_timer * 0.03) * 150
        self.y = 150 + math.sin(self.movement_timer * 0.03) * 50
        
        # Aggiorna minion
        for minion in self.minions[:]:
            minion['timer'] += 1
            if minion['timer'] > 180:
                self.minions.remove(minion)
                
    def attack(self, player):
        projectiles = []
        if self.attack_cooldown == 0:
            if self.phase == 1:
                # Evoca 2 minion
                for _ in range(2):
                    self.minions.append({
                        'x': self.x + random.randint(-100, 100),
                        'y': self.y + random.randint(50, 150),
                        'timer': 0
                    })
                self.attack_cooldown = 90
            else:
                # Fase 2: Evoca più minion e sparano
                for _ in range(3):
                    self.minions.append({
                        'x': self.x + random.randint(-100, 100),
                        'y': self.y + random.randint(50, 150),
                        'timer': 0
                    })
                # I minion sparano
                for minion in self.minions:
                    if minion['timer'] % 30 == 0:
                        projectiles.append(Projectile(minion['x'], minion['y'], 
                                                     player.x, player.y, GREEN, 4, 6, 6))
                self.attack_cooldown = 75
        return projectiles
        
    def draw(self, surface):
        # Disegna minion
        for minion in self.minions:
            pulse = abs(math.sin(minion['timer'] * 0.1)) * 5
            pygame.draw.circle(surface, (0, 200, 0), (int(minion['x']), int(minion['y'])), int(10 + pulse))
        # Corpo principale
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        for i in range(3):
            angle = self.movement_timer * 5 + i * 120
            eye_x = self.x + math.cos(math.radians(angle)) * 20
            eye_y = self.y + math.sin(math.radians(angle)) * 20
            pygame.draw.circle(surface, BLACK, (int(eye_x), int(eye_y)), 8)

# Boss 3: The Laser Sentinel - Spara laser
class LaserBoss(Boss):
    def __init__(self):
        super().__init__("LASER SENTINEL", 350, RED)
        self.laser_active = False
        self.laser_target_y = 0
        self.laser_charge = 0
        
    def update(self):
        super().update()
        self.x = WIDTH // 2 + math.sin(self.movement_timer * 0.015) * 250
        
    def attack(self, player):
        projectiles = []
        if self.attack_cooldown == 0:
            if self.phase == 1:
                # Spara 3 proiettili verso il player
                for offset in [-30, 0, 30]:
                    projectiles.append(Projectile(self.x, self.y,player.x + offset, player.y, RED, 7, 12))         
                self.attack_cooldown = 50
            else:
                # Fase 2: Pattern a ventaglio
                for i in range(5):
                    angle = -60 + i * 30
                    rad = math.radians(angle + 90)
                    target_x = self.x + math.cos(rad) * 500
                    target_y = self.y + math.sin(rad) * 500
                    projectiles.append(Projectile(self.x, self.y, target_x, target_y, ORANGE, 8, 15))
                self.attack_cooldown = 40
        return projectiles
        
    def draw(self, surface):
        # Corpo con cannoni
        pygame.draw.rect(surface, self.color, 
                        (int(self.x - self.size), int(self.y - self.size // 2), 
                         self.size * 2, self.size))
        # Cannone laser
        pygame.draw.rect(surface, DARK_RED, 
                        (int(self.x - 10), int(self.y - self.size // 2 - 20), 20, 20))
        # Energia pulsante
        pulse = abs(math.sin(self.movement_timer * 0.1)) * 10
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), int(15 + pulse))

class SentinelBoss(Boss):
    def __init__(self):
        super().__init__(name="Sentinel", hp=200, color=(150, 200, 255))
        self.orbit_radius = 200
        self.orbit_speed = 0.02
        self.angle = 0
        self.shield_active = False
        self.shield_timer = 0

    def update(self):
        # Movimento orbitale attorno al centro dello schermo
        self.angle += self.orbit_speed
        self.x = WIDTH // 2 + math.cos(self.angle) * self.orbit_radius
        self.y = HEIGHT // 2 + math.sin(self.angle) * self.orbit_radius

        # Gestione scudo
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False

    def attack(self, player):
        projectiles = []
        if random.random() < 0.02:
            # Spara 8 proiettili radiali
            for i in range(8):
                angle = math.radians(i * 45)
                dx, dy = math.cos(angle), math.sin(angle)
                projectiles.append(Projectile(self.x, self.y, player.x, player.y, RED, speed=5, damage=10))
        # Attiva scudo a intervalli
        if random.random() < 0.005:
            self.shield_active = True
            self.shield_timer = 120
        return projectiles

    def take_damage(self, damage):
        if self.shield_active:
            # Lo scudo blocca completamente i danni
            return False
        return super().take_damage(damage)

# Boss 5: The Spinner - Rotazione e proiettili rotanti
class SpinnerBoss(Boss):
    def __init__(self):
        super().__init__("THE SPINNER", 320, ORANGE)
        self.rotation = 0
        self.spin_speed = 3
        
    def update(self):
        super().update()
        self.rotation += self.spin_speed
        if self.phase == 2:
            self.spin_speed = 5
        # Movimento a spirale
        radius = 100 + abs(math.sin(self.movement_timer * 0.02)) * 100
        self.x = WIDTH // 2 + math.cos(self.movement_timer * 0.03) * radius
        self.y = 150 + math.sin(self.movement_timer * 0.03) * radius // 2
        
    def attack(self, player):
        projectiles = []
        if self.attack_cooldown == 0:
            num_projectiles = 6 if self.phase == 1 else 10
            for i in range(num_projectiles):
                angle = self.rotation + (360 / num_projectiles) * i
                rad = math.radians(angle)
                target_x = self.x + math.cos(rad) * 500
                target_y = self.y + math.sin(rad) * 500
                speed = 5 if self.phase == 1 else 7
                projectiles.append(Projectile(self.x, self.y, target_x, target_y, 
                                             ORANGE, speed, 11))
            self.attack_cooldown = 55 if self.phase == 1 else 40
        return projectiles
        
    def draw(self, surface):
        # Disegna bracci rotanti
        for i in range(4):
            angle = self.rotation + i * 90
            rad = math.radians(angle)
            end_x = self.x + math.cos(rad) * 60
            end_y = self.y + math.sin(rad) * 60
            pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), 8)
            pygame.draw.circle(surface, YELLOW, (int(end_x), int(end_y)), 12)
        # Nucleo
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size - 15)

# Boss 6: The Final Chaos - Boss finale con tutti gli attacchi
class ChaosBoss(Boss):
    def __init__(self):
        super().__init__("THE FINAL CHAOS", 500, PURPLE)
        self.phase_timer = 0
        self.enraged = False
        self.teleport_cooldown = 300

    def update(self):
        self.phase_timer += 1
        self.teleport_cooldown -= 1

        # Enrage sotto 30% HP
        if not self.enraged and self.hp <= self.max_hp * 0.3:
            self.enraged = True
            self.color = (255, 0, 200)

    def attack(self, player):
        projectiles = []
        if random.random() < (0.05 if not self.enraged else 0.12):
            pattern = random.choice(["burst", "spiral", "aimed"])
            if pattern == "burst":
                # Cerchio di 12 proiettili
                for i in range(12):
                    angle = math.radians(i * 30)
                    dx, dy = math.cos(angle) * 6, math.sin(angle) * 6
                    projectiles.append(Projectile(self.x, self.y, player.x, player.y, RED, speed=5, damage=10))
            elif pattern == "spiral":
                # Spirale di 8 proiettili ruotati
                for i in range(8):
                    angle = math.radians(i * 45 + self.phase_timer * 5)
                    dx, dy = math.cos(angle) * 5, math.sin(angle) * 5
                    projectiles.append(Projectile(self.x, self.y, player.x, player.y, RED, speed=4, damage=15))
            elif pattern == "aimed":
                # Raffica diretta verso il player
                dx, dy = player.x - self.x, player.y - self.y
                dist = math.hypot(dx, dy)
                dx, dy = dx / dist * 8, dy / dist * 8
                for i in range(3 if not self.enraged else 6):
                    projectiles.append(Projectile(self.x, self.y, player.x, player.y, PURPLE, speed=7, damage=20))
        return projectiles

# UIa
def draw_health_bar(surface, x, y, width, height, hp, max_hp, color):
    # Bordo
    pygame.draw.rect(surface, WHITE, (x - 2, y - 2, width + 4, height + 4), 2)
    # Background
    pygame.draw.rect(surface, DARK_GRAY, (x, y, width, height))
    # HP bar
    hp_width = int((hp / max_hp) * width)
    pygame.draw.rect(surface, color, (x, y, hp_width, height))
    # Testo HP
    hp_text = small_font.render(f"{int(hp)}/{int(max_hp)}", True, WHITE)
    surface.blit(hp_text, (x + width // 2 - hp_text.get_width() // 2, y + 2))

def draw_timer(surface, time_seconds):
    minutes = int(time_seconds // 60)
    seconds = int(time_seconds % 60)
    timer_text = medium_font.render(f"TIME: {minutes:02d}:{seconds:02d}", True, WHITE)
    surface.blit(timer_text, (WIDTH - 200, 20))

# Stati del gioco
class GameState:
    MENU = 0
    PLAYING = 1
    VICTORY = 2
    GAME_OVER = 3

# Game Manager
class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.player = None
        self.current_boss_index = 0
        self.boss = None
        self.projectiles = []
        self.particles = []
        self.start_time = 0
        self.elapsed_time = 0
        self.total_time = 0
        self.transition_timer = 0
        self.next_boss_index = 0
        self.boss_classes = [
            OrbiterBoss,
            SwarmBoss,
            LaserBoss,
            SentinelBoss,
            SpinnerBoss,
            ChaosBoss
        ]
        
    def start_game(self):
        self.state = GameState.PLAYING
        self.player = Player()
        self.current_boss_index = 0
        self.projectiles = []
        self.particles = []
        self.start_time = pygame.time.get_ticks()
        self.load_boss()
        sound_manager.play_battle_music()
        
    def load_boss(self):
        self.boss = self.boss_classes[self.current_boss_index]()
        self.projectiles = []
        
    def update(self):
        # --- Gioco attivo ---
        if self.state == GameState.PLAYING:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            keys = pygame.key.get_pressed()
            self.player.update(keys)
    
            # --- Spara solo se non in transizione ---
            if self.boss and self.transition_timer == 0:
                proj = self.player.shoot(self.boss.x, self.boss.y)
                if proj:
                    self.projectiles.append(proj)
    
            # --- Aggiorna boss e attacchi (solo se non in pausa) ---
            if self.boss and self.transition_timer == 0:
                self.boss.update()
                new_projectiles = self.boss.attack(self.player)
                self.projectiles.extend(new_projectiles)
    
            # --- Aggiorna proiettili ---
            for proj in self.projectiles[:]:
                proj.update()
                if not proj.active:
                    self.projectiles.remove(proj)
                    continue
                
                # --- Collisione con player (solo proiettili nemici) ---
                if proj.color != YELLOW:
                    dist = math.dist((proj.x, proj.y), (self.player.x, self.player.y))
                    if dist < self.player.size + proj.size:
                        if self.player.take_damage(proj.damage):
                            self.state = GameState.GAME_OVER
                            self.total_time = self.elapsed_time
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
                        # Particelle di impatto
                        for _ in range(10):
                            vel = (random.uniform(-3, 3), random.uniform(-3, 3))
                            self.particles.append(Particle(proj.x, proj.y, RED, vel))
                        continue
                    
                # --- Collisione con boss (solo proiettili del player) ---
                if proj.color == YELLOW and self.boss:
                    dist = math.dist((proj.x, proj.y), (self.boss.x, self.boss.y))
                    if dist < self.boss.size + proj.size:
                        boss_died = self.boss.take_damage(proj.damage)
    
                        # Rimuovi il proiettile solo se ancora presente
                        if proj in self.projectiles:
                            self.projectiles.remove(proj)
    
                        # Effetto particelle
                        for _ in range(15):
                            vel = (random.uniform(-4, 4), random.uniform(-4, 4))
                            self.particles.append(Particle(proj.x, proj.y, self.boss.color, vel))
                        sound_manager.play_hit_sound()
    
                        if boss_died:
                            # --- Boss sconfitto: prepara transizione ---
                            self.transition_timer = 120  # 2 secondi
                            self.next_boss_index = self.current_boss_index + 1
    
                            if self.next_boss_index >= len(self.boss_classes):
                                self.state = GameState.VICTORY
                                self.total_time = self.elapsed_time
                            else:
                                # Congela boss e proiettili per la transizione
                                self.boss = None
                                self.projectiles.clear()
                                self.particles.clear()
                        break  # esci dal ciclo per evitare doppie collisioni
                    
                # --- Collisione con minion (solo per SwarmBoss) ---
                if proj.color == YELLOW and isinstance(self.boss, SwarmBoss):
                    for minion in self.boss.minions[:]:
                        dist = math.dist((proj.x, proj.y), (minion["x"], minion["y"]))
                        if dist < 15:
                            self.boss.minions.remove(minion)
                            if proj in self.projectiles:
                                self.projectiles.remove(proj)
                            for _ in range(8):
                                vel = (random.uniform(-3, 3), random.uniform(-3, 3))
                                self.particles.append(Particle(minion["x"], minion["y"], GREEN, vel))
                            break
                        
            # --- Aggiorna particelle ---
            for particle in self.particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.particles.remove(particle)
    
        # --- Gestione transizione boss (fuori dallo stato PLAYING) ---
        if hasattr(self, "transition_timer") and self.transition_timer > 0:
            self.transition_timer -= 1
            if self.transition_timer == 0:
                if self.next_boss_index < len(self.boss_classes):
                    self.current_boss_index = self.next_boss_index
                    self.load_boss()

    
    def draw(self):
        screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
    
    def draw_menu(self):
        # Sfondo animato
        for i in range(10):
            x = (WIDTH // 10 * i + pygame.time.get_ticks() // 10) % WIDTH
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT), 2)
        
        # Titolo con effetto
        title_offset = math.sin(pygame.time.get_ticks() * 0.003) * 10
        title = title_font.render("BOSS RUN", True, CYAN)
        title_shadow = title_font.render("BOSS RUN", True, BLUE)
        screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 5, 100 + title_offset + 5))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100 + title_offset))
        
        subtitle = medium_font.render("6 Epic Battles Await", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 200))
        
        # Istruzioni
        instructions = [
            "CONTROLS:",
            "WASD / Arrow Keys - Move",
            "Auto-shoot at boss",
            "",
            "Defeat all 6 bosses!",
            "Each boss has 2 phases"
        ]
        
        y_pos = 300
        for line in instructions:
            if line == "CONTROLS:":
                text = medium_font.render(line, True, YELLOW)
            else:
                text = small_font.render(line, True, LIGHT_GRAY)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 40
        
        # Pulsante start con animazione
        button_pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 20
        button_rect = pygame.Rect(WIDTH // 2 - 150, 600, 300, 80)
        pygame.draw.rect(screen, CYAN, button_rect.inflate(button_pulse, button_pulse), 3)
        pygame.draw.rect(screen, DARK_GRAY, button_rect)
        
        start_text = large_font.render("START", True, WHITE)
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 620))
        
        # Preview bosses
        boss_y = HEIGHT - 100
        boss_names = ["Orbiter", "Swarm", "Laser", "Teleporter", "Spinner", "Chaos"]
        colors = [BLUE, GREEN, RED, PURPLE, ORANGE, (255, 0, 255)]
        
        for i, (name, color) in enumerate(zip(boss_names, colors)):
            x = 100 + i * 180
            pygame.draw.circle(screen, color, (x, boss_y), 25)
            name_text = small_font.render(name, True, WHITE)
            screen.blit(name_text, (x - name_text.get_width() // 2, boss_y + 35))
    
    def draw_game(self):
        # Sfondo con griglia
        for i in range(0, WIDTH, 50):
            pygame.draw.line(screen, (30, 30, 30), (i, 0), (i, HEIGHT))
        for i in range(0, HEIGHT, 50):
            pygame.draw.line(screen, (30, 30, 30), (0, i), (WIDTH, i))
        
        # Linea di separazione
        pygame.draw.line(screen, WHITE, (0, HEIGHT // 2 - 50), (WIDTH, HEIGHT // 2 - 50), 2)
        
        # Disegna particelle
        for particle in self.particles:
            particle.draw(screen)
        
        # Disegna proiettili
        for proj in self.projectiles:
            proj.draw(screen)
        
        # Disegna boss
        if self.boss:
            self.boss.draw(screen)
            # Boss HP
            draw_health_bar(screen, WIDTH // 2 - 250, 50, 500, 30, 
                          self.boss.hp, self.boss.max_hp, self.boss.color)
            # Nome boss
            boss_name = large_font.render(self.boss.name, True, WHITE)
            screen.blit(boss_name, (WIDTH // 2 - boss_name.get_width() // 2, 10))
            # Fase
            phase_text = small_font.render(f"PHASE {self.boss.phase}", True, YELLOW if self.boss.phase == 2 else WHITE)
            screen.blit(phase_text, (WIDTH // 2 + 260, 55))
        
        # Disegna player
        self.player.draw(screen)
        
        # Player HP
        draw_health_bar(screen, 50, HEIGHT - 80, 300, 30, 
                       self.player.hp, self.player.max_hp, CYAN)
        player_label = small_font.render("PLAYER", True, WHITE)
        screen.blit(player_label, (50, HEIGHT - 110))
        
        # Boss counter
        boss_counter = medium_font.render(f"BOSS {self.current_boss_index + 1} / 6", True, WHITE)
        screen.blit(boss_counter, (50, 20))
        
        # Timer
        draw_timer(screen, self.elapsed_time)
        
        # Warning se HP basso
        if self.player.hp < 30:
            warning_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255)
            warning_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            warning_surf.fill((255, 0, 0, warning_alpha // 4))
            screen.blit(warning_surf, (0, 0))
            
            warning_text = large_font.render("LOW HP!", True, RED)
            screen.blit(warning_text, (WIDTH // 2 - warning_text.get_width() // 2, HEIGHT - 150))
    
    def draw_victory(self):
        # Sfondo celebrativo
        for i in range(50):
            x = random.randint(0, WIDTH)
            y = (random.randint(0, HEIGHT) + pygame.time.get_ticks() // 5) % HEIGHT
            size = random.randint(2, 5)
            color = random.choice([YELLOW, CYAN, GREEN, PURPLE])
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Titolo vittoria
        victory_text = title_font.render("VICTORY!", True, YELLOW)
        victory_shadow = title_font.render("VICTORY!", True, ORANGE)
        y_offset = math.sin(pygame.time.get_ticks() * 0.003) * 10
        screen.blit(victory_shadow, (WIDTH // 2 - victory_text.get_width() // 2 + 5, 150 + y_offset + 5))
        screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, 150 + y_offset))
        
        # Statistiche
        minutes = int(self.total_time // 60)
        seconds = int(self.total_time % 60)
        
        stats = [
            f"All 6 Bosses Defeated!",
            f"Total Time: {minutes:02d}:{seconds:02d}",
            f"Final HP: {int(self.player.hp)}/{self.player.max_hp}"
        ]
        
        y_pos = 300
        for stat in stats:
            text = medium_font.render(stat, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 60
        
        # Classificazione tempo
        if self.total_time < 180:
            rank = "S - LEGENDARY"
            rank_color = YELLOW
        elif self.total_time < 300:
            rank = "A - EXCELLENT"
            rank_color = CYAN
        elif self.total_time < 420:
            rank = "B - GREAT"
            rank_color = GREEN
        else:
            rank = "C - GOOD"
            rank_color = WHITE
        
        rank_text = large_font.render(f"RANK: {rank}", True, rank_color)
        screen.blit(rank_text, (WIDTH // 2 - rank_text.get_width() // 2, 500))
        
        # Pulsante restart
        button_pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
        button_rect = pygame.Rect(WIDTH // 2 - 150, 620, 300, 60)
        pygame.draw.rect(screen, GREEN, button_rect.inflate(button_pulse, button_pulse), 3)
        pygame.draw.rect(screen, DARK_GRAY, button_rect)
        
        restart_text = medium_font.render("PLAY AGAIN", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 635))
    
    def draw_game_over(self):
        # Sfondo scuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, 200))
        
        # Stats
        minutes = int(self.total_time // 60)
        seconds = int(self.total_time % 60)
        
        stats = [
            f"Defeated {self.current_boss_index} / 6 Bosses",
            f"Time Survived: {minutes:02d}:{seconds:02d}"
        ]
        
        y_pos = 350
        for stat in stats:
            text = medium_font.render(stat, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 60
        
        # Pulsante restart
        button_pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
        button_rect = pygame.Rect(WIDTH // 2 - 150, 550, 300, 60)
        pygame.draw.rect(screen, RED, button_rect.inflate(button_pulse, button_pulse), 3)
        pygame.draw.rect(screen, DARK_GRAY, button_rect)
        
        retry_text = medium_font.render("TRY AGAIN", True, WHITE)
        screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, 565))
        
        # Menu button
        menu_rect = pygame.Rect(WIDTH // 2 - 150, 640, 300, 60)
        pygame.draw.rect(screen, BLUE, menu_rect, 3)
        pygame.draw.rect(screen, DARK_GRAY, menu_rect)
        
        menu_text = medium_font.render("MAIN MENU", True, WHITE)
        screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 655))
    
    def handle_click(self, pos):
        if self.state == GameState.MENU:
            button_rect = pygame.Rect(WIDTH // 2 - 150, 600, 300, 80)
            if button_rect.collidepoint(pos):
                self.start_game()
        
        elif self.state == GameState.VICTORY:
            button_rect = pygame.Rect(WIDTH // 2 - 150, 620, 300, 60)
            if button_rect.collidepoint(pos):
                self.start_game()
        
        elif self.state == GameState.GAME_OVER:
            retry_rect = pygame.Rect(WIDTH // 2 - 150, 550, 300, 60)
            menu_rect = pygame.Rect(WIDTH // 2 - 150, 640, 300, 60)
            
            if retry_rect.collidepoint(pos):
                self.start_game()
            elif menu_rect.collidepoint(pos):
                self.state = GameState.MENU

# Main
def main():
    game = Game()
    sound_manager.play_menu_music()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.state == GameState.PLAYING:
                        game.state = GameState.MENU
                    else:
                        running = False
    
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
