import pygame
import math
import random

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -12
GROUND_Y = 500

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
DARK_GREEN = (0, 100, 0)

class Rocket:
    """火箭弹类"""
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.direction = direction
        self.speed = 12
        self.size = 6
        self.damage = 50
        self.exploded = False
        self.explosion_timer = 0
        self.trail = []  # 尾迹效果
        self.angle = 0
        
    def update(self):
        if self.exploded:
            self.explosion_timer -= 1
            return
        
        # 记录尾迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # 移动
        self.x += self.direction * self.speed
        
        # 计算火箭角度（指向飞行方向）
        self.angle = 0 if self.direction > 0 else 180
        
        # 简单的抛物线效果（略微下坠）
        self.y += 0.5
        
        # 边界检查
        if self.x < -100 or self.x > SCREEN_WIDTH + 100:
            self.exploded = True
            self.explosion_timer = 10
    
    def explode(self):
        """触发爆炸"""
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 15
            return True
        return False
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        
        if self.exploded:
            # 绘制爆炸效果
            if self.explosion_timer > 0:
                explosion_radius = (15 - self.explosion_timer) * 2
                pygame.draw.circle(screen, ORANGE, (int(screen_x), int(self.y)), explosion_radius)
                pygame.draw.circle(screen, RED, (int(screen_x), int(self.y)), explosion_radius // 2)
                pygame.draw.circle(screen, YELLOW, (int(screen_x), int(self.y)), explosion_radius // 4)
            return
        
        # 绘制尾迹
        for i, (tx, ty) in enumerate(self.trail):
            alpha = i / len(self.trail)
            trail_x = tx - camera_x
            trail_size = int(3 * alpha)
            if trail_size > 0:
                pygame.draw.circle(screen, ORANGE, (int(trail_x), int(ty)), trail_size)
        
        # 绘制火箭弹体
        rocket_points = []
        if self.direction > 0:
            # 向右的火箭
            rocket_points = [
                (screen_x + self.size, self.y),           # 弹头
                (screen_x - self.size, self.y - 3),       # 尾翼上
                (screen_x - self.size, self.y + 3),       # 尾翼下
                (screen_x - self.size//2, self.y)         # 喷口
            ]
        else:
            # 向左的火箭
            rocket_points = [
                (screen_x - self.size, self.y),           # 弹头
                (screen_x + self.size, self.y - 3),       # 尾翼上
                (screen_x + self.size, self.y + 3),       # 尾翼下
                (screen_x + self.size//2, self.y)         # 喷口
            ]
        
        pygame.draw.polygon(screen, DARK_GRAY, rocket_points)
        # 弹头
        if self.direction > 0:
            pygame.draw.circle(screen, RED, (int(screen_x + self.size), int(self.y)), 3)
        else:
            pygame.draw.circle(screen, RED, (int(screen_x - self.size), int(self.y)), 3)
        
        # 火焰效果
        flame_size = random.randint(3, 6)
        if self.direction > 0:
            pygame.draw.circle(screen, ORANGE, (int(screen_x - self.size), int(self.y)), flame_size)
        else:
            pygame.draw.circle(screen, ORANGE, (int(screen_x + self.size), int(self.y)), flame_size)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)
    
    def get_explosion_rect(self):
        """爆炸范围（用于范围伤害）"""
        return pygame.Rect(self.x - 50, self.y - 50, 100, 100)

class RPG:
    """火箭筒类"""
    def __init__(self):
        self.reload_time = 0
        self.max_reload = 40  # 装填时间（帧）
        self.muzzle_flash = 0
        self.rockets = []  # 当前场景中的火箭弹
        
    def update(self):
        if self.reload_time > 0:
            self.reload_time -= 1
        if self.muzzle_flash > 0:
            self.muzzle_flash -= 1
        
        # 更新所有火箭弹
        for rocket in self.rockets[:]:
            rocket.update()
            if rocket.exploded and rocket.explosion_timer <= 0:
                self.rockets.remove(rocket)
    
    def can_shoot(self):
        return self.reload_time <= 0
    
    def shoot(self, x, y, direction):
        if self.can_shoot():
            self.reload_time = self.max_reload
            self.muzzle_flash = 5
            rocket = Rocket(x, y, direction)
            self.rockets.append(rocket)
            return rocket
        return None
    
    def draw(self, screen, x, y, facing_right, camera_x=0):
        screen_x = x - camera_x
        
        # 火箭筒主体
        if facing_right:
            # 炮管
            pygame.draw.rect(screen, DARK_GREEN, (screen_x + 20, y + 25, 35, 10))
            # 瞄准镜
            pygame.draw.rect(screen, GRAY, (screen_x + 45, y + 20, 8, 8))
            pygame.draw.circle(screen, BLUE, (screen_x + 49, y + 24), 2)
            # 肩托
            pygame.draw.rect(screen, BROWN, (screen_x + 10, y + 28, 15, 4))
            # 握把
            pygame.draw.rect(screen, DARK_GRAY, (screen_x + 25, y + 35, 6, 8))
            
            # 炮口火焰
            if self.muzzle_flash > 0:
                flash_size = random.randint(8, 15)
                pygame.draw.circle(screen, ORANGE, (screen_x + 55, y + 30), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x + 55, y + 30), flash_size // 2)
                # 烟雾
                pygame.draw.circle(screen, GRAY, (screen_x + 60, y + 28), flash_size // 2)
        else:
            # 向左的火箭筒
            pygame.draw.rect(screen, DARK_GREEN, (screen_x - 15, y + 25, 35, 10))
            pygame.draw.rect(screen, GRAY, (screen_x - 13, y + 20, 8, 8))
            pygame.draw.circle(screen, BLUE, (screen_x - 9, y + 24), 2)
            pygame.draw.rect(screen, BROWN, (screen_x - 5, y + 28, 15, 4))
            pygame.draw.rect(screen, DARK_GRAY, (screen_x - 1, y + 35, 6, 8))
            
            if self.muzzle_flash > 0:
                flash_size = random.randint(8, 15)
                pygame.draw.circle(screen, ORANGE, (screen_x - 15, y + 30), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x - 15, y + 30), flash_size // 2)
                pygame.draw.circle(screen, GRAY, (screen_x - 20, y + 28), flash_size // 2)

class StickMan:
    def __init__(self, x, y, color=BLACK, is_player=True):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.on_ground = True
        self.facing_right = True
        self.health = 100 if is_player else 50
        self.max_health = self.health
        self.is_player = is_player
        self.color = color
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_timer = 0
        self.knockback_timer = 0
        self.width = 30
        self.height = 60
        
        # 玩家特有的火箭筒
        if is_player:
            self.rpg = RPG()
        else:
            self.rpg = None
        
    def update(self, platforms, enemies=None):
        # 应用速度
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 重力
        self.vel_y += GRAVITY
        
        # 地面碰撞
        if self.y + self.height >= GROUND_Y:
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
        
        # 边界限制
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        
        # 更新攻击计时
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        # 更新击退计时
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        # 更新火箭筒
        if self.is_player and self.rpg:
            self.rpg.update()
    
    def shoot_rpg(self):
        """发射火箭弹"""
        if self.is_player and self.rpg:
            rocket_x = self.x + self.width if self.facing_right else self.x
            rocket_y = self.y + self.height // 2
            direction = 1 if self.facing_right else -1
            return self.rpg.shoot(rocket_x, rocket_y, direction)
        return None
    
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
    
    def attack(self):
        if self.attack_cooldown <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = 30
            return True
        return False
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def get_attack_rect(self):
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20, 40, 40)
        else:
            return pygame.Rect(self.x - 40, self.y + 20, 40, 40)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        
        # 身体各部分的坐标
        head_x = screen_x + self.width // 2
        head_y = self.y
        body_top = (head_x, self.y + 20)
        body_bottom = (head_x, self.y + 50)
        
        # 手臂坐标
        if self.is_attacking:
            if self.facing_right:
                left_arm = (head_x - 10, self.y + 30)
                right_arm = (head_x + 30, self.y + 25)
            else:
                left_arm = (head_x - 30, self.y + 25)
                right_arm = (head_x + 10, self.y + 30)
        else:
            left_arm = (head_x - 15, self.y + 30)
            right_arm = (head_x + 15, self.y + 30)
        
        # 腿部坐标
        if abs(self.vel_x) > 1 and self.on_ground:
            leg_offset = 5 * math.sin(pygame.time.get_ticks() * 0.01)
            left_leg = (head_x - 10, self.y + 60 + leg_offset)
            right_leg = (head_x + 10, self.y + 60 - leg_offset)
        else:
            left_leg = (head_x - 10, self.y + 60)
            right_leg = (head_x + 10, self.y + 60)
        
        # 绘制身体线条
        color = self.color if self.knockback_timer <= 0 else RED
        pygame.draw.circle(screen, color, (head_x, head_y + 10), 12, 3)
        pygame.draw.line(screen, color, body_top, body_bottom, 3)
        pygame.draw.line(screen, color, body_top, left_arm, 3)
        pygame.draw.line(screen, color, body_top, right_arm, 3)
        pygame.draw.line(screen, color, body_bottom, left_leg, 3)
        pygame.draw.line(screen, color, body_bottom, right_leg, 3)
        
        # 绘制眼睛
        if self.facing_right:
            eye_x = head_x + 5
        else:
            eye_x = head_x - 5
        pygame.draw.circle(screen, BLACK, (eye_x, head_y + 8), 2)
        
        # 绘制火箭筒（玩家专用）
        if self.is_player and self.rpg:
            self.rpg.draw(screen, screen_x, self.y, self.facing_right, camera_x)
        elif self.is_attacking:
            # 敌人的近战武器
            if self.facing_right:
                weapon_end = (head_x + 50, self.y + 25)
            else:
                weapon_end = (head_x - 50, self.y + 25)
            pygame.draw.line(screen, RED, right_arm, weapon_end, 4)
        
        # 绘制血条
        bar_width = 40
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))

class Enemy(StickMan):
    def __init__(self, x, y):
        super().__init__(x, y, RED, False)
        self.speed = 2
        self.patrol_left = x - 100
        self.patrol_right = x + 100
        self.ai_timer = 0
    
    def update_ai(self, player, platforms):
        distance = player.x - self.x
        
        if abs(distance) < 200 and not self.knockback_timer:
            if distance > 0:
                self.vel_x = self.speed
                self.facing_right = True
            else:
                self.vel_x = -self.speed
                self.facing_right = False
            
            if abs(distance) < 50 and self.attack_cooldown <= 0:
                self.attack()
        else:
            if self.ai_timer <= 0:
                self.vel_x = random.choice([-self.speed, self.speed])
                self.ai_timer = random.randint(60, 180)
            else:
                self.ai_timer -= 1
            
            if self.x < self.patrol_left:
                self.vel_x = self.speed
                self.facing_right = True
            elif self.x > self.patrol_right:
                self.vel_x = -self.speed
                self.facing_right = False
        
        super().update(platforms)
        
        if self.is_attacking and self.attack_timer == 5:
            attack_rect = self.get_attack_rect()
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            if attack_rect.colliderect(player_rect):
                player.take_damage(10, -1 if player.x < self.x else 1)

class Platform:
    def __init__(self, x, y, width, height, color=BROWN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        pygame.draw.rect(screen, self.color, (screen_x, self.y, self.width, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stickman Battle - RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.init_game()
    
    def init_game(self):
        self.player = StickMan(100, GROUND_Y - 60)
        self.enemies = []
        self.platforms = []
        self.camera_x = 0
        self.game_over = False
        self.win = False
        self.score = 0
        self.kill_count = 0
        self.reload_display = 0
        self.tutorial_text = "SPACE=Jump  K=Rocket  J=Melee"
        
        # 创建平台
        self.platforms.append(Platform(0, GROUND_Y, SCREEN_WIDTH * 2, 20, DARK_GRAY))
        self.platforms.append(Platform(200, 450, 100, 20))
        self.platforms.append(Platform(500, 400, 100, 20))
        self.platforms.append(Platform(800, 350, 100, 20))
        self.platforms.append(Platform(1100, 450, 100, 20))
        
        # 创建敌人
        self.create_enemies()
    
    def create_enemies(self):
        enemy_positions = [(300, GROUND_Y - 60), (600, 360), (900, 310), (1200, 410)]
        for x, y in enemy_positions:
            self.enemies.append(Enemy(x, y))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.game_over and not self.win:
            # 移动
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            else:
                self.player.vel_x *= 0.8
            
            # 火箭筒（单发，按K键发射）
            # 在事件循环中处理按键，避免连发
    
    def handle_collisions(self):
        # 玩家近战攻击判定
        if self.player.is_attacking and self.player.attack_timer == 5:
            attack_rect = self.player.get_attack_rect()
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if attack_rect.colliderect(enemy_rect):
                    enemy.take_damage(25, 1 if enemy.x < self.player.x else -1)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
        
        # 火箭弹碰撞检测
        if self.player.rpg:
            for rocket in self.player.rpg.rockets[:]:
                # 检查与敌人的碰撞
                hit = False
                for enemy in self.enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if not rocket.exploded and rocket.get_rect().colliderect(enemy_rect):
                        rocket.explode()
                        hit = True
                        
                        # 范围伤害（爆炸半径内所有敌人受伤）
                        explosion_rect = rocket.get_explosion_rect()
                        for enemy2 in self.enemies[:]:
                            enemy2_rect = pygame.Rect(enemy2.x, enemy2.y, enemy2.width, enemy2.height)
                            if explosion_rect.colliderect(enemy2_rect):
                                enemy2.take_damage(rocket.damage, 1 if enemy2.x < rocket.x else -1)
                                if enemy2.health <= 0:
                                    self.enemies.remove(enemy2)
                                    self.score += 100
                                    self.kill_count += 1
                        break
                
                # 检查与平台的碰撞
                if not rocket.exploded and not hit:
                    for platform in self.platforms:
                        platform_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
                        if rocket.get_rect().colliderect(platform_rect):
                            rocket.explode()
                            break
                        
                        # 简化版：检查火箭弹附近是否有平台（爆炸效果）
                        dist_to_platform = abs(rocket.x - platform.x)
                        if dist_to_platform < 30 and rocket.y + rocket.size > platform.y and rocket.y - rocket.size < platform.y + platform.height:
                            rocket.explode()
                            break
    
    def update(self):
        self.player.update(self.platforms)
        
        for enemy in self.enemies:
            enemy.update_ai(self.player, self.platforms)
        
        self.handle_collisions()
        
        self.camera_x = self.player.x - SCREEN_WIDTH // 2 + self.player.width // 2
        self.camera_x = max(0, min(self.camera_x, SCREEN_WIDTH * 2 - SCREEN_WIDTH))
        
        if self.kill_count >= 4:
            self.win = True
        
        if self.player.health <= 0:
            self.game_over = True
        
        # 更新装填显示
        if self.player.rpg:
            self.reload_display = self.player.rpg.reload_time
    
    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        # 绘制云朵
        for i in range(3):
            cloud_x = (i * 300 - self.camera_x * 0.5) % (SCREEN_WIDTH + 200) - 100
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 50))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 100, 60))
        
        # 绘制平台
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # 绘制玩家
        self.player.draw(self.screen, self.camera_x)
        
        # 绘制火箭弹（独立绘制）
        if self.player.rpg:
            for rocket in self.player.rpg.rockets:
                rocket.draw(self.screen, self.camera_x)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}/4", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        # 火箭筒装填显示
        if self.player.rpg:
            if self.reload_display > 0:
                reload_text = self.font.render(f"Reloading: {self.reload_display//6 + 1}", True, RED)
                self.screen.blit(reload_text, (SCREEN_WIDTH - 150, 10))
                # 装填进度条
                reload_percent = 1 - (self.reload_display / self.player.rpg.max_reload)
                pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 150, 35, 100, 10))
                pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 150, 35, 100 * reload_percent, 10))
            else:
                ready_text = self.font.render("READY", True, GREEN)
                self.screen.blit(ready_text, (SCREEN_WIDTH - 150, 10))
        
        if self.kill_count == 0:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 200, 20))
        
        # 游戏结束/胜利画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        elif self.win:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            win_text = self.big_font.render("VICTORY!", True, GREEN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(win_text, text_rect)
            
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Press R to play again or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over and not self.win:
                        self.player.jump()
                    
                    elif event.key == pygame.K_k and not self.game_over and not self.win:
                        # 发射火箭弹
                        self.player.shoot_rpg()
                    
                    elif event.key == pygame.K_j and not self.game_over and not self.win:
                        self.player.attack()
                    
                    elif event.key == pygame.K_r and (self.game_over or self.win):
                        self.init_game()
                    
                    elif event.key == pygame.K_q and (self.game_over or self.win):
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
