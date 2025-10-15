import pygame
import sys
import math
import random

# Inizializzazione di pygame
pygame.init()

# Costanti
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

# Colori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 150, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 100
        self.hp = self.max_hp
        self.radius = 20
        self.speed = 5
        self.color = BLUE
        self.attack_range = 130
        self.attack_damage = 25
        self.last_direction_x = 0
        self.last_direction_y = 0

        self.dash_speed = 15
        self.dash_duration = 10
        self.dash_cooldown = 60
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

    def update(self, keys):
        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        if not self.is_dashing:
            movement_x = 0
            movement_y = 0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                movement_y = -self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                movement_y = self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                movement_x = -self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                movement_x = self.speed

            if movement_x != 0 or movement_y != 0:
                self.last_direction_x = movement_x
                self.last_direction_y = movement_y

            self.x += movement_x
            self.y += movement_y
        else:
            self.x += self.last_direction_x * (self.dash_speed / self.speed)
            self.y += self.last_direction_y * (self.dash_speed / self.speed)

        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))

    def dash(self):
        if self.dash_cooldown_timer <= 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            return True
        return False

    def can_attack(self, boss):
        distance = math.hypot(self.x - boss.x, self.y - boss.y)
        return distance <= self.attack_range

    def attack(self, boss):
        if self.can_attack(boss):
            boss.hp = max(0, boss.hp - self.attack_damage)
            return True
        return False

    def draw(self, screen):
        color = WHITE if self.is_dashing else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        inner_color = BLUE if self.is_dashing else WHITE
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), self.radius // 3)
    
    def can_attack_boss6(self, boss):
        """Controlla se può attaccare il boss6 o le sue torrette"""
        # Controlla se può attaccare il boss
        boss_dist = math.hypot(self.x - boss.x, self.y - boss.y)
        if boss_dist <= self.attack_range:
            return True
        
        # Controlla se può attaccare qualche torrette
        for turret in boss.turrets:
            if turret.hp > 0:
                turret_dist = math.hypot(self.x - turret.x, self.y - turret.y)
                if turret_dist <= self.attack_range:
                    return True
        
        return False

