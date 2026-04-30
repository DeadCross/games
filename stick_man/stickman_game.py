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
METAL = (169, 169, 169)
DARK_METAL = (105, 105, 105)

class GatlingBullet:
    """加特林子弹"""
    def __init__(self, x, y, direction, angle_offset=0):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 20
        self.size = 3
        self.damage = 10
        self.angle_offset = angle_offset  # 子弹散布
        
    def update(self):
        # 主方向移动
        self.x += self.direction * self.speed
        # 散布效果
        self.y += self.angle_offset * 2
        
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        # 曳光弹效果 - 拉长的子弹
        if self.direction > 0:
            pygame.draw.line(screen, YELLOW, 
                           (int(screen_x - 5), int(self.y)),
                           (int(screen_x + 5), int(self.y)), 2)
            pygame.draw.circle(screen, ORANGE, (int(screen_x + 3), int(self.y)), 2)
        else:
            pygame.draw.line(screen, YELLOW,
                           (int(screen_x + 5), int(self.y)),
                           (int(screen_x - 5), int(self.y)), 2)
            pygame.draw.circle(screen, ORANGE, (int(screen_x - 3), int(self.y)), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 2, 10, 4)

class GatlingGun:
    """真正的加特林机枪"""
    def __init__(self):
        self.barrels = 6  # 6根枪管
        self.rotation = 0  # 枪管旋转角度
        self.rotation_speed = 15  # 旋转速度
        self.fire_rate = 3  # 每3帧射一发
        self.shoot_timer = 0
        self.bullets = []
        self.muzzle_flash = 0
        self.spread = 3  # 子弹散布范围
        self.barrel_heats = [0] * 6  # 枪管热度（视觉效果）
        
    def update(self):
        # 枪管持续旋转
        self.rotation = (self.rotation + self.rotation_speed) % 360
        
        # 冷却枪管
        for i in range(len(self.barrel_heats)):
            if self.barrel_heats[i] > 0:
                self.barrel_heats[i] -= 1
        
        # 更新射击计时
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        # 更新枪口火焰
        if self.muzzle_flash > 0:
            self.muzzle_flash -= 1
        
        # 更新所有子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < -100 or bullet.x > SCREEN_WIDTH + 100:
                self.bullets.remove(bullet)
    
    def shoot(self, x, y, facing_right):
        """射击"""
        if self.shoot_timer <= 0:
            self.shoot_timer = self.fire_rate
            self.muzzle_flash = 4
            
            # 当前射击的是哪根枪管
            current_barrel = int(self.rotation / 60) % 6
            self.barrel_heats[current_barrel] = 20  # 枪管发热
            
            # 子弹散布（越热的枪管散布越大）
            spread = self.spread + sum(self.barrel_heats) / 20
            
            # 创建子弹，带散布角度
            angle_offset = random.uniform(-spread, spread) / 10
            
            bullet_x = x + 25 if facing_right else x - 25
            bullet_y = y + 28 + angle_offset * 5
            direction = 1 if facing_right else -1
            
            # 连发两颗子弹（增加弹幕密度）
            bullet = GatlingBullet(bullet_x, bullet_y, direction, angle_offset)
            self.bullets.append(bullet)
            
            # 偶尔双发
            if random.random() < 0.3:
                bullet2 = GatlingBullet(bullet_x, bullet_y + random.uniform(-3, 3), 
                                       direction, angle_offset + random.uniform(-1, 1))
                self.bullets.append(bullet2)
            
            return True
        return False
    
    def draw(self, screen, x, y, facing_right, camera_x=0):
        screen_x = x - camera_x
        
        if facing_right:
            # 加特林主体
            # 电机外壳
            pygame.draw.rect(screen, DARK_METAL, (screen_x + 20, y + 22, 15, 20))
            # 握把
            pygame.draw.rect(screen, DARK_GRAY, (screen_x + 10, y + 35, 12, 8))
            pygame.draw.rect(screen, BLACK, (screen_x + 12, y + 43, 8, 6))
            # 弹药箱
            pygame.draw.rect(screen, METAL, (screen_x + 30, y + 15, 20, 15))
            pygame.draw.rect(screen, BROWN, (screen_x + 35, y + 18, 10, 9))
            
            # 多根枪管（旋转效果）
            for i in range(6):
                angle_rad = math.radians(self.rotation + i * 60)
                radius = 8
                barrel_x = screen_x + 38 + int(math.cos(angle_rad) * radius)
                barrel_y = y + 32 + int(math.sin(angle_rad) * radius)
                
                # 根据热度改变枪管颜色
                if self.barrel_heats[i] > 15:
                    barrel_color = RED
                elif self.barrel_heats[i] > 8:
                    barrel_color = ORANGE
                elif self.barrel_heats[i] > 3:
                    barrel_color = (255, 100, 0)
                else:
                    barrel_color = DARK_METAL
                
                pygame.draw.circle(screen, barrel_color, (barrel_x, barrel_y), 4)
                pygame.draw.circle(screen, METAL, (barrel_x, barrel_y), 3)
            
            # 中心轴
            pygame.draw.circle(screen, METAL, (screen_x + 38, y + 32), 6)
            pygame.draw.circle(screen, DARK_METAL, (screen_x + 38, y + 32), 3)
            
            # 枪口火焰
            if self.muzzle_flash > 0:
                flash_size = random.randint(8, 15)
                # 主火焰
                pygame.draw.circle(screen, ORANGE, (screen_x + 55, y + 30), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x + 55, y + 30), flash_size - 3)
                pygame.draw.circle(screen, WHITE, (screen_x + 55, y + 30), flash_size - 6)
                # 火花飞溅
                for _ in range(5):
                    sx = screen_x + 55 + random.randint(-5, 5)
                    sy = y + 30 + random.randint(-5, 5)
                    pygame.draw.circle(screen, RED, (sx, sy), random.randint(1, 2))
        else:
            # 向左的加特林（镜像）
            pygame.draw.rect(screen, DARK_METAL, (screen_x - 5, y + 22, 15, 20))
            pygame.draw.rect(screen, DARK_GRAY, (screen_x - 2, y + 35, 12, 8))
            pygame.draw.rect(screen, BLACK, (screen_x, y + 43, 8, 6))
            pygame.draw.rect(screen, METAL, (screen_x - 20, y + 15, 20, 15))
            pygame.draw.rect(screen, BROWN, (screen_x - 15, y + 18, 10, 9))
            
            for i in range(6):
                angle_rad = math.radians(self.rotation + i * 60)
                radius = 8
                barrel_x = screen_x - 18 + int(math.cos(angle_rad - math.pi) * radius)
                barrel_y = y + 32 + int(math.sin(angle_rad) * radius)
                
                if self.barrel_heats[i] > 15:
                    barrel_color = RED
                elif self.barrel_heats[i] > 8:
                    barrel_color = ORANGE
                else:
                    barrel_color = DARK_METAL
                
                pygame.draw.circle(screen, barrel_color, (barrel_x, barrel_y), 4)
                pygame.draw.circle(screen, METAL, (barrel_x, barrel_y), 3)
            
            pygame.draw.circle(screen, METAL, (screen_x - 18, y + 32), 6)
            pygame.draw.circle(screen, DARK_METAL, (screen_x - 18, y + 32), 3)
            
            if self.muzzle_flash > 0:
                flash_size = random.randint(8, 15)
                pygame.draw.circle(screen, ORANGE, (screen_x - 25, y + 30), flash_size)
                pygame.draw.circle(screen, YELLOW, (screen_x - 25, y + 30), flash_size - 3)
                pygame.draw.circle(screen, WHITE, (screen_x - 25, y + 30), flash_size - 6)
                for _ in range(5):
                    sx = screen_x - 25 + random.randint(-5, 5)
                    sy = y + 30 + random.randint(-5, 5)
                    pygame.draw.circle(screen, RED, (sx, sy), random.randint(1, 2))

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
        
        # 玩家特有的加特林
        if is_player:
            self.gatling = GatlingGun()
        
    def update(self, platforms, enemies=None):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY
        
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
        
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        if self.is_player and hasattr(self, 'gatling'):
            self.gatling.update()
    
    def shoot_gatling(self):
        """使用加特林射击"""
        if self.is_player and hasattr(self, 'gatling'):
            if self.facing_right:
                gun_x = self.x + self.width
            else:
                gun_x = self.x
            gun_y = self.y
            return self.gatling.shoot(gun_x, gun_y, self.facing_right)
        return False
    
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
        
        head_x = screen_x + self.width // 2
        head_y = self.y
        body_top = (head_x, self.y + 20)
        body_bottom = (head_x, self.y + 50)
        
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
        
        if abs(self.vel_x) > 1 and self.on_ground:
            leg_offset = 5 * math.sin(pygame.time.get_ticks() * 0.01)
            left_leg = (head_x - 10, self.y + 60 + leg_offset)
            right_leg = (head_x + 10, self.y + 60 - leg_offset)
        else:
            left_leg = (head_x - 10, self.y + 60)
            right_leg = (head_x + 10, self.y + 60)
        
        color = self.color if self.knockback_timer <= 0 else RED
        pygame.draw.circle(screen, color, (head_x, head_y + 10), 12, 3)
        pygame.draw.line(screen, color, body_top, body_bottom, 3)
        pygame.draw.line(screen, color, body_top, left_arm, 3)
        pygame.draw.line(screen, color, body_top, right_arm, 3)
        pygame.draw.line(screen, color, body_bottom, left_leg, 3)
        pygame.draw.line(screen, color, body_bottom, right_leg, 3)
        
        if self.facing_right:
            eye_x = head_x + 5
        else:
            eye_x = head_x - 5
        pygame.draw.circle(screen, BLACK, (eye_x, head_y + 8), 2)
        
        # 绘制加特林
        if self.is_player and hasattr(self, 'gatling'):
            self.gatling.draw(screen, screen_x, self.y, self.facing_right, camera_x)
        
        # 血条
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
        pygame.display.set_caption("Stickman Battle - GATLING GUN")
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
        self.shoot_hold = False
        self.tutorial_text = "HOLD K = GATLING!  SPACE=Jump  J=Melee"
        
        self.platforms.append(Platform(0, GROUND_Y, SCREEN_WIDTH * 2, 20, DARK_GRAY))
        self.platforms.append(Platform(200, 450, 100, 20))
        self.platforms.append(Platform(500, 400, 100, 20))
        self.platforms.append(Platform(800, 350, 100, 20))
        self.platforms.append(Platform(1100, 450, 100, 20))
        
        self.create_enemies()
    
    def create_enemies(self):
        enemy_positions = [(300, GROUND_Y - 60), (600, 360), (900, 310), (1200, 410)]
        for x, y in enemy_positions:
            self.enemies.append(Enemy(x, y))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.game_over and not self.win:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            else:
                self.player.vel_x *= 0.8
            
            # 加特林连射（按住K键）
            if keys[pygame.K_k]:
                self.player.shoot_gatling()
    
    def handle_collisions(self):
        # 近战攻击
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
        
        # 加特林子弹
        if hasattr(self.player, 'gatling'):
            for bullet in self.player.gatling.bullets[:]:
                for enemy in self.enemies[:]:
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if bullet.get_rect().colliderect(enemy_rect):
                        enemy.take_damage(bullet.damage, 1 if enemy.x < bullet.x else -1)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.score += 100
                            self.kill_count += 1
                        if bullet in self.player.gatling.bullets:
                            self.player.gatling.bullets.remove(bullet)
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
    
    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        for i in range(3):
            cloud_x = (i * 300 - self.camera_x * 0.5) % (SCREEN_WIDTH + 200) - 100
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 50))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 100, 60))
        
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        self.player.draw(self.screen, self.camera_x)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}/4", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        # 弹药显示
        if hasattr(self.player, 'gatling'):
            ammo_text = self.font.render("GATLING: HOLD K", True, BLACK)
            self.screen.blit(ammo_text, (SCREEN_WIDTH - 200, 10))
            
            # 枪管热度指示器
            heat_sum = sum(self.player.gatling.barrel_heats)
            if heat_sum > 50:
                heat_color = RED
                heat_text = "OVERHEAT!"
            elif heat_sum > 30:
                heat_color = ORANGE
                heat_text = "HOT"
            else:
                heat_color = GREEN
                heat_text = "COOL"
            
            heat_display = self.font.render(heat_text, True, heat_color)
            self.screen.blit(heat_display, (SCREEN_WIDTH - 200, 50))
        
        if self.kill_count == 0:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 250, 20))
        
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
