import pygame
import math
import random

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_POWER = -10
GROUND_Y = 500
WORLD_WIDTH = 5000

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
ICE_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (100, 149, 237)
PURPLE = (138, 43, 226)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_GREEN = (0, 100, 0)
DARK_RED = (139, 0, 0)

class ShotgunPellet:
    def __init__(self, x, y, direction, angle_offset=0, damage=10):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 22
        self.damage = damage
        self.angle_offset = angle_offset
        
    def update(self):
        self.x += self.direction * self.speed
        self.y += self.angle_offset * 2.5
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(self.y)), 3)
        pygame.draw.circle(screen, ORANGE, (int(screen_x), int(self.y)), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - 3, self.y - 3, 6, 6)

class GatlingBullet:
    def __init__(self, x, y, direction, angle_offset=0, damage=8):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 18
        self.damage = damage
        self.angle_offset = angle_offset
        
    def update(self):
        self.x += self.direction * self.speed
        self.y += self.angle_offset * 1.5
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if self.direction > 0:
            pygame.draw.line(screen, YELLOW, 
                           (int(screen_x - 5), int(self.y)),
                           (int(screen_x + 5), int(self.y)), 3)
            pygame.draw.circle(screen, ORANGE, (int(screen_x + 3), int(self.y)), 3)
        else:
            pygame.draw.line(screen, YELLOW,
                           (int(screen_x + 5), int(self.y)),
                           (int(screen_x - 5), int(self.y)), 3)
            pygame.draw.circle(screen, ORANGE, (int(screen_x - 3), int(self.y)), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 3, 10, 6)

class TankBullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 20
        self.damage = 100
        self.size = 14
        
    def update(self):
        self.x += self.direction * self.speed
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        pygame.draw.circle(screen, RED, (int(screen_x), int(self.y)), self.size)
        pygame.draw.circle(screen, ORANGE, (int(screen_x), int(self.y)), self.size - 3)
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(self.y)), self.size - 6)
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(self.y)), self.size - 9)
        trail_x = self.x - self.direction * 12 - camera_x
        pygame.draw.circle(screen, ORANGE, (int(trail_x), int(self.y)), self.size - 5)
        pygame.draw.circle(screen, RED, (int(trail_x), int(self.y)), self.size - 8)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class TurretGunner:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 25
        self.shoot_timer = 0
        self.shoot_delay = 4
        self.bullets = []
        self.facing_right = True
        
    def update(self, tank_x, tank_y, tank_facing_right, enemies):
        if tank_facing_right:
            self.x = tank_x + 45
        else:
            self.x = tank_x - 5
        self.y = tank_y - 25
        self.facing_right = tank_facing_right
        
        target = None
        min_dist = 500
        for enemy in enemies:
            dist = abs(enemy.x - self.x)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        
        if self.shoot_timer <= 0 and target:
            direction = 1 if target.x > self.x else -1
            spread = random.uniform(-2, 2)
            bullet_x = self.x + 10 if direction > 0 else self.x - 5
            bullet_y = self.y + 12
            bullet = GatlingBullet(bullet_x, bullet_y, direction, spread, 12)
            self.bullets.append(bullet)
            self.shoot_timer = self.shoot_delay
        else:
            self.shoot_timer -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        pygame.draw.circle(screen, (50, 50, 150), (screen_x + 10, self.y + 10), 8)
        pygame.draw.rect(screen, (50, 50, 150), (screen_x + 5, self.y + 15, 10, 10))
        pygame.draw.rect(screen, DARK_GRAY, (screen_x + 3, self.y + 3, 14, 8))
        
        if self.facing_right:
            pygame.draw.rect(screen, DARK_GRAY, (screen_x + 15, self.y + 12, 20, 6))
            pygame.draw.circle(screen, GRAY, (screen_x + 35, self.y + 15), 5)
            for i in range(3):
                offset = i * 2
                pygame.draw.circle(screen, GRAY, (screen_x + 35 + offset, self.y + 15 + offset % 2), 2)
        else:
            pygame.draw.rect(screen, DARK_GRAY, (screen_x - 10, self.y + 12, 20, 6))
            pygame.draw.circle(screen, GRAY, (screen_x - 10, self.y + 15), 5)
            for i in range(3):
                offset = i * 2
                pygame.draw.circle(screen, GRAY, (screen_x - 10 - offset, self.y + 15 + offset % 2), 2)
        
        if self.shoot_timer > 0 and self.shoot_timer < 3:
            if self.facing_right:
                pygame.draw.circle(screen, ORANGE, (screen_x + 35, self.y + 15), 6)
                pygame.draw.circle(screen, YELLOW, (screen_x + 35, self.y + 15), 3)
            else:
                pygame.draw.circle(screen, ORANGE, (screen_x - 10, self.y + 15), 6)
                pygame.draw.circle(screen, YELLOW, (screen_x - 10, self.y + 15), 3)
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.health = 500000
        self.max_health = 500000
        self.vel_x = 0
        self.speed = 4
        self.facing_right = True
        self.shoot_timer = 0
        self.shoot_delay = 20
        self.bullets = []
        self.exhaust_timer = 0
        self.respawn_timer = 0
        self.heat_timer = 0
        self.heat_damage_timer = 0
        self.gunner = TurretGunner(x + 45, y - 25)
        
    def update(self, platforms, enemies):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return
        
        self.x += self.vel_x
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
        
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + platform.height + 10):
                self.y = platform.y - self.height
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
        
        if self.exhaust_timer > 0:
            self.exhaust_timer -= 1
        
        self.gunner.update(self.x, self.y, self.facing_right, enemies)
        
        if self.vel_x != 0 or self.shoot_timer > 0:
            self.heat_timer = min(60, self.heat_timer + 1)
        else:
            self.heat_timer = max(0, self.heat_timer - 1)
        
        if self.heat_timer > 0:
            self.heat_damage_timer += 1
        else:
            self.heat_damage_timer = 0
    
    def get_heat_level(self):
        if self.heat_timer > 50:
            return 3
        elif self.heat_timer > 30:
            return 2
        elif self.heat_timer > 10:
            return 1
        return 0
    
    def get_heat_damage(self):
        if self.heat_damage_timer >= 30:
            self.heat_damage_timer = 0
            return 30
        return 0
    
    def get_gunner_bullets(self):
        return self.gunner.bullets
    
    def move_left(self):
        self.vel_x = -self.speed
        self.facing_right = False
        self.exhaust_timer = 5
    
    def move_right(self):
        self.vel_x = self.speed
        self.facing_right = True
        self.exhaust_timer = 5
    
    def stop(self):
        self.vel_x = 0
    
    def shoot(self):
        if self.shoot_timer <= 0 and self.respawn_timer == 0:
            bullet_x = self.x + self.width if self.facing_right else self.x
            bullet_y = self.y + self.height // 2
            direction = 1 if self.facing_right else -1
            bullet = TankBullet(bullet_x, bullet_y, direction)
            self.bullets.append(bullet)
            self.shoot_timer = self.shoot_delay
            return True
        return False
    
    def take_damage(self, damage, knockback_dir=None):
        if self.respawn_timer > 0:
            return False
        self.health -= damage
        if self.health <= 0:
            self.start_respawn()
            return True
        return False
    
    def start_respawn(self):
        self.respawn_timer = 180
        self.vel_x = 0
        self.bullets.clear()
        self.heat_timer = 0
        self.gunner.bullets.clear()
    
    def respawn(self):
        self.x = 400
        self.y = GROUND_Y - 40
        self.health = self.max_health
        self.vel_x = 0
        self.facing_right = True
        self.shoot_timer = 0
        self.bullets.clear()
        self.respawn_timer = 0
        self.heat_timer = 0
        self.gunner = TurretGunner(self.x + 45, self.y - 25)
    
    def draw_flag(self, screen, x, y, facing_right, camera_x=0):
        """绘制五星红旗 - 放大版"""
        screen_x = x - camera_x
        if facing_right:
            flag_x = screen_x - 15
        else:
            flag_x = screen_x + self.width + 5
        flag_y = y - 45
        
        pygame.draw.line(screen, (139, 69, 19), (flag_x, flag_y), (flag_x, flag_y + 55), 4)
        pygame.draw.circle(screen, GOLD, (flag_x, flag_y - 2), 4)
        
        if facing_right:
            flag_rect = pygame.Rect(flag_x - 43, flag_y - 3, 45, 30)
        else:
            flag_rect = pygame.Rect(flag_x - 2, flag_y - 3, 45, 30)
        pygame.draw.rect(screen, RED, flag_rect)
        
        center_x = flag_rect.x + 12
        center_y = flag_rect.y + 15
        outer_radius = 10
        inner_radius = 4
        star_points = []
        for i in range(5):
            angle = math.radians(90 - i * 72)
            outer_x = center_x + outer_radius * math.cos(angle)
            outer_y = center_y - outer_radius * math.sin(angle)
            inner_angle = angle + math.radians(36)
            inner_x = center_x + inner_radius * math.cos(inner_angle)
            inner_y = center_y - inner_radius * math.sin(inner_angle)
            star_points.extend([(outer_x, outer_y), (inner_x, inner_y)])
        pygame.draw.polygon(screen, YELLOW, star_points)
        
        small_positions = [(-14, -8), (-4, -12), (-4, 5), (-14, 10)]
        for sx, sy in small_positions:
            scx = flag_rect.x + 32 + sx
            scy = flag_rect.y + 15 + sy
            small_points = []
            for i in range(5):
                angle = math.radians(90 - i * 72)
                ox = scx + 4 * math.cos(angle)
                oy = scy - 4 * math.sin(angle)
                ix = scx + 1.5 * math.cos(angle + math.radians(36))
                iy = scy - 1.5 * math.sin(angle + math.radians(36))
                small_points.extend([(ox, oy), (ix, iy)])
            pygame.draw.polygon(screen, YELLOW, small_points)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        if self.respawn_timer > 0:
            if (self.respawn_timer // 10) % 2 == 0:
                return
        
        heat_level = self.get_heat_level()
        if heat_level == 3:
            color = (255, 50, 0)
        elif heat_level == 2:
            color = (255, 100, 0)
        elif heat_level == 1:
            color = (255, 150, 0)
        else:
            color = DARK_GREEN
        
        pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
        
        pygame.draw.rect(screen, DARK_GRAY, (screen_x - 5, self.y + 5, 5, self.height - 10))
        pygame.draw.rect(screen, DARK_GRAY, (screen_x + self.width, self.y + 5, 5, self.height - 10))
        
        turret_x = screen_x + self.width // 2
        turret_y = self.y - 15
        pygame.draw.circle(screen, DARK_GREEN, (turret_x, turret_y), 18)
        
        if self.facing_right:
            pygame.draw.rect(screen, DARK_GRAY, (turret_x + 5, turret_y - 3, 30, 6))
            pygame.draw.circle(screen, RED, (turret_x + 35, turret_y), 5)
        else:
            pygame.draw.rect(screen, DARK_GRAY, (turret_x - 35, turret_y - 3, 30, 6))
            pygame.draw.circle(screen, RED, (turret_x - 35, turret_y), 5)
        
        if self.exhaust_timer > 0:
            exh_x = screen_x - 10 if self.facing_right else screen_x + self.width + 10
            pygame.draw.circle(screen, GRAY, (exh_x, self.y + self.height - 10), 5)
            pygame.draw.circle(screen, DARK_GRAY, (exh_x, self.y + self.height - 10), 3)
        
        if heat_level > 0:
            for _ in range(heat_level * 2):
                px = screen_x + random.randint(0, self.width)
                py = self.y + random.randint(0, self.height)
                pygame.draw.circle(screen, (255, random.randint(100, 200), 0), (px, py), 2)
        
        bar_width = self.width
        bar_height = 8
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 12, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 12, bar_width * health_percent, bar_height))
        
        self.draw_flag(screen, self.x, self.y, self.facing_right, camera_x)
        
        self.gunner.draw(screen, camera_x)
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class ArrowBullet:
    """僵尸BOSS的弓箭子弹"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 14
        self.damage = 6
        self.size = 6
        
    def update(self):
        self.x += self.direction * self.speed
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        # 箭身
        pygame.draw.line(screen, BROWN, (screen_x - 5, self.y), (screen_x + 5, self.y), 3)
        # 箭头
        if self.direction > 0:
            pygame.draw.polygon(screen, DARK_GRAY, [(screen_x + 5, self.y), (screen_x, self.y - 3), (screen_x, self.y + 3)])
        else:
            pygame.draw.polygon(screen, DARK_GRAY, [(screen_x - 5, self.y), (screen_x, self.y - 3), (screen_x, self.y + 3)])
        # 箭羽
        pygame.draw.line(screen, DARK_GRAY, (screen_x - 8, self.y - 2), (screen_x - 3, self.y), 2)
        pygame.draw.line(screen, DARK_GRAY, (screen_x - 8, self.y + 2), (screen_x - 3, self.y), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 3, 10, 6)

class ZombieBoss:
    """僵尸BOSS - 弓箭手"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.8
        self.width = 45
        self.height = 80
        self.health = 900
        self.max_health = 900
        self.facing_right = False
        self.on_ground = True
        self.frozen = False
        self.frozen_timer = 0
        self.knockback_timer = 0
        self.shoot_timer = 0
        self.shoot_delay = 70
        self.bullets = []
        self.color = (80, 150, 80)
        
    def update(self, player, platforms, tank=None):
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
            return
        
        target = tank if tank and tank.health > 0 and tank.respawn_timer == 0 else player
        dx = target.x - self.x
        dy = target.y - self.y
        
        # 移动
        if abs(dx) > 80:
            self.vel_x = self.speed if dx > 0 else -self.speed
            self.facing_right = dx > 0
        else:
            self.vel_x = 0
        
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + platform.height + 10):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
        
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            self.health = 0
        
        # 射击
        if self.shoot_timer <= 0:
            if abs(dx) < 400:
                direction = 1 if dx > 0 else -1
                bullet = ArrowBullet(
                    self.x + self.width if direction > 0 else self.x,
                    self.y + self.height // 2,
                    direction
                )
                self.bullets.append(bullet)
                self.shoot_timer = self.shoot_delay
        else:
            self.shoot_timer -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0 and not self.frozen:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def freeze(self, duration=60):
        self.frozen = True
        self.frozen_timer = duration
    
    def draw_flag(self, screen, x, y, facing_right, camera_x=0):
        """美国国旗"""
        screen_x = x - camera_x
        if facing_right:
            flag_x = screen_x - 15
        else:
            flag_x = screen_x + self.width - 5
        flag_y = y - 45
        
        pygame.draw.line(screen, BROWN, (flag_x, flag_y), (flag_x, flag_y + 40), 3)
        
        # 国旗矩形
        flag_rect = pygame.Rect(flag_x - 35, flag_y - 3, 40, 25) if facing_right else pygame.Rect(flag_x - 5, flag_y - 3, 40, 25)
        pygame.draw.rect(screen, WHITE, flag_rect)
        # 红色条纹
        for i in range(7):
            if i % 2 == 0:
                stripe_rect = pygame.Rect(flag_rect.x, flag_rect.y + i * 3.6, 40, 1.8)
                pygame.draw.rect(screen, RED, stripe_rect)
        # 蓝色方块
        blue_rect = pygame.Rect(flag_rect.x, flag_rect.y, 16, 13)
        pygame.draw.rect(screen, BLUE, blue_rect)
        # 白色星星（简化：白点）
        for sy in range(3):
            for sx in range(3):
                star_x = blue_rect.x + 3 + sx * 5
                star_y = blue_rect.y + 2 + sy * 4
                pygame.draw.circle(screen, WHITE, (star_x, star_y), 1.5)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        self.draw_flag(screen, self.x, self.y, self.facing_right, camera_x)
        
        color = self.color if self.knockback_timer <= 0 else ORANGE
        if self.frozen:
            color = ICE_BLUE
        
        # 僵尸身体
        pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
        # 头部
        head_x = screen_x + self.width // 2
        head_y = self.y - 20
        pygame.draw.circle(screen, color, (head_x, head_y), 18)
        # 眼睛
        eye_x = head_x + 8 if self.facing_right else head_x - 8
        pygame.draw.circle(screen, RED, (eye_x, head_y - 5), 4)
        pygame.draw.circle(screen, BLACK, (eye_x, head_y - 5), 2)
        # 嘴
        pygame.draw.line(screen, DARK_RED, (head_x - 6, head_y + 5), (head_x + 6, head_y + 5), 3)
        # 僵尸手臂（持弓）
        arm_x = head_x + 25 if self.facing_right else head_x - 25
        pygame.draw.line(screen, color, (head_x, head_y + 15), (arm_x, head_y + 10), 5)
        # 弓
        bow_color = BROWN
        if self.facing_right:
            pygame.draw.arc(screen, bow_color, (arm_x - 10, head_y - 5, 20, 30), 0, math.pi, 4)
        else:
            pygame.draw.arc(screen, bow_color, (arm_x - 10, head_y - 5, 20, 30), 0, math.pi, 4)
        
        # 血条
        bar_width = self.width
        bar_height = 8
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class SniperBullet:
    def __init__(self, x, y, direction, damage=20):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 25
        self.damage = damage
        self.size = 5
        
    def update(self):
        self.x += self.direction * self.speed
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        pygame.draw.line(screen, RED, (screen_x - 5, self.y), (screen_x + 5, self.y), 3)
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(self.y)), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 3, 10, 6)