def attack_boss6(self, boss):
    """Attacca boss6 o le sue torrette (target più vicino)"""
    targets = []
    
    # Aggiungi il boss come target possibile
    boss_dist = math.hypot(self.x - boss.x, self.y - boss.y)
    if boss_dist <= self.attack_range:
        targets.append(('boss', boss_dist, boss))
    
    # Aggiungi le torrette come target possibili
    for turret in boss.turrets:
        if turret.hp > 0:
            turret_dist = math.hypot(self.x - turret.x, self.y - turret.y)
            if turret_dist <= self.attack_range:
                targets.append(('turret', turret_dist, turret))
    
    if not targets:
        return False
    
    # Attacca il target più vicino
    target_type, _, target = min(targets, key=lambda x: x[1])
    
    if target_type == 'boss':
        target.hp = max(0, target.hp - self.attack_damage)
    elif target_type == 'turret':
        target.take_damage(self.attack_damage)
    
    return True

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 400
        self.hp = self.max_hp
        self.radius = 50
        self.speed = 2
        self.color = RED
        self.movement_timer = 0
        self.direction = 0

        self.attack_range = 120
        self.attack_damage = 20
        self.dash_speed = 8
        self.dash_duration = 20
        self.dash_cooldown = 120
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown_timer = 0
        self.attack_direction_x = 0
        self.attack_direction_y = 0

    def update(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)

        if not self.is_attacking:
            self.movement_timer += 1
            if self.movement_timer % 60 == 0:
                if distance > 0:
                    self.direction = math.atan2(dy, dx)

            if distance <= self.attack_range and self.attack_cooldown_timer <= 0:
                self.start_attack(dx, dy, distance)
            else:
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed
        else:
            self.x += self.attack_direction_x * self.dash_speed
            self.y += self.attack_direction_y * self.dash_speed

        self.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.y))

    def start_attack(self, dx, dy, distance):
        self.is_attacking = True
        self.attack_timer = self.dash_duration
        self.attack_cooldown_timer = self.dash_cooldown
        if distance > 0:
            self.attack_direction_x = dx / distance
            self.attack_direction_y = dy / distance

    def draw(self, screen):
        color = (255, 100, 100) if self.is_attacking else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

        eye_offset = self.radius // 3
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 8)

        eye_color = RED if self.is_attacking else BLACK
        pygame.draw.circle(screen, eye_color, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(screen, eye_color, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)

class Boss2(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = PURPLE
        self.projectiles = []
        self.projectile_cooldown = 40
        self.projectile_timer = 0

    def update(self, player):
        super().update(player)

        if self.projectile_timer > 0:
            self.projectile_timer -= 1
        else:
            self.fire_projectile(player)
            self.projectile_timer = self.projectile_cooldown

        for proj in self.projectiles:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']

        self.projectiles = [p for p in self.projectiles if 0 < p['x'] < WINDOW_WIDTH and 0 < p['y'] < WINDOW_HEIGHT]

    def fire_projectile(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            speed = 6
            self.projectiles.append({
                'x': self.x,
                'y': self.y,
                'dx': dx / dist * speed,
                'dy': dy / dist * speed
            })

    def draw(self, screen):
        super().draw(screen)
        for p in self.projectiles:
            pygame.draw.circle(screen, YELLOW, (int(p['x']), int(p['y'])), 5)

class Boss3(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = YELLOW
        self.teleport_cooldown = 180  # Frames tra i teletrasporti
        self.teleport_timer = 0

        # Parametri ascia rotante
        self.axe_angle = 0  # angolo iniziale in radianti
        self.axe_distance = self.radius + 50  # distanza dal centro boss
        self.axe_radius = 15  # dimensione ascia
        self.axe_speed = 0.1  # velocità rotazione (radianti per frame)

        self.damage_cooldown = 30  # immunità dopo danno
        self.damage_timer = 0

    def update(self, player):

        super().update(player)

        # Aggiorna angolo ascia per rotazione
        self.axe_angle += self.axe_speed
        if self.axe_angle > 2 * math.pi:
            self.axe_angle -= 2 * math.pi

        # Posizione ascia
        axe_x = self.x + math.cos(self.axe_angle) * self.axe_distance
        axe_y = self.y + math.sin(self.axe_angle) * self.axe_distance

        # Timer danno immunità
        if self.damage_timer > 0:
            self.damage_timer -= 1

        # Controllo collisione ascia-player
        dist = math.hypot(player.x - axe_x, player.y - axe_y)
        if dist < player.radius + self.axe_radius and self.damage_timer <= 0:
            player.hp = max(0, player.hp - 20)  # danno ascia
            self.damage_timer = self.damage_cooldown

    def draw(self, screen):
       # Disegna il boss (con lampeggio teletrasporto)
       if self.teleport_timer < 30:
           color = (255, 255, 150)
       else:
           color = self.color
       pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

       # Occhi rossi fissi
       eye_offset = self.radius // 3
       pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 8)
       pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 8)
       pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
       pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)

       # Disegna l’ascia rotante come rettangolo ruotato
       axe_x = self.x + math.cos(self.axe_angle) * self.axe_distance
       axe_y = self.y + math.sin(self.axe_angle) * self.axe_distance

       axe_width = 10
       axe_height = 40

       # Calcola i punti del rettangolo ruotato
       angle = self.axe_angle
       cos_a = math.cos(angle)
       sin_a = math.sin(angle)

       points = []
       # Rettangolo centrato in (axe_x, axe_y)
       for dx, dy in [(-axe_width/2, -axe_height/2), (axe_width/2, -axe_height/2), 
                      (axe_width/2, axe_height/2), (-axe_width/2, axe_height/2)]:
           x = axe_x + dx * cos_a - dy * sin_a
           y = axe_y + dx * sin_a + dy * cos_a
           points.append((int(x), int(y)))

       pygame.draw.polygon(screen, DARK_RED, points)

class Boss4(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0, 255, 255)
        self.splash_cooldown = 300  # ogni 10 secondi
        self.splash_timer = self.splash_cooldown
        self.splash_charging = False
        self.splash_charge_time = 60  # si ferma per 1 secondo
        self.splash_charge_counter = 0
        self.splash_projectiles = []

        self.minions = []
        self.minion_spawn_on_dash = True

    def update(self, player):
        # Splash Attack
        if self.splash_charging:
            self.splash_charge_counter += 1
            if self.splash_charge_counter >= self.splash_charge_time:
                self.perform_splash_attack()
                self.splash_charging = False
                self.splash_timer = self.splash_cooldown
        else:
            self.splash_timer -= 1
            if self.splash_timer <= 0:
                self.splash_charging = True
                self.splash_charge_counter = 0

        # Dash logic (copiato e modificato)
        if not self.is_attacking and self.attack_cooldown_timer <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist <= self.attack_range:
                self.start_attack(dx, dy, dist)
                self.spawn_minion()

        super().update(player)  # Boss base movement/attack

        # Aggiorna splash proiettili
        for p in self.splash_projectiles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1

            if p['x'] <= 0 or p['x'] >= WINDOW_WIDTH:
                p['dx'] *= -1
            if p['y'] <= 0 or p['y'] >= WINDOW_HEIGHT:
                p['dy'] *= -1

        self.splash_projectiles = [p for p in self.splash_projectiles if p['life'] > 0]

        # Collisione splash
        for p in self.splash_projectiles:
            if math.hypot(player.x - p['x'], player.y - p['y']) < player.radius + 5:
                player.hp = max(0, player.hp - 8)

        # Aggiorna minion
        for m in self.minions:
            m.update(player)

    def perform_splash_attack(self):
        angle_offsets = [0, math.pi / 3, -math.pi / 3]
        for base_angle in angle_offsets:
            for i in range(15): 
                angle = base_angle + i * (2 * math.pi / 24)
                speed = 5
                self.splash_projectiles.append({
                    'x': self.x,
                    'y': self.y,
                    'dx': math.cos(angle) * speed,
                    'dy': math.sin(angle) * speed,
                    'life': 240
                })

    def spawn_minion(self):
        if len(self.minions) < 50:  # Limite massimo
            mx = self.x + random.randint(-50, 50)
            my = self.y + random.randint(-50, 50)
            self.minions.append(Minion(mx, my))

    def draw(self, screen):
        color = (0, 150, 150) if self.splash_charging else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

        eye_offset = self.radius // 3
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)

        for p in self.splash_projectiles:
            pygame.draw.circle(screen, GREEN, (int(p['x']), int(p['y'])), 5)

        for m in self.minions:
            m.draw(screen)

