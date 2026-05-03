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
WORLD_WIDTH = 5000  # 世界宽度

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

class Enemy:
    """敌人基类"""
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type  # sword, sniper, plane, tank
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.5
        self.width = 35
        self.height = 65
        self.health = 50
        self.max_health = 50
        self.facing_right = False
        self.on_ground = True
        self.frozen = False
        self.frozen_timer = 0
        self.knockback_timer = 0
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.shoot_timer = 0
        self.bullets = []
        
        # 根据类型设置属性
        if enemy_type == "sword":
            self.color = (200, 100, 100)
            self.speed = 2.5
            self.health = 80
            self.max_health = 80
            self.attack_damage = 20
        elif enemy_type == "sniper":
            self.color = (100, 200, 100)
            self.speed = 1.5
            self.health = 40
            self.max_health = 40
            self.attack_damage = 15
            self.shoot_delay = 60
        elif enemy_type == "plane":
            self.color = (100, 100, 200)
            self.speed = 3
            self.health = 60
            self.max_health = 60
            self.attack_damage = 12
            self.flying = True
            self.y = y - 100
        else:  # tank
            self.color = (150, 150, 50)
            self.speed = 1
            self.health = 120
            self.max_health = 120
            self.width = 45
            self.height = 50
            self.attack_damage = 25
            self.shoot_delay = 45
    
    def update(self, player, platforms, boss_allies):
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
            return
        
        # 移动向玩家
        dx = player.x - self.x
        if abs(dx) > 20:
            self.vel_x = self.speed if dx > 0 else -self.speed
            self.facing_right = dx > 0
        else:
            self.vel_x = 0
        
        # 重力
        if self.type != "plane":
            self.vel_y += GRAVITY
        else:
            # 飞机在空中飘浮
            self.vel_y += GRAVITY * 0.3
            if self.y > GROUND_Y - 100:
                self.vel_y = -3
        
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 地面碰撞
        if self.type != "plane" and self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # 平台碰撞
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + platform.height + 10):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
        
        # 边界
        self.x = max(0, min(self.x, WORLD_WIDTH - self.width))
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            self.health = 0
        
        # 攻击冷却
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        # 射击（狙击手和坦克）
        if self.type in ["sniper", "tank"]:
            if self.shoot_timer <= 0:
                if abs(dx) < 300:
                    direction = 1 if dx > 0 else -1
                    bullet = GatlingBullet(
                        self.x + self.width if direction > 0 else self.x,
                        self.y + self.height // 2,
                        direction, random.uniform(-1, 1), self.attack_damage
                    )
                    self.bullets.append(bullet)
                    self.shoot_timer = self.shoot_delay
            else:
                self.shoot_timer -= 1
        
        # 近战攻击（大剑）
        if self.type == "sword" and abs(dx) < 50 and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = 40
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                self.bullets.remove(bullet)
        
        # 击退
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
    
    def attack_player(self, player):
        if self.type == "sword" and self.is_attacking and self.attack_timer == 5:
            if abs(self.x - player.x) < 60:
                player.take_damage(self.attack_damage, 1 if player.x < self.x else -1)
                return True
        return False
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        color = self.color if self.knockback_timer <= 0 else ORANGE
        if self.frozen:
            color = ICE_BLUE
        
        # 身体
        pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
        
        # 头部
        head_x = screen_x + self.width // 2
        head_y = self.y - 15
        pygame.draw.circle(screen, color, (head_x, head_y), 15)
        
        # 眼睛
        eye_x = head_x + 8 if self.facing_right else head_x - 8
        pygame.draw.circle(screen, BLACK, (eye_x, head_y - 5), 4)
        
        # 根据类型绘制武器
        if self.type == "sword":
            # 大剑
            if self.is_attacking:
                sword_end = (head_x + 60 if self.facing_right else head_x - 60, head_y + 10)
            else:
                sword_end = (head_x + 40 if self.facing_right else head_x - 40, head_y + 10)
            pygame.draw.line(screen, SILVER, (head_x, head_y + 10), sword_end, 6)
        elif self.type == "sniper":
            # 狙击枪
            gun_x = head_x + 25 if self.facing_right else head_x - 25
            pygame.draw.line(screen, DARK_GRAY, (head_x, head_y + 15), (gun_x, head_y + 10), 5)
            pygame.draw.rect(screen, DARK_GRAY, (gun_x - 5, head_y + 8, 10, 6))
        elif self.type == "plane":
            # 飞机
            pygame.draw.polygon(screen, color, [
                (screen_x, self.y + self.height//2),
                (screen_x + self.width//2, self.y),
                (screen_x + self.width, self.y + self.height//2),
                (screen_x + self.width//2, self.y + self.height)
            ])
            pygame.draw.polygon(screen, (200, 0, 0), [
                (screen_x + self.width, self.y + self.height//2),
                (screen_x + self.width + 15, self.y + self.height//2 - 5),
                (screen_x + self.width + 15, self.y + self.height//2 + 5)
            ])
        elif self.type == "tank":
            # 坦克
            pygame.draw.rect(screen, DARK_GREEN, (screen_x + 5, self.y - 10, self.width - 10, 20))
            pygame.draw.rect(screen, DARK_GRAY, (screen_x + self.width//2 - 10, self.y - 20, 20, 15))
            pygame.draw.line(screen, GRAY, (head_x, self.y - 20), 
                           (head_x + 30 if self.facing_right else head_x - 30, self.y - 15), 5)
        
        # 血条
        bar_width = self.width
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 10, bar_width * health_percent, bar_height))
        
        # 子弹
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

class BossAlly:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3
        self.width = 35
        self.height = 70
        self.health = 200
        self.max_health = 200
        self.facing_right = True
        self.on_ground = True
        self.flying = False
        self.shoot_timer = 0
        self.shoot_delay = 20
        self.bullets = []
        self.color = DARK_RED
        self.knockback_timer = 0
        self.is_charging = False
        self.charge_timer = 0
        
    def update(self, platforms, enemies, player):
        self.vel_y += GRAVITY * 0.5
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
            
            if abs(dx) > 80:
                self.vel_x = self.speed if dx > 0 else -self.speed
                self.facing_right = dx > 0
            else:
                self.vel_x = 0
            
            # 冲锋
            if abs(dx) < 150 and abs(dx) > 30 and random.randint(0, 80) == 0 and not self.is_charging:
                self.is_charging = True
                self.charge_timer = 25
            
            if self.is_charging:
                self.charge_timer -= 1
                if self.charge_timer <= 0:
                    self.is_charging = False
                else:
                    self.vel_x = 12 if dx > 0 else -12
            
            # 射击
            if self.shoot_timer <= 0:
                direction = 1 if dx > 0 else -1
                bullet = GatlingBullet(
                    self.x + self.width if direction > 0 else self.x,
                    self.y + self.height // 2,
                    direction, random.uniform(-2, 2), 15
                )
                self.bullets.append(bullet)
                self.shoot_timer = self.shoot_delay
            else:
                self.shoot_timer -= 1
        
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
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        head_x = screen_x + self.width // 2
        head_y = self.y
        
        color = ORANGE if self.is_charging else self.color
        if self.knockback_timer > 0:
            color = YELLOW
        
        pygame.draw.circle(screen, color, (head_x, head_y + 12), 14, 3)
        pygame.draw.line(screen, color, (head_x, self.y + 20), (head_x, self.y + 50), 4)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x - 18, self.y + 30), 4)
        pygame.draw.line(screen, color, (head_x, self.y + 30), (head_x + 18, self.y + 30), 4)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x - 12, self.y + 65), 4)
        pygame.draw.line(screen, color, (head_x, self.y + 50), (head_x + 12, self.y + 65), 4)
        
        eye_x = head_x + 6 if self.facing_right else head_x - 6
        pygame.draw.circle(screen, RED, (eye_x, head_y + 8), 3)
        
        pygame.draw.line(screen, DARK_RED, (head_x - 8, head_y - 5), (head_x - 15, head_y - 20), 3)
        pygame.draw.line(screen, DARK_RED, (head_x + 8, head_y - 5), (head_x + 15, head_y - 20), 3)
        
        bar_width = self.width
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)

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
        
        if is_player:
            self.frostmourne = Frostmourne()
            self.ice_shards = []
            self.gatling_bullets = []
        
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
            for bullet in self.gatling_bullets[:]:
                bullet.update()
                if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100:
                    self.gatling_bullets.remove(bullet)
    
    def shoot_gatling(self):
        if self.is_player and self.gatling_timer <= 0:
            self.gatling_timer = 4
            spread = random.uniform(-3, 3)
            if self.facing_right:
                bullet_x = self.x + self.width + 5
            else:
                bullet_x = self.x - 5
            bullet_y = self.y + self.height // 2
            direction = 1 if self.facing_right else -1
            bullet = GatlingBullet(bullet_x, bullet_y, direction, spread)
            self.gatling_bullets.append(bullet)
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
        if self.is_player:
            self.ice_shards.clear()
            self.gatling_bullets.clear()
    
    def fly(self):
        if self.can_fly and self.respawn_timer == 0:
            self.flying = True
            self.vel_y = -8
            self.on_ground = False
    
    def stop_fly(self):
        self.flying = False
    
    def use_frostmourne(self):
        if self.is_player and self.frostmourne.use():
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
        if self.on_ground and not self.frozen and self.respawn_timer == 0:
            self.vel_y = JUMP_POWER
            self.on_ground = False
    
    def attack(self):
        if (self.attack_cooldown <= 0 and not self.is_attacking 
            and not self.frozen and self.respawn_timer == 0):
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
            return pygame.Rect(self.x + self.width, self.y + 20, 60, 40)
        else:
            return pygame.Rect(self.x - 60, self.y + 20, 60, 40)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > SCREEN_WIDTH:
            return
        
        if self.respawn_timer > 0:
            if (self.respawn_timer // 5) % 2 == 0:
                return
        
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
                sword_end = (head_x + 85, self.y + 15 + math.sin(self.sword_angle * 0.1) * 5)
                pygame.draw.line(screen, SILVER, sword_start, sword_end, 6)
                pygame.draw.line(screen, BROWN, (head_x + 20, self.y + 28), (head_x + 25, self.y + 25), 4)
                pygame.draw.line(screen, GOLD, (head_x + 23, self.y + 22), (head_x + 27, self.y + 28), 3)
                pygame.draw.circle(screen, SILVER, (head_x + 85, self.y + 15), 4)
            else:
                sword_start = (head_x - 25, self.y + 25)
                sword_end = (head_x - 85, self.y + 15 + math.sin(self.sword_angle * 0.1) * 5)
                pygame.draw.line(screen, SILVER, sword_start, sword_end, 6)
                pygame.draw.line(screen, BROWN, (head_x - 20, self.y + 28), (head_x - 25, self.y + 25), 4)
                pygame.draw.line(screen, GOLD, (head_x - 23, self.y + 22), (head_x - 27, self.y + 28), 3)
                pygame.draw.circle(screen, SILVER, (head_x - 85, self.y + 15), 4)
        
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
                pygame.draw.rect(screen, DARK_GRAY, (screen_x + 20, self.y + 15, 15, 8))
                pygame.draw.circle(screen, GRAY, (screen_x + 35, self.y + 19), 5)
            else:
                pygame.draw.rect(screen, DARK_GRAY, (screen_x - 5, self.y + 15, 15, 8))
                pygame.draw.circle(screen, GRAY, (screen_x - 5, self.y + 19), 5)
        
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
            for bullet in self.gatling_bullets:
                bullet.draw(screen, camera_x)

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
        pygame.display.set_caption("Stickman - Endless Runner")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.screen_flash_timer = 0
        self.init_game()
    
    def init_game(self):
        self.player = StickMan(200, GROUND_Y - 60)
        self.boss_allies = []
        self.enemies = []
        self.platforms = []
        self.camera_x = 0
        self.game_over = False
        self.score = 0
        self.kill_count = 0
        self.death_count = 0
        self.spawn_timer = 0
        self.tutorial_text = "G = NUKE | F = Freeze | SPACE = Fly | J = Sword | HOLD K = Gatling"
        
        self.shake_timer = 0
        self.frost_effect_timer = 0
        
        # 创建平台（多个）
        for i in range(0, WORLD_WIDTH, 300):
            self.platforms.append(Platform(i, GROUND_Y, 200, 20, DARK_GRAY))
            if i > 200 and i % 600 == 0:
                self.platforms.append(Platform(i + 100, GROUND_Y - 80, 120, 20, BROWN))
            if i > 400 and i % 500 == 0:
                self.platforms.append(Platform(i + 200, GROUND_Y - 150, 100, 20, BROWN))
        
        # 初始3个BOSS小弟
        for i in range(3):
            ally = BossAlly(250 + i * 80, GROUND_Y - 60)
            self.boss_allies.append(ally)
        
        # 初始敌人
        for i in range(5):
            self.spawn_enemy(300 + i * 400)
    
    def spawn_enemy(self, x=None):
        if x is None:
            x = self.player.x + random.randint(300, 600)
            x = min(x, WORLD_WIDTH - 100)
        else:
            x = min(x, WORLD_WIDTH - 100)
        y = GROUND_Y - 70
        enemy_type = random.choice(["sword", "sniper", "plane", "tank"])
        new_enemy = Enemy(x, y, enemy_type)
        self.enemies.append(new_enemy)
    
    def nuclear_strike(self):
        self.screen_flash_timer = 8
        self.shake_timer = 15
        
        for enemy in self.enemies[:]:
            enemy.health = 0
            self.enemies.remove(enemy)
            self.score += 100
        
        for ally in self.boss_allies[:]:
            ally.health = 0
            self.boss_allies.remove(ally)
            self.score += 50
        
        while len(self.boss_allies) < 3:
            new_ally = BossAlly(self.player.x + random.randint(-100, 100), GROUND_Y - 60)
            self.boss_allies.append(new_ally)
        
        return True
    
    def frostmourne_aoe(self):
        for enemy in self.enemies[:]:
            if not enemy.frozen:
                enemy.take_damage(10, 1 if enemy.x < self.player.x else -1)
                enemy.freeze(90)
        
        for ally in self.boss_allies[:]:
            if not ally.frozen:
                ally.take_damage(10, 1 if ally.x < self.player.x else -1)
                ally.freeze(60)
        
        self.shake_timer = 8
        self.frost_effect_timer = 15
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.player.respawn_timer > 0:
            return
        
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
            self.player.shoot_gatling()
        
        if keys[pygame.K_g]:
            self.nuclear_strike()
    
    def check_collisions(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        # 玩家与敌人碰撞
        for enemy in self.enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect):
                if self.player.collision_damage_timer <= 0 and self.player.respawn_timer == 0:
                    self.player.health -= 10
                    self.player.collision_damage_timer = 30
        
        # 玩家近战攻击
        if self.player.is_attacking and self.player.attack_timer == 5:
            attack_rect = self.player.get_attack_rect()
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if attack_rect.colliderect(enemy_rect):
                    enemy.take_damage(40, 1 if enemy.x < self.player.x else -1)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
            for ally in self.boss_allies[:]:
                ally_rect = pygame.Rect(ally.x, ally.y, ally.width, ally.height)
                if attack_rect.colliderect(ally_rect):
                    ally.take_damage(30, 1 if ally.x < self.player.x else -1)
        
        # 玩家加特林子弹
        for bullet in self.player.gatling_bullets[:]:
            bullet_rect = bullet.get_rect()
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if bullet_rect.colliderect(enemy_rect):
                    enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                    if bullet in self.player.gatling_bullets:
                        self.player.gatling_bullets.remove(bullet)
                    break
        
        # 冰霜碎片
        for shard in self.player.ice_shards[:]:
            shard_rect = pygame.Rect(shard.x-3, shard.y-3, 6, 6)
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if shard_rect.colliderect(enemy_rect):
                    enemy.take_damage(15, 1 if enemy.x < shard.x else -1)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                    if shard in self.player.ice_shards:
                        self.player.ice_shards.remove(shard)
                    break
        
        # 敌人攻击和子弹
        for enemy in self.enemies:
            enemy.attack_player(self.player)
            for bullet in enemy.bullets[:]:
                bullet_rect = bullet.get_rect()
                if bullet_rect.colliderect(player_rect):
                    self.player.take_damage(bullet.damage, 1 if bullet.x < self.player.x else -1)
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
        
        # BOSS小弟子弹
        for ally in self.boss_allies:
            for bullet in ally.bullets[:]:
                bullet_rect = bullet.get_rect()
                if bullet_rect.colliderect(player_rect):
                    self.player.take_damage(bullet.damage, 1 if bullet.x < self.player.x else -1)
                    if bullet in ally.bullets:
                        ally.bullets.remove(bullet)
                for enemy in self.enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                        if bullet in ally.bullets:
                            ally.bullets.remove(bullet)
                        break
        
        # BOSS小弟冲锋伤害
        for ally in self.boss_allies:
            if ally.is_charging:
                ally_rect = pygame.Rect(ally.x, ally.y, ally.width, ally.height)
                if player_rect.colliderect(ally_rect):
                    if self.player.collision_damage_timer <= 0:
                        self.player.health -= 15
                        self.player.collision_damage_timer = 30
        
        self.boss_allies = [a for a in self.boss_allies if a.health > 0]
    
    def update(self):
        if self.game_over:
            return
        
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
        
        # 保持3个BOSS小弟
        if len(self.boss_allies) < 3:
            new_ally = BossAlly(self.player.x + random.randint(-100, 100), GROUND_Y - 60)
            self.boss_allies.append(new_ally)
        
        for ally in self.boss_allies:
            ally.update(self.platforms, self.enemies, self.player)
        
        for enemy in self.enemies:
            enemy.update(self.player, self.platforms, self.boss_allies)
        
        self.check_collisions()
        
        # 生成敌人
        self.spawn_timer += 1
        if self.spawn_timer > 120 and len(self.enemies) < 12:
            self.spawn_timer = 0
            self.spawn_enemy()
        
        # 相机跟随
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
        
        # 云朵
        for i in range(5):
            cloud_x = (i * 400 - self.camera_x * 0.3) % (SCREEN_WIDTH + 400) - 200
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 50))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 100, 60))
        
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        for ally in self.boss_allies:
            ally.draw(self.screen, self.camera_x)
        
        self.player.draw(self.screen, self.camera_x)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {max(0, self.player.health)}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, BLACK)
        self.screen.blit(enemies_text, (10, 130))
        
        allies_text = self.font.render(f"Allies: {len(self.boss_allies)}/3", True, DARK_RED)
        self.screen.blit(allies_text, (10, 170))
        
        deaths_text = self.font.render(f"Deaths: {self.death_count}/10", True, RED if self.death_count >= 7 else BLACK)
        self.screen.blit(deaths_text, (10, 210))
        
        nuke_text = self.font.render("NUKE: G", True, GREEN)
        self.screen.blit(nuke_text, (SCREEN_WIDTH - 150, 10))
        
        gatling_text = self.font.render("HOLD K", True, DARK_BLUE)
        self.screen.blit(gatling_text, (SCREEN_WIDTH - 150, 50))
        
        fly_text = self.font.render("SPACE = FLY", True, DARK_BLUE)
        self.screen.blit(fly_text, (SCREEN_WIDTH - 200, 90))
        
        self.player.frostmourne.draw_cd_icon(self.screen, SCREEN_WIDTH - 70, 130)
        
        skill_desc = self.font.render("F = Freeze", True, DARK_BLUE)
        self.screen.blit(skill_desc, (SCREEN_WIDTH - 200, 190))
        
        if self.player.respawn_timer > 0:
            respawn_text = self.font.render(f"RESPAWNING... {self.player.respawn_timer // 6 + 1}", True, RED)
            text_rect = respawn_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(respawn_text, text_rect)
        
        if self.kill_count < 5:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 350, 20))
        
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