class SniperEnemy:
    """敌人狙击手 - 背美国国旗"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.5
        self.width = 30
        self.height = 60
        self.health = 60
        self.max_health = 60
        self.facing_right = False
        self.on_ground = True
        self.frozen = False
        self.frozen_timer = 0
        self.knockback_timer = 0
        self.shoot_timer = 0
        self.shoot_delay = 60
        self.bullets = []
        self.color = (100, 200, 100)
        self.attack_damage = 25
        
    def update(self, player, platforms, tank=None):
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
            return
        
        target = tank if tank and tank.health > 0 and tank.respawn_timer == 0 else player
        dx = target.x - self.x
        
        if abs(dx) > 150:
            self.vel_x = self.speed if dx > 0 else -self.speed
            self.facing_right = dx > 0
        elif abs(dx) < 80:
            self.vel_x = -self.speed if dx > 0 else self.speed
            self.facing_right = dx < 0
        else:
            self.vel_x = 0
        
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + platform.height + 10):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
        
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            self.health = 0
        
        if self.shoot_timer <= 0:
            if abs(dx) < 400:
                direction = 1 if dx > 0 else -1
                bullet = SniperBullet(
                    self.x + self.width if direction > 0 else self.x,
                    self.y + self.height // 2,
                    direction, self.attack_damage
                )
                self.bullets.append(bullet)
                self.shoot_timer = self.shoot_delay
        else:
            self.shoot_timer -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0 and not self.frozen:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def freeze(self, duration=60):
        self.frozen = True
        self.frozen_timer = duration
    
    def draw_flag(self, screen, x, y, facing_right, camera_x=0):
        """美国国旗"""
        screen_x = x - camera_x
        if facing_right:
            flag_x = screen_x - 12
        else:
            flag_x = screen_x + self.width - 5
        flag_y = y - 30
        
        pygame.draw.line(screen, BROWN, (flag_x, flag_y), (flag_x, flag_y + 30), 2)
        
        flag_rect = pygame.Rect(flag_x - 28, flag_y - 2, 30, 20) if facing_right else pygame.Rect(flag_x - 2, flag_y - 2, 30, 20)
        pygame.draw.rect(screen, WHITE, flag_rect)
        for i in range(6):
            if i % 2 == 0:
                stripe_rect = pygame.Rect(flag_rect.x, flag_rect.y + i * 3.3, 30, 1.6)
                pygame.draw.rect(screen, RED, stripe_rect)
        blue_rect = pygame.Rect(flag_rect.x, flag_rect.y, 12, 10)
        pygame.draw.rect(screen, BLUE, blue_rect)
        for sy in range(2):
            for sx in range(2):
                star_x = blue_rect.x + 3 + sx * 4
                star_y = blue_rect.y + 2 + sy * 4
                pygame.draw.circle(screen, WHITE, (star_x, star_y), 1)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        self.draw_flag(screen, self.x, self.y, self.facing_right, camera_x)
        
        color = self.color if self.knockback_timer <= 0 else ORANGE
        if self.frozen:
            color = ICE_BLUE
        
        pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
        
        head_x = screen_x + self.width // 2
        head_y = self.y - 15
        pygame.draw.circle(screen, color, (head_x, head_y), 15)
        
        eye_x = head_x + 8 if self.facing_right else head_x - 8
        pygame.draw.circle(screen, BLACK, (eye_x, head_y - 5), 4)
        
        gun_x = head_x + 30 if self.facing_right else head_x - 30
        pygame.draw.line(screen, DARK_GRAY, (head_x, head_y + 12), (gun_x, head_y + 5), 5)
        pygame.draw.rect(screen, DARK_GRAY, (gun_x - 5, head_y + 3, 10, 6))
        pygame.draw.circle(screen, BLUE, (gun_x - 2, head_y + 5), 4)
        pygame.draw.circle(screen, BLACK, (gun_x - 2, head_y + 5), 2)
        
        bar_width = self.width
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 10, bar_width * health_percent, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class SniperAlly:
    """友方狙击手 - 背五星红旗"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 2.5
        self.width = 30
        self.height = 60
        self.health = 150
        self.max_health = 150
        self.facing_right = True
        self.on_ground = True
        self.flying = False
        self.shoot_timer = 0
        self.shoot_delay = 45
        self.bullets = []
        self.color = (50, 150, 50)
        self.knockback_timer = 0
        
    def update(self, platforms, enemies, player, tank=None):
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + platform.height + 10):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
        
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            self.health = 0
        
        if enemies:
            nearest = min(enemies, key=lambda e: abs(e.x - self.x))
            dx = nearest.x - self.x
            
            if abs(dx) > 100:
                self.vel_x = self.speed if dx > 0 else -self.speed
                self.facing_right = dx > 0
            else:
                self.vel_x = 0
            
            if self.shoot_timer <= 0:
                direction = 1 if dx > 0 else -1
                bullet = SniperBullet(
                    self.x + self.width if direction > 0 else self.x,
                    self.y + self.height // 2,
                    direction, 25
                )
                self.bullets.append(bullet)
                self.shoot_timer = self.shoot_delay
            else:
                self.shoot_timer -= 1
        else:
            dx = player.x - self.x
            if abs(dx) > 80:
                self.vel_x = self.speed if dx > 0 else -self.speed
                self.facing_right = dx > 0
            else:
                self.vel_x = 0
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def draw_flag(self, screen, x, y, facing_right, camera_x=0):
        """五星红旗"""
        screen_x = x - camera_x
        if facing_right:
            flag_x = screen_x - 12
        else:
            flag_x = screen_x + self.width - 8
        flag_y = y - 40
        
        pygame.draw.line(screen, (139, 69, 19), (flag_x, flag_y), (flag_x, flag_y + 50), 3)
        pygame.draw.circle(screen, GOLD, (flag_x, flag_y - 2), 3)
        
        if facing_right:
            flag_rect = pygame.Rect(flag_x - 40, flag_y - 3, 42, 28)
        else:
            flag_rect = pygame.Rect(flag_x - 2, flag_y - 3, 42, 28)
        pygame.draw.rect(screen, RED, flag_rect)
        
        center_x = flag_rect.x + 11
        center_y = flag_rect.y + 14
        outer_radius = 9
        inner_radius = 3.5
        star_points = []
        for i in range(5):
            angle = math.radians(90 - i * 72)
            outer_x = center_x + outer_radius * math.cos(angle)
            outer_y = center_y - outer_radius * math.sin(angle)
            inner_angle = angle + math.radians(36)
            inner_x = center_x + inner_radius * math.cos(inner_angle)
            inner_y = center_y - inner_radius * math.sin(inner_angle)
            star_points.extend([(outer_x, outer_y), (inner_x, inner_y)])
        pygame.draw.polygon(screen, YELLOW, star_points)
        
        small_positions = [(-13, -7), (-4, -11), (-4, 4), (-13, 9)]
        for sx, sy in small_positions:
            scx = flag_rect.x + 30 + sx
            scy = flag_rect.y + 14 + sy
            small_points = []
            for i in range(5):
                angle = math.radians(90 - i * 72)
                ox = scx + 3.5 * math.cos(angle)
                oy = scy - 3.5 * math.sin(angle)
                ix = scx + 1.3 * math.cos(angle + math.radians(36))
                iy = scy - 1.3 * math.sin(angle + math.radians(36))
                small_points.extend([(ox, oy), (ix, iy)])
            pygame.draw.polygon(screen, YELLOW, small_points)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        self.draw_flag(screen, self.x, self.y, self.facing_right, camera_x)
        
        head_x = screen_x + self.width // 2
        head_y = self.y
        
        color = self.color if self.knockback_timer <= 0 else YELLOW
        
        pygame.draw.circle(screen, color, (head_x, head_y + 12), 12, 3)
        pygame.draw.line(screen, color, (head_x, self.y + 20), (head_x, self.y + 50), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x - 15, self.y + 30), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x + 15, self.y + 30), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x - 10, self.y + 60), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x + 10, self.y + 60), 3)
        
        eye_x = head_x + 5 if self.facing_right else head_x - 5
        pygame.draw.circle(screen, BLACK, (eye_x, head_y + 8), 2)
        
        gun_x = head_x + 25 if self.facing_right else head_x - 25
        pygame.draw.line(screen, DARK_GRAY, (head_x, head_y + 15), (gun_x, head_y + 10), 4)
        pygame.draw.rect(screen, DARK_GRAY, (gun_x - 5, head_y + 8, 10, 6))
        pygame.draw.circle(screen, BLUE, (gun_x - 2, head_y + 10), 3)
        
        bar_width = self.width
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class MuzzleFlash:
    def __init__(self, x, y, facing_right):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.timer = 5
        
    def update(self):
        self.timer -= 1
        return self.timer > 0
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if self.timer > 0:
            flash_size = random.randint(8, 15)
            if self.facing_right:
                pygame.draw.circle(screen, ORANGE, (screen_x + 5, self.y), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x + 5, self.y), flash_size - 3)
                pygame.draw.circle(screen, WHITE, (screen_x + 5, self.y), flash_size - 6)
            else:
                pygame.draw.circle(screen, ORANGE, (screen_x - 5, self.y), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x - 5, self.y), flash_size - 3)
                pygame.draw.circle(screen, WHITE, (screen_x - 5, self.y), flash_size - 6)