class Minion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.color = DARK_GREEN
        self.hp = 30
        self.speed = 1.5
        self.projectiles = []
        self.shoot_cooldown = 120
        self.shoot_timer = 0

    def update(self, player):
        if self.hp <= 0:
            return

        # Movimento verso il player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

        # Sparo
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.fire(player)
            self.shoot_timer = self.shoot_cooldown

        # Proiettili
        for p in self.projectiles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['life'] -= 1
            if p['x'] <= 0 or p['x'] >= WINDOW_WIDTH:
                p['dx'] *= -1
            if p['y'] <= 0 or p['y'] >= WINDOW_HEIGHT:
                p['dy'] *= -1

        self.projectiles = [p for p in self.projectiles if p['life'] > 0]

        # Collisione con player
        for p in self.projectiles:
            if math.hypot(player.x - p['x'], player.y - p['y']) < player.radius + 5:
                player.hp = max(0, player.hp - 3)
                p['life'] = 0  # rimuovi proiettile

    def fire(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        speed = 4
        self.projectiles.append({
            'x': self.x,
            'y': self.y,
            'dx': dx / dist * speed,
            'dy': dy / dist * speed,
            'life': 240
        })

    def draw(self, screen):
        if self.hp <= 0:
            return
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        for p in self.projectiles:
            pygame.draw.circle(screen, GREEN, (int(p['x']), int(p['y'])), 4)

class Boss5(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 100, 255)  # Magenta
        self.max_hp = 500
        self.hp = self.max_hp
        
        # Meccanica shapeshifting
        self.form = "normal"  # normal, giant, split, ghost
        self.form_timer = 0
        self.form_cooldown = 240  # 4 secondi
        
        # Forma Giant
        self.giant_radius = 80
        self.giant_damage = 35
        self.giant_speed = 1
        
        # Forma Split - cloni
        self.clones = []
        self.max_clones = 3
        
        # Forma Ghost - attraversa i muri e si teletrasporta
        self.ghost_alpha = 128
        self.teleport_timer = 0
        self.teleport_interval = 90  # ogni 1.5 secondi in forma ghost
        
        # Attacco speciale - laser rotante
        self.laser_active = False
        self.laser_angle = 0
        self.laser_duration = 120
        self.laser_timer = 0
        self.laser_cooldown = 360
        self.laser_cooldown_timer = 0
        
        # Timer per cambio forma automatico
        self.form_change_timer = 120  # 2 secondi a 60 FPS

    def take_damage(self, damage):
        """Override del metodo per tracciare i danni"""
        self.hp = max(0, self.hp - damage)

    def change_form(self):
        """Cambia forma del boss"""
        forms = ["normal", "giant", "split", "ghost"]
        # Rimuovi la forma attuale dalle opzioni
        available_forms = [f for f in forms if f != self.form]
        self.form = random.choice(available_forms)
        self.form_timer = self.form_cooldown
        
        if self.form == "split":
            self.create_clones()
        elif self.form == "normal":
            self.clones = []  # Rimuovi cloni quando torna normale
        
    def create_clones(self):
        """Crea cloni per la forma split"""
        self.clones = []
        for i in range(self.max_clones):
            angle = i * (2 * math.pi / self.max_clones)
            clone_x = self.x + math.cos(angle) * 100
            clone_y = self.y + math.sin(angle) * 100
            # Mantieni i cloni dentro i bordi
            clone_x = max(30, min(WINDOW_WIDTH - 30, clone_x))
            clone_y = max(30, min(WINDOW_HEIGHT - 30, clone_y))
            self.clones.append({
                'x': clone_x,
                'y': clone_y,
                'radius': 25,
                'hp': 50,
                'speed': 3,
                'color': (200, 50, 200)
            })

    def update(self, player):
        # Timer cambio forma automatico
        self.form_change_timer -= 1
        if self.form_change_timer <= 0:
            self.change_form()
            self.form_change_timer = 120  # Reset timer (2 secondi)
        
        # Timer forma
        if self.form_timer > 0:
            self.form_timer -= 1
            
        # Timer laser
        if self.laser_cooldown_timer > 0:
            self.laser_cooldown_timer -= 1
        elif not self.laser_active and self.form == "normal":
            self.laser_active = True
            self.laser_timer = self.laser_duration
            self.laser_cooldown_timer = self.laser_cooldown
            
        if self.laser_active:
            self.laser_timer -= 1
            self.laser_angle += 0.05  # Rotazione laser
            if self.laser_timer <= 0:
                self.laser_active = False
                
        # Comportamento basato sulla forma
        if self.form == "normal":
            self.update_normal_form(player)
        elif self.form == "giant":
            self.update_giant_form(player)
        elif self.form == "split":
            self.update_split_form(player)
        elif self.form == "ghost":
            self.update_ghost_form(player)
            
       
        if self.form != "ghost":
            current_radius = self.giant_radius if self.form == "giant" else self.radius
            self.x = max(current_radius, min(WINDOW_WIDTH - current_radius, self.x))
            self.y = max(current_radius, min(WINDOW_HEIGHT - current_radius, self.y))

    def update_normal_form(self, player):
        """Comportamento forma normale + laser"""
        # Movimento base verso il player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
            
        # Controllo collisione laser con player
        if self.laser_active:
            self.check_laser_collision(player)

    def update_giant_form(self, player):
        """Forma gigante - più lenta ma più potente"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.x += dx / distance * self.giant_speed
            self.y += dy / distance * self.giant_speed

    def update_split_form(self, player):
        """Forma divisa - aggiorna cloni"""
        # Il boss principale si muove normalmente
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
            
        # Aggiorna cloni
        for clone in self.clones:
            if clone['hp'] > 0:
                dx = player.x - clone['x']
                dy = player.y - clone['y']
                distance = math.hypot(dx, dy)
                
                if distance > 0:
                    clone['x'] += dx / distance * clone['speed']
                    clone['y'] += dy / distance * clone['speed']
                    
                # Mantieni cloni nei bordi
                clone['x'] = max(clone['radius'], min(WINDOW_WIDTH - clone['radius'], clone['x']))
                clone['y'] = max(clone['radius'], min(WINDOW_HEIGHT - clone['radius'], clone['y']))

    def update_ghost_form(self, player):
        """Forma fantasma - teletrasporto e movimento attraverso muri"""
        self.teleport_timer -= 1
        
        if self.teleport_timer <= 0:
            # Teletrasporto casuale
            self.x = random.randint(self.radius, WINDOW_WIDTH - self.radius)
            self.y = random.randint(self.radius, WINDOW_HEIGHT - self.radius)
            self.teleport_timer = self.teleport_interval
        else:
            # Movimento normale verso player
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.hypot(dx, dy)
            
            if distance > 0:
                self.x += dx / distance * (self.speed * 1.5)  # Più veloce in forma ghost
                self.y += dy / distance * (self.speed * 1.5)

    def check_laser_collision(self, player):
        """Controlla se il laser colpisce il player"""
        # Il laser è una linea dal centro del boss
        laser_length = 300
        laser_end_x = self.x + math.cos(self.laser_angle) * laser_length
        laser_end_y = self.y + math.sin(self.laser_angle) * laser_length
        
        # Distanza punto-linea per controllare collisione
        # Semplificazione: controlla se il player è vicino alla linea del laser
        player_distance = self.point_to_line_distance(
            player.x, player.y, self.x, self.y, laser_end_x, laser_end_y
        )
        
        if player_distance < player.radius + 5:  # 5 pixel di tolleranza
            # Controlla che il player sia effettivamente sulla linea del laser
            laser_dir_x = laser_end_x - self.x
            laser_dir_y = laser_end_y - self.y
            to_player_x = player.x - self.x
            to_player_y = player.y - self.y
            
            # Proiezione del vettore player sulla direzione laser
            projection = (to_player_x * laser_dir_x + to_player_y * laser_dir_y) / (laser_dir_x * laser_dir_x + laser_dir_y * laser_dir_y)
            
            if 0 <= projection <= 1:  # Player è sulla linea del laser
                player.hp = max(0, player.hp - 25)

    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calcola distanza da punto a linea"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return math.hypot(A, B)
            
        param = dot / len_sq
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
            
        dx = px - xx
        dy = py - yy
        return math.hypot(dx, dy)

    def check_collision_with_player(self, player):
        """Controlla collisioni con il player"""
        # Boss principale
        current_radius = self.giant_radius if self.form == "giant" else self.radius
        distance = math.hypot(player.x - self.x, player.y - self.y)
        
        if distance < player.radius + current_radius:
            if self.form == "giant":
                return self.giant_damage
            else:
                return 20
                
        # Cloni (solo in forma split)
        if self.form == "split":
            for clone in self.clones:
                if clone['hp'] > 0:
                    distance = math.hypot(player.x - clone['x'], player.y - clone['y'])
                    if distance < player.radius + clone['radius']:
                        return 15
                        
        return 0

    def take_attack_damage(self, damage):
        """Gestisce i danni degli attacchi del player"""
        if self.form == "split":
            # In forma split, attacca il clone più vicino al player se è nel range
            closest_clone = None
            min_distance = float('inf')
            
            for clone in self.clones:
                if clone['hp'] > 0:
                    distance = math.hypot(Player.x - clone['x'], Player.y - clone['y'])
                    if distance < min_distance:
                        min_distance = distance
                        closest_clone = clone
                        
            # Se c'è un clone nel range di attacco, colpisci quello
            if closest_clone and min_distance <= 130:  # range attacco player
                closest_clone['hp'] = max(0, closest_clone['hp'] - damage)
                return True
                
        # Altrimenti colpisci il boss principale
        self.take_damage(damage)
        return True

    def draw(self, screen):
        """Disegna il boss in base alla forma"""
        if self.form == "normal":
            self.draw_normal_form(screen)
        elif self.form == "giant":
            self.draw_giant_form(screen)
        elif self.form == "split":
            self.draw_split_form(screen)
        elif self.form == "ghost":
            self.draw_ghost_form(screen)
            
    def draw_normal_form(self, screen):
        """Disegna forma normale"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Occhi
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)
        
        # Laser rotante
        if self.laser_active:
            laser_length = 300
            laser_end_x = self.x + math.cos(self.laser_angle) * laser_length
            laser_end_y = self.y + math.sin(self.laser_angle) * laser_length
            pygame.draw.line(screen, (255, 255, 0), (int(self.x), int(self.y)), (int(laser_end_x), int(laser_end_y)), 4)

    def draw_giant_form(self, screen):
        """Disegna forma gigante"""
        pygame.draw.circle(screen, (255, 50, 50), (int(self.x), int(self.y)), self.giant_radius)
        
        # Occhi più grandi
        eye_offset = self.giant_radius // 3
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 12)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 12)
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(self.y - eye_offset)), 6)
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(self.y - eye_offset)), 6)

    def draw_split_form(self, screen):
        """Disegna forma divisa con cloni"""
        # Boss principale (più piccolo)
        pygame.draw.circle(screen, (200, 100, 255), (int(self.x), int(self.y)), self.radius - 10)
        
        # Cloni
        for clone in self.clones:
            if clone['hp'] > 0:
                pygame.draw.circle(screen, clone['color'], (int(clone['x']), int(clone['y'])), clone['radius'])
                # Piccoli occhi per i cloni
                pygame.draw.circle(screen, WHITE, (int(clone['x'] - 5), int(clone['y'] - 5)), 3)
                pygame.draw.circle(screen, WHITE, (int(clone['x'] + 5), int(clone['y'] - 5)), 3)

    def draw_ghost_form(self, screen):
        """Disegna forma fantasma (semi-trasparente)"""
        # Crea una superficie trasparente
        ghost_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        ghost_surface.set_alpha(128)  # Semi-trasparente
        ghost_surface.fill((100, 100, 255))
        
        # Disegna cerchio sulla superficie trasparente
        pygame.draw.circle(ghost_surface, (150, 150, 255), (self.radius, self.radius), self.radius)
        
        # Blit sulla schermata principale
        screen.blit(ghost_surface, (int(self.x - self.radius), int(self.y - self.radius)))
        
        # Occhi sempre visibili
        pygame.draw.circle(screen, WHITE, (int(self.x - 10), int(self.y - 10)), 6)
        pygame.draw.circle(screen, WHITE, (int(self.x + 10), int(self.y - 10)), 6)
        pygame.draw.circle(screen, (0, 255, 255), (int(self.x - 10), int(self.y - 10)), 3)
        pygame.draw.circle(screen, (0, 255, 255), (int(self.x + 10), int(self.y - 10)), 3)