class Frostmourne:
    def __init__(self):
        self.cooldown = 0
        self.max_cooldown = 90
        self.active = False
        self.skill_ready = True
        
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            self.skill_ready = False
        else:
            self.skill_ready = True
        if self.active:
            self.active = False
    
    def use(self):
        if self.skill_ready and not self.active:
            self.cooldown = self.max_cooldown
            self.active = True
            return True
        return False
    
    def draw_cd_icon(self, screen, x, y):
        pygame.draw.rect(screen, DARK_GRAY, (x, y, 50, 50))
        pygame.draw.rect(screen, ICE_BLUE, (x+2, y+2, 46, 46))
        sword_x = x + 25
        sword_y = y + 25
        pygame.draw.line(screen, LIGHT_BLUE, (sword_x, sword_y-15), (sword_x, sword_y+10), 4)
        pygame.draw.line(screen, PURPLE, (sword_x, sword_y-15), (sword_x-5, sword_y-5), 2)
        pygame.draw.line(screen, PURPLE, (sword_x, sword_y-15), (sword_x+5, sword_y-5), 2)
        pygame.draw.polygon(screen, LIGHT_BLUE, [
            (sword_x-3, sword_y+10),
            (sword_x+3, sword_y+10),
            (sword_x, sword_y+18)
        ])
        if not self.skill_ready:
            cooldown_percent = self.cooldown / self.max_cooldown
            mask = pygame.Surface((50, 50))
            mask.set_alpha(128)
            mask.fill(BLACK)
            screen.blit(mask, (x, y))
            pygame.draw.rect(screen, (0, 0, 0, 128), 
                           (x, y, 50, 50 * cooldown_percent))
            cd_seconds = (self.cooldown // 60) + 1
            font = pygame.font.Font(None, 20)
            cd_text = font.render(str(cd_seconds), True, WHITE)
            screen.blit(cd_text, (x+18, y+15))

class IceShard:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = 20
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        pygame.draw.polygon(screen, ICE_BLUE, [
            (screen_x, self.y-3),
            (screen_x-2, self.y+2),
            (screen_x, self.y+1),
            (screen_x+2, self.y+2)
        ])

class StickMan:
    def __init__(self, x, y, color=BLACK, is_player=True):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.can_fly = True
        self.flying = False
        self.on_ground = True
        self.facing_right = True
        self.health = 10000 if is_player else 30
        self.max_health = self.health
        self.is_player = is_player
        self.color = color
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.knockback_timer = 0
        self.width = 30
        self.height = 60
        self.frozen = False
        self.frozen_timer = 0
        self.respawn_timer = 0
        self.collision_damage_timer = 0
        self.gatling_timer = 0
        self.sword_angle = 0
        self.shotgun_timer = 0
        self.in_tank = False
        
        if is_player:
            self.frostmourne = Frostmourne()
            self.ice_shards = []
            self.shotgun_pellets = []
            self.gatling_bullets = []
            self.muzzle_flashes = []
        
    def update(self, platforms):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return
        
        if self.collision_damage_timer > 0:
            self.collision_damage_timer -= 1
        
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
            if not self.is_player:
                self.vel_x = 0
                self.vel_y = 0
                return
        
        if self.gatling_timer > 0:
            self.gatling_timer -= 1
        
        if self.shotgun_timer > 0:
            self.shotgun_timer -= 1
        
        if not self.in_tank:
            if self.flying:
                self.vel_y += GRAVITY * 0.3
            else:
                self.vel_y += GRAVITY
            
            self.x += self.vel_x
            self.y += self.vel_y
            
            if self.y + self.height >= GROUND_Y:
                self.y = GROUND_Y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.flying = False
            else:
                self.on_ground = False
            
            for platform in platforms:
                if (self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width and
                    self.y + self.height > platform.y and
                    self.y + self.height < platform.y + platform.height + 10):
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.flying = False
        
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            if self.is_player:
                self.start_respawn()
            else:
                self.health = 0
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        if self.is_attacking:
            self.sword_angle += 20
        else:
            self.sword_angle = 0
        
        if self.is_player:
            self.frostmourne.update()
            for shard in self.ice_shards[:]:
                if not shard.update():
                    self.ice_shards.remove(shard)
            for pellet in self.shotgun_pellets[:]:
                pellet.update()
                if pellet.x < -100 or pellet.x > WORLD_WIDTH + 100:
                    self.shotgun_pellets.remove(pellet)
            for bullet in self.gatling_bullets[:]:
                bullet.update()
                if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                    self.gatling_bullets.remove(bullet)
            for flash in self.muzzle_flashes[:]:
                if not flash.update():
                    self.muzzle_flashes.remove(flash)
    
    def shoot_shotgun(self):
        if self.is_player and self.shotgun_timer <= 0 and not self.in_tank:
            self.shotgun_timer = 40
            direction = 1 if self.facing_right else -1
            bullet_x = self.x + self.width if self.facing_right else self.x
            bullet_y = self.y + self.height // 2
            
            flash = MuzzleFlash(bullet_x, bullet_y, self.facing_right)
            self.muzzle_flashes.append(flash)
            
            for i in range(-10, 10):
                angle_offset = i * 3.6
                pellet = ShotgunPellet(bullet_x, bullet_y, direction, angle_offset, 10)
                self.shotgun_pellets.append(pellet)
            return True
        return False
    
    def start_respawn(self):
        self.respawn_timer = 60
        self.vel_x = 0
        self.vel_y = 0
    
    def respawn(self):
        self.x = 100
        self.y = GROUND_Y - 60
        self.vel_x = 0
        self.vel_y = 0
        self.health = self.max_health
        self.frozen = False
        self.frozen_timer = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.knockback_timer = 0
        self.on_ground = True
        self.flying = False
        self.respawn_timer = 0
        self.collision_damage_timer = 0
        self.gatling_timer = 0
        self.shotgun_timer = 0
        self.in_tank = False
        if self.is_player:
            self.ice_shards.clear()
            self.shotgun_pellets.clear()
            self.gatling_bullets.clear()
            self.muzzle_flashes.clear()
    
    def fly(self):
        if self.can_fly and self.respawn_timer == 0 and not self.in_tank:
            self.flying = True
            self.vel_y = -8
            self.on_ground = False
    
    def stop_fly(self):
        self.flying = False
    
    def use_frostmourne(self):
        if self.is_player and self.frostmourne.use() and not self.in_tank:
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                shard = IceShard(self.x + self.width//2, self.y + self.height//2, vx, vy)
                self.ice_shards.append(shard)
            return True
        return False
    
    def jump(self):
        if self.on_ground and not self.frozen and self.respawn_timer == 0 and not self.in_tank:
            self.vel_y = JUMP_POWER
            self.on_ground = False
    
    def attack(self):
        if (self.attack_cooldown <= 0 and not self.is_attacking 
            and not self.frozen and self.respawn_timer == 0 and not self.in_tank):
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = 30
            return True
        return False
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0 and not self.frozen and self.respawn_timer == 0:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def freeze(self, duration=90):
        if not self.is_player:
            self.frozen = True
            self.frozen_timer = duration
            self.vel_x = 0
            self.vel_y = 0
    
    def get_attack_rect(self):
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20, 300, 40)
        else:
            return pygame.Rect(self.x - 300, self.y + 20, 300, 40)
    
    def draw_flag(self, screen, x, y, facing_right, camera_x=0):
        """五星红旗"""
        screen_x = x - camera_x
        if facing_right:
            flag_x = screen_x - 12
        else:
            flag_x = screen_x + self.width - 8
        flag_y = y - 40
        
        pygame.draw.line(screen, (139, 69, 19), (flag_x, flag_y), (flag_x, flag_y + 50), 3)
        pygame.draw.circle(screen, GOLD, (flag_x, flag_y - 2), 3)
        
        if facing_right:
            flag_rect = pygame.Rect(flag_x - 40, flag_y - 3, 42, 28)
        else:
            flag_rect = pygame.Rect(flag_x - 2, flag_y - 3, 42, 28)
        pygame.draw.rect(screen, RED, flag_rect)
        
        center_x = flag_rect.x + 11
        center_y = flag_rect.y + 14
        outer_radius = 9
        inner_radius = 3.5
        star_points = []
        for i in range(5):
            angle = math.radians(90 - i * 72)
            outer_x = center_x + outer_radius * math.cos(angle)
            outer_y = center_y - outer_radius * math.sin(angle)
            inner_angle = angle + math.radians(36)
            inner_x = center_x + inner_radius * math.cos(inner_angle)
            inner_y = center_y - inner_radius * math.sin(inner_angle)
            star_points.extend([(outer_x, outer_y), (inner_x, inner_y)])
        pygame.draw.polygon(screen, YELLOW, star_points)
        
        small_positions = [(-13, -7), (-4, -11), (-4, 4), (-13, 9)]
        for sx, sy in small_positions:
            scx = flag_rect.x + 30 + sx
            scy = flag_rect.y + 14 + sy
            small_points = []
            for i in range(5):
                angle = math.radians(90 - i * 72)
                ox = scx + 3.5 * math.cos(angle)
                oy = scy - 3.5 * math.sin(angle)
                ix = scx + 1.3 * math.cos(angle + math.radians(36))
                iy = scy - 1.3 * math.sin(angle + math.radians(36))
                small_points.extend([(ox, oy), (ix, iy)])
            pygame.draw.polygon(screen, YELLOW, small_points)
    
    def draw(self, screen, camera_x=0):
        if self.in_tank:
            return
        
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        if self.respawn_timer > 0:
            if (self.respawn_timer // 5) % 2 == 0:
                return
        
        self.draw_flag(screen, self.x, self.y, self.facing_right, camera_x)
        
        if self.frozen:
            pygame.draw.rect(screen, ICE_BLUE, (screen_x-2, self.y-2, self.width+4, self.height+4), 3)
        
        if self.flying and not self.frozen and self.respawn_timer == 0:
            if self.facing_right:
                pygame.draw.ellipse(screen, (200, 200, 200), 
                                  (screen_x-15, self.y+20, 15, 25))
                pygame.draw.ellipse(screen, (200, 200, 200), 
                                  (screen_x+30, self.y+20, 15, 25))
            else:
                pygame.draw.ellipse(screen, (200, 200, 200), 
                                  (screen_x-15, self.y+20, 15, 25))
                pygame.draw.ellipse(screen, (200, 200, 200), 
                                  (screen_x+30, self.y+20, 15, 25))
        
        head_x = screen_x + self.width // 2
        head_y = self.y
        
        if self.is_attacking:
            if self.facing_right:
                sword_start = (head_x + 25, self.y + 25)
                sword_end = (head_x + 300, self.y + 15 + math.sin(self.sword_angle * 0.05) * 10)
                pygame.draw.line(screen, SILVER, sword_start, sword_end, 8)
                pygame.draw.line(screen, BROWN, (head_x + 20, self.y + 28), (head_x + 25, self.y + 25), 5)
                pygame.draw.line(screen, GOLD, (head_x + 23, self.y + 22), (head_x + 27, self.y + 28), 4)
                pygame.draw.circle(screen, SILVER, (head_x + 300, self.y + 15), 8)
                pygame.draw.line(screen, WHITE, sword_start, sword_end, 2)
            else:
                sword_start = (head_x - 25, self.y + 25)
                sword_end = (head_x - 300, self.y + 15 + math.sin(self.sword_angle * 0.05) * 10)
                pygame.draw.line(screen, SILVER, sword_start, sword_end, 8)
                pygame.draw.line(screen, BROWN, (head_x - 20, self.y + 28), (head_x - 25, self.y + 25), 5)
                pygame.draw.line(screen, GOLD, (head_x - 23, self.y + 22), (head_x - 27, self.y + 28), 4)
                pygame.draw.circle(screen, SILVER, (head_x - 300, self.y + 15), 8)
                pygame.draw.line(screen, WHITE, sword_start, sword_end, 2)
        
        color = self.color if self.knockback_timer <= 0 else RED
        if self.frozen:
            color = ICE_BLUE
        
        pygame.draw.circle(screen, color, (head_x, head_y + 10), 12, 3)
        pygame.draw.line(screen, color, (head_x, self.y + 20), (head_x, self.y + 50), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x - 15, self.y + 30), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x + 15, self.y + 30), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x - 10, self.y + 60), 3)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x + 10, self.y + 60), 3)
        
        eye_x = head_x + 5 if self.facing_right else head_x - 5
        pygame.draw.circle(screen, BLACK, (eye_x, head_y + 8), 2)
        
        if self.is_player:
            if self.facing_right:
                pygame.draw.rect(screen, DARK_GRAY, (screen_x + 20, self.y + 28, 25, 8))
                pygame.draw.rect(screen, BROWN, (screen_x + 30, self.y + 36, 8, 6))
                pygame.draw.circle(screen, GRAY, (screen_x + 45, self.y + 32), 5)
            else:
                pygame.draw.rect(screen, DARK_GRAY, (screen_x - 15, self.y + 28, 25, 8))
                pygame.draw.rect(screen, BROWN, (screen_x - 8, self.y + 36, 8, 6))
                pygame.draw.circle(screen, GRAY, (screen_x - 15, self.y + 32), 5)
        
        if self.is_player and self.frostmourne.active:
            for i in range(3):
                radius = 30 + i * 10
                pygame.draw.circle(screen, ICE_BLUE, (head_x, head_y + 30), radius, 2)
        
        if self.respawn_timer == 0:
            bar_width = 40
            bar_height = 6
            health_percent = max(0, self.health / self.max_health)
            pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        if self.is_player:
            for shard in self.ice_shards:
                shard.draw(screen, camera_x)
            for pellet in self.shotgun_pellets:
                pellet.draw(screen, camera_x)
            for bullet in self.gatling_bullets:
                bullet.draw(screen, camera_x)
            for flash in self.muzzle_flashes:
                flash.draw(screen, camera_x)

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        pygame.draw.rect(screen, self.color, (screen_x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stickman - Tank & Zombie Boss")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.screen_flash_timer = 0
        self.init_game()
    
    def init_game(self):
        self.player = StickMan(200, GROUND_Y - 60)
        self.tank = None
        self.sniper_allies = []
        self.sniper_enemies = []
        self.zombie_boss = None
        self.platforms = []
        self.camera_x = 0
        self.game_over = False
        self.score = 0
        self.kill_count = 0
        self.kills_since_boss = 0
        self.boss_active = False
        self.death_count = 0
        self.spawn_timer = 0
        self.tutorial_text = "K = Shotgun | G = Nuke | F = Freeze | SPACE = Fly | J = Sword | H = Enter Tank"
        
        self.shake_timer = 0
        self.frost_effect_timer = 0
        
        for i in range(0, WORLD_WIDTH, 300):
            self.platforms.append(Platform(i, GROUND_Y, 200, 20, DARK_GRAY))
            if i > 200 and i % 600 == 0:
                self.platforms.append(Platform(i + 100, GROUND_Y - 80, 120, 20, BROWN))
            if i > 400 and i % 500 == 0:
                self.platforms.append(Platform(i + 200, GROUND_Y - 150, 100, 20, BROWN))
        
        self.tank = Tank(400, GROUND_Y - 40)
        
        for i in range(8):
            ally = SniperAlly(150 + i * 40, GROUND_Y - 60)
            self.sniper_allies.append(ally)
        
        for i in range(5):
            self.spawn_sniper_enemy(300 + i * 400)
    
    def spawn_sniper_enemy(self, x=None):
        if x is None:
            x = self.player.x + random.randint(300, 600)
            x = min(x, WORLD_WIDTH - 100)
        else:
            x = min(x, WORLD_WIDTH - 100)
        y = GROUND_Y - 70
        new_enemy = SniperEnemy(x, y)
        self.sniper_enemies.append(new_enemy)
    
    def spawn_zombie_boss(self):
        if not self.boss_active and self.kills_since_boss >= 15:
            self.zombie_boss = ZombieBoss(self.player.x + 300, GROUND_Y - 80)
            self.boss_active = True
            self.shake_timer = 20
            print("僵尸BOSS出现了！")
    
    def nuclear_strike(self):
        self.screen_flash_timer = 8
        self.shake_timer = 15
        
        for enemy in self.sniper_enemies[:]:
            enemy.health = 0
            self.sniper_enemies.remove(enemy)
            self.score += 100
            self.kill_count += 1
            self.kills_since_boss += 1
        
        if self.zombie_boss:
            self.zombie_boss.take_damage(500, 0)
            if self.zombie_boss.health <= 0:
                self.zombie_boss = None
                self.boss_active = False
                self.score += 500
                self.kill_count += 1
                self.kills_since_boss = 0
                print("僵尸BOSS被核弹击败！")
        
        for ally in self.sniper_allies[:]:
            ally.health = 0
            self.sniper_allies.remove(ally)
            self.score += 50
        
        if self.tank and self.tank.health > 0 and self.tank.respawn_timer == 0:
            self.tank.health = max(0, self.tank.health - 200)
        
        while len(self.sniper_allies) < 8:
            new_ally = SniperAlly(self.player.x + random.randint(-100, 100), GROUND_Y - 60)
            self.sniper_allies.append(new_ally)
        
        return True
    
    def frostmourne_aoe(self):
        for enemy in self.sniper_enemies[:]:
            if not enemy.frozen:
                enemy.take_damage(10, 1 if enemy.x < self.player.x else -1)
                enemy.freeze(90)
        if self.zombie_boss and not self.zombie_boss.frozen:
            self.zombie_boss.take_damage(10, 1 if self.zombie_boss.x < self.player.x else -1)
            self.zombie_boss.freeze(60)
        for ally in self.sniper_allies[:]:
            if not ally.frozen:
                ally.take_damage(10, 1 if ally.x < self.player.x else -1)
                ally.freeze(60)
        self.shake_timer = 8
        self.frost_effect_timer = 15
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.player.respawn_timer > 0:
            return
        
        if keys[pygame.K_h]:
            if self.player.in_tank:
                self.player.in_tank = False
                if self.tank and self.tank.health > 0:
                    self.player.x = self.tank.x + self.tank.width // 2 - self.player.width // 2
                    self.player.y = self.tank.y - self.player.height
            else:
                if self.tank and self.tank.health > 0 and self.tank.respawn_timer == 0:
                    self.player.in_tank = True
                    self.player.x = self.tank.x + self.tank.width // 2 - self.player.width // 2
                    self.player.y = self.tank.y - self.player.height
            return
        
        if self.player.in_tank and self.tank and self.tank.health > 0 and self.tank.respawn_timer == 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.tank.move_left()
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.tank.move_right()
            else:
                self.tank.stop()
            
            if keys[pygame.K_SPACE]:
                self.tank.shoot()
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            else:
                self.player.vel_x *= 0.8
            
            if keys[pygame.K_SPACE]:
                self.player.fly()
            else:
                self.player.stop_fly()
            
            if keys[pygame.K_k]:
                self.player.shoot_shotgun()
        
        if keys[pygame.K_g]:
            self.nuclear_strike()
    
    def check_collisions(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        tank_rect = None
        
        if self.tank and self.tank.health > 0 and self.tank.respawn_timer == 0:
            tank_rect = pygame.Rect(self.tank.x, self.tank.y, self.tank.width, self.tank.height)
            
            heat_damage = self.tank.get_heat_damage()
            if heat_damage > 0:
                tank_center = (self.tank.x + self.tank.width//2, self.tank.y + self.tank.height//2)
                for enemy in self.sniper_enemies[:]:
                    enemy_center = (enemy.x + enemy.width//2, enemy.y + enemy.height//2)
                    dist = math.sqrt((tank_center[0] - enemy_center[0])**2 + (tank_center[1] - enemy_center[1])**2)
                    if dist < 80:
                        enemy.take_damage(heat_damage, 1 if enemy.x < self.tank.x else -1)
                        if enemy.health <= 0:
                            self.sniper_enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                            self.kills_since_boss += 1
                if self.zombie_boss:
                    boss_center = (self.zombie_boss.x + self.zombie_boss.width//2, self.zombie_boss.y + self.zombie_boss.height//2)
                    dist = math.sqrt((tank_center[0] - boss_center[0])**2 + (tank_center[1] - boss_center[1])**2)
                    if dist < 100:
                        self.zombie_boss.take_damage(heat_damage, 1 if self.zombie_boss.x < self.tank.x else -1)
            
            for enemy in self.sniper_enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if tank_rect.colliderect(enemy_rect):
                    enemy.take_damage(20, 1 if enemy.x < self.tank.x else -1)
                    if enemy.health <= 0:
                        self.sniper_enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                        self.kills_since_boss += 1
            if self.zombie_boss:
                boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                if tank_rect.colliderect(boss_rect):
                    self.zombie_boss.take_damage(20, 1 if self.zombie_boss.x < self.tank.x else -1)
        
        # 敌人子弹
        for enemy in self.sniper_enemies:
            for bullet in enemy.bullets[:]:
                bullet_rect = bullet.get_rect()
                if tank_rect and bullet_rect.colliderect(tank_rect):
                    if self.tank.take_damage(bullet.damage):
                        if self.player.in_tank:
                            self.player.in_tank = False
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
                elif bullet_rect.colliderect(player_rect):
                    self.player.take_damage(bullet.damage, 1 if bullet.x < self.player.x else -1)
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
        
        # BOSS弓箭
        if self.zombie_boss:
            for bullet in self.zombie_boss.bullets[:]:
                bullet_rect = bullet.get_rect()
                if tank_rect and bullet_rect.colliderect(tank_rect):
                    if self.tank.take_damage(bullet.damage):
                        if self.player.in_tank:
                            self.player.in_tank = False
                    if bullet in self.zombie_boss.bullets:
                        self.zombie_boss.bullets.remove(bullet)
                elif bullet_rect.colliderect(player_rect):
                    self.player.take_damage(bullet.damage, 1 if bullet.x < self.player.x else -1)
                    if bullet in self.zombie_boss.bullets:
                        self.zombie_boss.bullets.remove(bullet)
        
        # 坦克炮弹
        if self.tank and self.tank.health > 0 and self.tank.respawn_timer == 0:
            for bullet in self.tank.bullets[:]:
                bullet_rect = bullet.get_rect()
                for enemy in self.sniper_enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                        if enemy.health <= 0:
                            self.sniper_enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                            self.kills_since_boss += 1
                        if bullet in self.tank.bullets:
                            self.tank.bullets.remove(bullet)
                        break
                if self.zombie_boss:
                    boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                    if bullet_rect.colliderect(boss_rect):
                        self.zombie_boss.take_damage(bullet.damage, 1 if self.zombie_boss.x < bullet.x else -1)
                        if bullet in self.tank.bullets:
                            self.tank.bullets.remove(bullet)
            
            for bullet in self.tank.gunner.bullets[:]:
                bullet_rect = bullet.get_rect()
                for enemy in self.sniper_enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                        if enemy.health <= 0:
                            self.sniper_enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                            self.kills_since_boss += 1
                        if bullet in self.tank.gunner.bullets:
                            self.tank.gunner.bullets.remove(bullet)
                        break
                if self.zombie_boss:
                    boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                    if bullet_rect.colliderect(boss_rect):
                        self.zombie_boss.take_damage(bullet.damage, 1 if self.zombie_boss.x < bullet.x else -1)
                        if bullet in self.tank.gunner.bullets:
                            self.tank.gunner.bullets.remove(bullet)
        
        # 玩家近战攻击
        if self.player.is_attacking and self.player.attack_timer == 5:
            attack_rect = self.player.get_attack_rect()
            for enemy in self.sniper_enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if attack_rect.colliderect(enemy_rect):
                    enemy.take_damage(50, 1 if enemy.x < self.player.x else -1)
                    if enemy.health <= 0:
                        self.sniper_enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                        self.kills_since_boss += 1
            if self.zombie_boss:
                boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                if attack_rect.colliderect(boss_rect):
                    self.zombie_boss.take_damage(50, 1 if self.zombie_boss.x < self.player.x else -1)
            for ally in self.sniper_allies[:]:
                ally_rect = pygame.Rect(ally.x, ally.y, ally.width, ally.height)
                if attack_rect.colliderect(ally_rect):
                    ally.take_damage(40, 1 if ally.x < self.player.x else -1)
        
        # 霰弹枪子弹
        for pellet in self.player.shotgun_pellets[:]:
            pellet_rect = pellet.get_rect()
            for enemy in self.sniper_enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if pellet_rect.colliderect(enemy_rect):
                    enemy.take_damage(pellet.damage, 1 if enemy.x < pellet.x else -1)
                    if enemy.health <= 0:
                        self.sniper_enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                        self.kills_since_boss += 1
                    if pellet in self.player.shotgun_pellets:
                        self.player.shotgun_pellets.remove(pellet)
                    break
            if self.zombie_boss:
                boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                if pellet_rect.colliderect(boss_rect):
                    self.zombie_boss.take_damage(pellet.damage, 1 if self.zombie_boss.x < pellet.x else -1)
                    if pellet in self.player.shotgun_pellets:
                        self.player.shotgun_pellets.remove(pellet)
        
        # 冰霜碎片
        for shard in self.player.ice_shards[:]:
            shard_rect = pygame.Rect(shard.x-3, shard.y-3, 6, 6)
            for enemy in self.sniper_enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if shard_rect.colliderect(enemy_rect):
                    enemy.take_damage(15, 1 if enemy.x < shard.x else -1)
                    if enemy.health <= 0:
                        self.sniper_enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                        self.kills_since_boss += 1
                    if shard in self.player.ice_shards:
                        self.player.ice_shards.remove(shard)
                    break
            if self.zombie_boss:
                boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                if shard_rect.colliderect(boss_rect):
                    self.zombie_boss.take_damage(15, 1 if self.zombie_boss.x < shard.x else -1)
                    if shard in self.player.ice_shards:
                        self.player.ice_shards.remove(shard)
        
        # 友方子弹
        for ally in self.sniper_allies:
            for bullet in ally.bullets[:]:
                bullet_rect = bullet.get_rect()
                if bullet_rect.colliderect(player_rect):
                    self.player.take_damage(bullet.damage, 1 if bullet.x < self.player.x else -1)
                    if bullet in ally.bullets:
                        ally.bullets.remove(bullet)
                for enemy in self.sniper_enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                        if enemy.health <= 0:
                            self.sniper_enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                            self.kills_since_boss += 1
                        if bullet in ally.bullets:
                            ally.bullets.remove(bullet)
                        break
                if self.zombie_boss:
                    boss_rect = pygame.Rect(self.zombie_boss.x, self.zombie_boss.y, self.zombie_boss.width, self.zombie_boss.height)
                    if bullet_rect.colliderect(boss_rect):
                        self.zombie_boss.take_damage(bullet.damage, 1 if self.zombie_boss.x < bullet.x else -1)
                        if bullet in ally.bullets:
                            ally.bullets.remove(bullet)
        
        # 玩家与敌人碰撞
        for enemy in self.sniper_enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect):
                if self.player.collision_damage_timer <= 0 and self.player.respawn_timer == 0:
                    self.player.health -= 10
                    self.player.collision_damage_timer = 30
        
        self.sniper_allies = [a for a in self.sniper_allies if a.health > 0]
        if self.zombie_boss and self.zombie_boss.health <= 0:
            self.zombie_boss = None
            self.boss_active = False
            self.score += 500
            self.kill_count += 1
            self.kills_since_boss = 0
            print("僵尸BOSS被击败！")
    
    def update(self):
        if self.game_over:
            return
        
        if self.tank and self.tank.health > 0:
            self.tank.update(self.platforms, self.sniper_enemies + ([self.zombie_boss] if self.zombie_boss else []))
            if self.player.in_tank:
                self.player.x = self.tank.x + self.tank.width // 2 - self.player.width // 2
                self.player.y = self.tank.y - self.player.height
        elif self.player.in_tank:
            self.player.in_tank = False
        
        self.player.update(self.platforms)
        
        if self.death_count >= 10:
            self.game_over = True
            return
        
        if self.player.health <= 0 and self.player.respawn_timer == 0:
            self.death_count += 1
            if self.death_count < 10:
                self.player.start_respawn()
        
        if self.screen_flash_timer > 0:
            self.screen_flash_timer -= 1
        
        # 保持8个狙击手小弟
        if len(self.sniper_allies) < 8:
            new_ally = SniperAlly(self.player.x + random.randint(-100, 100), GROUND_Y - 60)
            self.sniper_allies.append(new_ally)
        
        for ally in self.sniper_allies:
            ally.update(self.platforms, self.sniper_enemies + ([self.zombie_boss] if self.zombie_boss else []), self.player, self.tank)
        
        for enemy in self.sniper_enemies:
            enemy.update(self.player, self.platforms, self.tank)
        
        if self.zombie_boss:
            self.zombie_boss.update(self.player, self.platforms, self.tank)
        
        self.check_collisions()
        
        # 召唤BOSS条件
        if not self.boss_active and self.kills_since_boss >= 15:
            self.spawn_zombie_boss()
        
        # 保持5个狙击手敌人
        self.spawn_timer += 1
        if self.spawn_timer > 90 and len(self.sniper_enemies) < 5 and not self.boss_active:
            self.spawn_timer = 0
            self.spawn_sniper_enemy()
        
        if self.player.in_tank and self.tank and self.tank.health > 0:
            self.camera_x = self.tank.x - SCREEN_WIDTH // 2 + self.tank.width // 2
        else:
            self.camera_x = self.player.x - SCREEN_WIDTH // 2 + self.player.width // 2
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - SCREEN_WIDTH))
        
        if self.shake_timer > 0:
            self.shake_timer -= 1
        if self.frost_effect_timer > 0:
            self.frost_effect_timer -= 1
    
    def draw(self):
        shake_x = random.randint(-5, 5) if self.shake_timer > 0 else 0
        shake_y = random.randint(-5, 5) if self.shake_timer > 0 else 0
        
        if self.frost_effect_timer > 0:
            self.screen.fill((150, 200, 255))
        else:
            self.screen.fill(SKY_BLUE)
        
        if self.screen_flash_timer > 0:
            alpha = min(255, self.screen_flash_timer * 30)
            white_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            white_surface.fill(WHITE)
            white_surface.set_alpha(alpha)
            self.screen.blit(white_surface, (0, 0))
        
        if self.frost_effect_timer > 0:
            for _ in range(30):
                fx = random.randint(0, SCREEN_WIDTH)
                fy = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (fx, fy), random.randint(1, 3))
        
        for i in range(5):
            cloud_x = (i * 400 - self.camera_x * 0.3) % (SCREEN_WIDTH + 400) - 200
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 50))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 100, 60))
        
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        for enemy in self.sniper_enemies:
            enemy.draw(self.screen, self.camera_x)
        
        if self.zombie_boss:
            self.zombie_boss.draw(self.screen, self.camera_x)
        
        for ally in self.sniper_allies:
            ally.draw(self.screen, self.camera_x)
        
        if self.tank and self.tank.health > 0:
            self.tank.draw(self.screen, self.camera_x)
        
        self.player.draw(self.screen, self.camera_x)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {max(0, self.player.health)}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        enemies_text = self.font.render(f"Enemies: {len(self.sniper_enemies)}/5", True, BLACK)
        self.screen.blit(enemies_text, (10, 130))
        
        allies_text = self.font.render(f"Snipers: {len(self.sniper_allies)}/8", True, DARK_GREEN)
        self.screen.blit(allies_text, (10, 170))
        
        deaths_text = self.font.render(f"Deaths: {self.death_count}/10", True, RED if self.death_count >= 7 else BLACK)
        self.screen.blit(deaths_text, (10, 210))
        
        # BOSS相关UI
        boss_info = ""
        if self.zombie_boss:
            boss_info = f"ZOMBIE BOSS HP: {self.zombie_boss.health}"
            boss_color = RED
        elif self.boss_active:
            boss_info = "BOSS INCOMING!"
            boss_color = ORANGE
        else:
            boss_info = f"Next Boss: {15 - self.kills_since_boss} kills"
            boss_color = BLACK
        boss_text = self.font.render(boss_info, True, boss_color)
        self.screen.blit(boss_text, (10, 250))
        
        if self.tank and self.tank.health > 0:
            tank_text = self.font.render(f"Tank HP: {self.tank.health}", True, DARK_GREEN)
            self.screen.blit(tank_text, (10, 290))
            heat_level = self.tank.get_heat_level()
            if heat_level > 0:
                heat_text = self.font.render(f"HEAT: {heat_level}", True, ORANGE)
                self.screen.blit(heat_text, (10, 330))
            if self.tank.respawn_timer > 0:
                respawn_text = self.font.render(f"TANK RESPAWN: {self.tank.respawn_timer // 60 + 1}s", True, ORANGE)
                self.screen.blit(respawn_text, (10, 370))
            if self.player.in_tank:
                in_tank_text = self.font.render("IN TANK (H to exit)", True, GREEN)
                self.screen.blit(in_tank_text, (SCREEN_WIDTH - 250, 10))
            else:
                near_text = self.font.render("H to teleport to tank", True, GREEN)
                self.screen.blit(near_text, (SCREEN_WIDTH - 250, 10))
        
        shotgun_text = self.font.render("K = SHOTGUN", True, ORANGE)
        self.screen.blit(shotgun_text, (SCREEN_WIDTH - 250, 50))
        
        nuke_text = self.font.render("G = NUKE", True, GREEN)
        self.screen.blit(nuke_text, (SCREEN_WIDTH - 250, 90))
        
        fly_text = self.font.render("SPACE = FLY", True, DARK_BLUE)
        self.screen.blit(fly_text, (SCREEN_WIDTH - 250, 130))
        
        sword_text = self.font.render("J = LONG SWORD", True, SILVER)
        self.screen.blit(sword_text, (SCREEN_WIDTH - 250, 170))
        
        tank_shoot_text = self.font.render("IN TANK: SPACE = Cannon", True, DARK_RED)
        self.screen.blit(tank_shoot_text, (SCREEN_WIDTH - 300, 210))
        
        self.player.frostmourne.draw_cd_icon(self.screen, SCREEN_WIDTH - 70, 250)
        
        skill_desc = self.font.render("F = Freeze", True, DARK_BLUE)
        self.screen.blit(skill_desc, (SCREEN_WIDTH - 200, 310))
        
        if self.player.respawn_timer > 0:
            respawn_text = self.font.render(f"RESPAWNING... {self.player.respawn_timer // 6 + 1}", True, RED)
            text_rect = respawn_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(respawn_text, text_rect)
        
        if self.kill_count < 5:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 400, 20))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            kills_text = self.font.render(f"Total Kills: {self.kill_count}", True, WHITE)
            kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(kills_text, kills_rect)
            
            deaths_text = self.font.render(f"Deaths: {self.death_count}/10", True, ORANGE)
            deaths_rect = deaths_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(deaths_text, deaths_rect)
            
            final_text = self.font.render("Press Q to quit", True, WHITE)
            final_rect = final_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
            self.screen.blit(final_text, final_rect)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j:
                        self.player.attack()
                    
                    elif event.key == pygame.K_f:
                        if self.player.use_frostmourne():
                            self.frostmourne_aoe()
                    
                    elif event.key == pygame.K_q and self.game_over:
                        self.running = False
            
            self.handle_input()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