class Boss6(Boss):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (255, 165, 0)  # Arancione
        self.max_hp = 600
        self.hp = self.max_hp
        
        # Torrette
        self.turrets = []
        self.max_turrets = 5
        self.turret_spawn_cooldown = 180  # 3 secondi
        self.turret_spawn_timer = 0
        
        # Bombe ad area
        self.bombs = []
        self.bomb_cooldown = 120  # 2 secondi
        self.bomb_timer = 0
        self.bomb_explosion_radius = 80
        self.bomb_fuse_time = 120  # 2 secondi prima dell'esplosione
        self.bomb_damage = 30
        
        # Cura dalle torrette
        self.heal_cooldown = 60  # 1 secondo
        self.heal_timer = 0
        self.heal_amount = 3  # HP per torrette per secondo
        
        # Spawn iniziale delle torrette
        self.spawn_initial_turrets()
    
    def spawn_initial_turrets(self):
        """Spawna le torrette iniziali"""
        for _ in range(self.max_turrets):
            self.spawn_turret()
    
    def spawn_turret(self):
        """Spawna una nuova torretta in posizione casuale"""
        if len(self.turrets) >= self.max_turrets:
            return
            
        # Trova una posizione valida (non troppo vicina al boss o al player)
        attempts = 0
        while attempts < 20:  # Massimo 20 tentativi
            x = random.randint(50, WINDOW_WIDTH - 50)
            y = random.randint(50, WINDOW_HEIGHT - 50)
            
            # Controlla distanza dal boss
            boss_dist = math.hypot(x - self.x, y - self.y)
            if boss_dist > 100:  # Almeno 100 pixel dal boss
                self.turrets.append(Turret(x, y))
                break
            attempts += 1
    
    def update(self, player):
        # Eredita il comportamento base del boss
        super().update(player)
        
        # Timer per spawnare nuove torrette
        if len(self.turrets) < self.max_turrets:
            self.turret_spawn_timer -= 1
            if self.turret_spawn_timer <= 0:
                self.spawn_turret()
                self.turret_spawn_timer = self.turret_spawn_cooldown
        
        # Timer per lanciare bombe
        self.bomb_timer -= 1
        if self.bomb_timer <= 0:
            self.launch_bomb(player)
            self.bomb_timer = self.bomb_cooldown
        
        # Timer per cura dalle torrette
        self.heal_timer -= 1
        if self.heal_timer <= 0:
            self.heal_from_turrets()
            self.heal_timer = self.heal_cooldown
        
        # Aggiorna torrette
        for turret in self.turrets:
            turret.update(player)
        
        # Rimuovi torrette distrutte
        self.turrets = [t for t in self.turrets if t.hp > 0]
        
        # Aggiorna bombe
        for bomb in self.bombs:
            bomb['fuse_timer'] -= 1
            if bomb['fuse_timer'] <= 0:
                # Esplode: controlla se colpisce il player
                dist = math.hypot(player.x - bomb['x'], player.y - bomb['y'])
                if dist <= self.bomb_explosion_radius:
                    player.hp = max(0, player.hp - self.bomb_damage)
                bomb['exploded'] = True
        
        # Rimuovi bombe esplose
        self.bombs = [b for b in self.bombs if not b.get('exploded', False)]
    
    def launch_bomb(self, player):
        """Lancia una bomba verso la posizione del player"""
        # Predici dove sarà il player (semplice previsione)
        prediction_time = 60  # 1 secondo
        predicted_x = player.x
        predicted_y = player.y
        
        # Se il player si sta muovendo, predici la posizione
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            predicted_y -= player.speed * prediction_time
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            predicted_y += player.speed * prediction_time
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            predicted_x -= player.speed * prediction_time
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            predicted_x += player.speed * prediction_time
        
        # Mantieni la previsione nei bordi
        predicted_x = max(50, min(WINDOW_WIDTH - 50, predicted_x))
        predicted_y = max(50, min(WINDOW_HEIGHT - 50, predicted_y))
        
        self.bombs.append({
            'x': predicted_x,
            'y': predicted_y,
            'fuse_timer': self.bomb_fuse_time,
            'exploded': False
        })
    
    def heal_from_turrets(self):
        """Cura il boss in base al numero di torrette attive"""
        active_turrets = len([t for t in self.turrets if t.hp > 0])
        if active_turrets > 0 and self.hp < self.max_hp:
            heal_amount = active_turrets * self.heal_amount
            self.hp = min(self.max_hp, self.hp + heal_amount)
    
    def take_player_attack(self, player, damage):
        """Gestisce l'attacco del player - può colpire boss o torrette"""
        # Trova il target più vicino nel range di attacco
        targets = []
        
        # Aggiungi il boss come target
        boss_dist = math.hypot(player.x - self.x, player.y - self.y)
        if boss_dist <= player.attack_range:
            targets.append(('boss', boss_dist, self))
        
        # Aggiungi le torrette come target
        for turret in self.turrets:
            if turret.hp > 0:
                turret_dist = math.hypot(player.x - turret.x, player.y - turret.y)
                if turret_dist <= player.attack_range:
                    targets.append(('turret', turret_dist, turret))
        
        if not targets:
            return False
        
        # Colpisci il target più vicino
        target_type, _, target = min(targets, key=lambda x: x[1])
        
        if target_type == 'boss':
            self.hp = max(0, self.hp - damage)
        elif target_type == 'turret':
            target.hp = max(0, target.hp - damage)
        
        return True
    
    def draw(self, screen):
        # Disegna il boss principale
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Occhi
        eye_offset = self.radius // 3
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset), int(self.y - eye_offset)), 8)
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(self.y - eye_offset)), 4)
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(self.y - eye_offset)), 4)
        
        # Disegna torrette
        for turret in self.turrets:
            if turret.hp > 0:
                turret.draw(screen)
        
        # Disegna bombe (con area di esplosione)
        for bomb in self.bombs:
            if not bomb.get('exploded', False):
                # Bomba (cerchio nero)
                pygame.draw.circle(screen, BLACK, (int(bomb['x']), int(bomb['y'])), 15)
                
                # Area di esplosione (cerchio rosso trasparente)
                # Calcola l'alpha in base al tempo rimanente
                alpha = max(70, int(150 * (1 - bomb['fuse_timer'] / self.bomb_fuse_time)))
                
                # Crea superficie trasparente per l'area
                bomb_surface = pygame.Surface((self.bomb_explosion_radius * 2, self.bomb_explosion_radius * 2))
                bomb_surface.set_alpha(alpha)
                bomb_surface.fill((255, 0, 0))
                
                # Disegna cerchio dell'area
                pygame.draw.circle(bomb_surface, (255, 100, 100), 
                                 (self.bomb_explosion_radius, self.bomb_explosion_radius), 
                                 self.bomb_explosion_radius)
                
                # Blit sulla schermata
                screen.blit(bomb_surface, 
                           (int(bomb['x'] - self.bomb_explosion_radius), 
                            int(bomb['y'] - self.bomb_explosion_radius)))
                
                # Timer visivo sulla bomba
                time_left = bomb['fuse_timer'] / 60.0  # Secondi
                font = pygame.font.Font(None, 20)
                timer_text = font.render(f"{time_left:.1f}", True, WHITE)
                screen.blit(timer_text, (int(bomb['x'] - 10), int(bomb['y'] - 20)))

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 75
        self.max_hp = 75
        self.radius = 25
        self.color = (100, 100, 100)  # Grigio
        
        # Attacco a raffica
        self.projectiles = []
        self.burst_cooldown = 180  # 3 secondi tra le raffiche
        self.burst_timer = 0
        self.shots_per_burst = 5
        self.shot_delay = 8  # Delay tra i colpi della raffica
        self.burst_active = False
        self.burst_shots_fired = 0
        self.burst_shot_timer = 0
        
        self.range = 200
        self.projectile_speed = 4
        self.projectile_damage = 8
    
    def update(self, player):
        if self.hp <= 0:
            return
        
        # Controlla se il player è nel range
        dist = math.hypot(player.x - self.x, player.y - self.y)
        
        if dist <= self.range:
            # Timer per iniziare nuova raffica
            if not self.burst_active:
                self.burst_timer -= 1
                if self.burst_timer <= 0:
                    self.burst_active = True
                    self.burst_shots_fired = 0
                    self.burst_shot_timer = 0
            else:
                # Gestione raffica attiva
                self.burst_shot_timer -= 1
                if self.burst_shot_timer <= 0 and self.burst_shots_fired < self.shots_per_burst:
                    self.fire_at_player(player)
                    self.burst_shots_fired += 1
                    self.burst_shot_timer = self.shot_delay
                
                # Fine raffica
                if self.burst_shots_fired >= self.shots_per_burst:
                    self.burst_active = False
                    self.burst_timer = self.burst_cooldown
        
        # Aggiorna proiettili
        for proj in self.projectiles:
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            proj['life'] -= 1
            
            # Rimbalzo sui bordi
            if proj['x'] <= 0 or proj['x'] >= WINDOW_WIDTH:
                proj['dx'] *= -1
            if proj['y'] <= 0 or proj['y'] >= WINDOW_HEIGHT:
                proj['dy'] *= -1
        
        # Rimuovi proiettili scaduti
        self.projectiles = [p for p in self.projectiles if p['life'] > 0]
        
        # Controlla collisioni con player
        for proj in self.projectiles:
            dist = math.hypot(player.x - proj['x'], player.y - proj['y'])
            if dist <= player.radius + 3:
                player.hp = max(0, player.hp - self.projectile_damage)
                proj['life'] = 0  # Rimuovi proiettile
    
    def take_damage(self, damage):
        """Riceve danno dal player"""
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0  # Ritorna True se è distrutta

    def fire_at_player(self, player):
        """Spara un proiettile verso il player"""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist
        self.projectiles.append({
            'x': self.x,
            'y': self.y,
            'dx': dx * self.projectile_speed,
            'dy': dy * self.projectile_speed,
            'life': 300  # 5 secondi
        })
    
    def draw(self, screen):
        if self.hp <= 0:
            return
        
        # Corpo torrette
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Barra HP della torrette
        bar_width = 40
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 10
        
        # Sfondo barra
        pygame.draw.rect(screen, BLACK, (int(bar_x - 1), int(bar_y - 1), bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_RED, (int(bar_x), int(bar_y), bar_width, bar_height))
        
        # HP attuale
        hp_percentage = self.hp / self.max_hp
        current_width = int(bar_width * hp_percentage)
        pygame.draw.rect(screen, GREEN, (int(bar_x), int(bar_y), current_width, bar_height))
        
        # Indicatore se sta sparando
        if self.burst_active:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y - self.radius // 2)), 5)
        
        # Range di attacco (opzionale - mostra solo per debug)
        # pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.range, 1)
        
        # Proiettili
        for proj in self.projectiles:
            pygame.draw.circle(screen, YELLOW, (int(proj['x']), int(proj['y'])), 3)

class HealthBar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen, current_hp, max_hp, label=""):
        hp_percentage = max(0, current_hp / max_hp)
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, self.width + 4, self.height + 4))
        pygame.draw.rect(screen, DARK_RED, (self.x, self.y, self.width, self.height))
        health_width = int(self.width * hp_percentage)
        pygame.draw.rect(screen, GREEN, (self.x, self.y, health_width, self.height))

        font = pygame.font.Font(None, 24)
        hp_text = f"{int(current_hp)}/{int(max_hp)}"
        text_surface = font.render(hp_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

        if label:
            label_surface = font.render(label, True, WHITE)
            label_rect = label_surface.get_rect(center=(self.x + self.width // 2, self.y - 20))
            screen.blit(label_surface, label_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Boss Run RPG")
        self.clock = pygame.time.Clock()
        self.level = 1
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.load_level(self.level)
        self.running = True
        self.damage_timer = 0
        self.game_state = "playing"

    def load_level(self, level):
       if level == 1:
           self.boss = Boss(WINDOW_WIDTH // 2, 150)
       elif level == 2:
           self.boss = Boss2(WINDOW_WIDTH // 2, 150)
       elif level == 3:
           self.boss = Boss3(WINDOW_WIDTH // 2, 150)
       elif level == 4:
           self.boss = Boss4(WINDOW_WIDTH // 2, 150)
       elif level == 5:
           self.boss = Boss5(WINDOW_WIDTH // 2, 150)
       elif level == 6:  # AGGIUNGI QUESTA PARTE
           self.boss = Boss6(WINDOW_WIDTH // 2, 150)

       self.boss_health_bar = HealthBar(WINDOW_WIDTH // 2 - 150, 20, 300, 30)
       self.player_health_bar = HealthBar(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 60, 200, 25)


    def restart_game(self):
       self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
       self.load_level(self.level)
       self.running = True
       self.damage_timer = 0
       self.game_state = "playing"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.game_state == "playing":
                    if event.key == pygame.K_k:
                        # MODIFICA QUI: attacco Boss6 e torrette
                        if isinstance(self.boss, Boss6):
                            self.boss.take_player_attack(self.player, self.player.attack_damage)
                        else:
                            self.player.attack(self.boss)
                    elif event.key == pygame.K_SPACE:
                        self.player.dash()
                elif self.game_state in ["player_dead", "boss_dead"]:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        self.running = False

    def update(self):
        if self.game_state != "playing":
            return

        keys = pygame.key.get_pressed()
        if self.damage_timer > 0:
            self.damage_timer -= 1
        self.player.update(keys)
        self.boss.update(self.player)

        # Gestione danni da proiettili Boss2
        if isinstance(self.boss, Boss2):
            for proj in self.boss.projectiles:
                dist = math.hypot(self.player.x - proj['x'], self.player.y - proj['y'])
                if dist < self.player.radius + 5 and self.damage_timer <= 0:
                    self.player.hp = max(0, self.player.hp - 10)
                    self.damage_timer = 30
        
        if isinstance(self.boss, Boss5):
        # Boss5 ha il suo metodo di gestione collisioni
            damage = self.boss.check_collision_with_player(self.player)
            if damage > 0 and not self.player.is_dashing and self.damage_timer <= 0:
                self.player.hp = max(0, self.player.hp - damage)
                self.damage_timer = 30

        if self.boss.hp <= 0:
            if self.level < 6:
                self.level += 1
                self.load_level(self.level)
                self.player.hp = self.player.max_hp
            else:
                self.game_state = "boss_dead"
            return



        if self.player.hp <= 0:
            self.game_state = "player_dead"
            return

        distance = math.hypot(self.player.x - self.boss.x, self.player.y - self.boss.y)
        if distance < self.player.radius + self.boss.radius:
            if not self.player.is_dashing and self.damage_timer <= 0:
                damage = self.boss.attack_damage if self.boss.is_attacking else 15
                self.player.hp = max(0, self.player.hp - damage)
                self.damage_timer = 30

    def draw(self):
        self.screen.fill(DARK_GRAY)
        grid_size = 50
        for x in range(0, WINDOW_WIDTH, grid_size):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, grid_size):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)

        self.boss.draw(self.screen)
        self.player.draw(self.screen)

        if self.player.can_attack(self.boss):
            pygame.draw.circle(self.screen, GREEN, (int(self.player.x), int(self.player.y)), self.player.attack_range, 2)
        else:
            pygame.draw.circle(self.screen, RED, (int(self.player.x), int(self.player.y)), self.player.attack_range, 1)

        self.boss_health_bar.draw(self.screen, self.boss.hp, self.boss.max_hp, "BOSS")
        self.player_health_bar.draw(self.screen, self.player.hp, self.player.max_hp, "PLAYER")

        if self.player.dash_cooldown_timer > 0:
            cooldown_rect = pygame.Rect(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 90,
                                        int(200 * (self.player.dash_cooldown_timer / self.player.dash_cooldown)), 10)
            pygame.draw.rect(self.screen, BLUE, cooldown_rect)

        if self.damage_timer > 0:
            immunity_rect = pygame.Rect(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 105,
                                        int(200 * (self.damage_timer / 30)), 8)
            pygame.draw.rect(self.screen, YELLOW, immunity_rect)

        font = pygame.font.Font(None, 24)
        controls = [
            "WASD/Frecce: Movimento",
            "K: Attacco (range limitato)",
            "SPAZIO: Dash evasivo",
            "Toccare il boss o i proiettili = danno!",
            "ESC: Esci"
        ]
        for i, control in enumerate(controls):
            text = font.render(control, True, WHITE)
            self.screen.blit(text, (10, 10 + i * 25))

        if self.game_state == "boss_dead":
            text = font.render("HAI VINTO! Premi R per riprovare o Q per uscire.", True, GREEN)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2))
        elif self.game_state == "player_dead":
            text = font.render("SEI MORTO! Premi R per riprovare o Q per uscire.", True, RED)
            self.screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
