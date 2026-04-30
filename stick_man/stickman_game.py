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
ICE_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (100, 149, 237)
PURPLE = (138, 43, 226)

class Frostmourne:
    """霜之哀伤 - 全屏冰霜技能"""
    def __init__(self):
        self.cooldown = 0
        self.max_cooldown = 180  # 3秒CD (60fps * 3)
        self.active = False
        self.duration = 30  # 技能持续时间0.5秒
        self.timer = 0
        self.skill_ready = True
        
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            self.skill_ready = False
        else:
            self.skill_ready = True
        
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
    
    def use(self):
        """使用霜之哀伤技能"""
        if self.skill_ready and not self.active:
            self.cooldown = self.max_cooldown
            self.active = True
            self.timer = self.duration
            return True
        return False
    
    def draw_cd_icon(self, screen, x, y):
        """绘制技能冷却图标"""
        # 技能图标背景
        pygame.draw.rect(screen, DARK_GRAY, (x, y, 50, 50))
        pygame.draw.rect(screen, ICE_BLUE, (x+2, y+2, 46, 46))
        
        # 绘制霜之哀伤小图标
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
        
        # 冷却遮罩
        if not self.skill_ready:
            cooldown_percent = self.cooldown / self.max_cooldown
            # 创建半透明遮罩
            mask = pygame.Surface((50, 50))
            mask.set_alpha(128)
            mask.fill(BLACK)
            screen.blit(mask, (x, y))
            # 绘制冷却进度
            pygame.draw.rect(screen, (0, 0, 0, 128), 
                           (x, y, 50, 50 * cooldown_percent))
            
            # 显示冷却时间数字
            cd_seconds = (self.cooldown // 60) + 1
            font = pygame.font.Font(None, 20)
            cd_text = font.render(str(cd_seconds), True, WHITE)
            screen.blit(cd_text, (x+18, y+15))

class IceShard:
    """冰霜碎片"""
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = 30
        
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
        self.frozen = False
        self.frozen_timer = 0
        
        # 玩家的霜之哀伤
        if is_player:
            self.frostmourne = Frostmourne()
            self.ice_shards = []
        
    def update(self, platforms, enemies=None):
        # 冰冻效果
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
            # 冰冻时无法移动
            if not self.is_player:
                super().update(platforms)
                return
        
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
        
        # 更新霜之哀伤
        if self.is_player:
            self.frostmourne.update()
            # 更新冰霜碎片
            for shard in self.ice_shards[:]:
                if not shard.update():
                    self.ice_shards.remove(shard)
    
    def use_frostmourne(self):
        """使用霜之哀伤 - 全屏冰霜"""
        if self.is_player and self.frostmourne.use():
            # 创建冰霜碎片特效
            for _ in range(50):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                shard = IceShard(self.x + self.width//2, self.y + self.height//2, vx, vy)
                self.ice_shards.append(shard)
            return True
        return False
    
    def jump(self):
        if self.on_ground and not self.frozen:
            self.vel_y = JUMP_POWER
            self.on_ground = False
    
    def attack(self):
        if self.attack_cooldown <= 0 and not self.is_attacking and not self.frozen:
            self.is_attacking = True
            self.attack_timer = 10
            self.attack_cooldown = 30
            return True
        return False
    
    def take_damage(self, damage, knockback_dir):
        if self.knockback_timer <= 0 and not self.frozen:
            self.health -= damage
            self.knockback_timer = 20
            self.vel_x = knockback_dir * 8
            self.vel_y = -5
            return True
        return False
    
    def freeze(self, duration=60):
        """冰冻敌人"""
        if not self.is_player:
            self.frozen = True
            self.frozen_timer = duration
            self.vel_x = 0
            self.vel_y = 0
    
    def get_attack_rect(self):
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y + 20, 40, 40)
        else:
            return pygame.Rect(self.x - 40, self.y + 20, 40, 40)
    
    def draw(self, screen, camera_x=0):
        screen_x = self.x - camera_x
        
        # 冰冻效果（蓝色外框）
        if self.frozen:
            pygame.draw.rect(screen, ICE_BLUE, (screen_x-2, self.y-2, self.width+4, self.height+4), 2)
        
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
        if abs(self.vel_x) > 1 and self.on_ground and not self.frozen:
            leg_offset = 5 * math.sin(pygame.time.get_ticks() * 0.01)
            left_leg = (head_x - 10, self.y + 60 + leg_offset)
            right_leg = (head_x + 10, self.y + 60 - leg_offset)
        else:
            left_leg = (head_x - 10, self.y + 60)
            right_leg = (head_x + 10, self.y + 60)
        
        # 绘制身体线条
        color = self.color if self.knockback_timer <= 0 else RED
        if self.frozen:
            color = ICE_BLUE
        
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
        
        # 绘制霜之哀伤激活光环
        if self.is_player and self.frostmourne.active:
            for i in range(3):
                radius = 30 + i * 10
                alpha = 100 - i * 30
                color = (173, 216, 230, alpha)
                pygame.draw.circle(screen, ICE_BLUE, (head_x, head_y + 30), radius, 2)
        
        # 绘制血条
        bar_width = 40
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        # 绘制冰霜碎片
        if self.is_player:
            for shard in self.ice_shards:
                shard.draw(screen, camera_x)

class Enemy(StickMan):
    def __init__(self, x, y):
        super().__init__(x, y, RED, False)
        self.speed = 2
        self.patrol_left = x - 100
        self.patrol_right = x + 100
        self.ai_timer = 0
    
    def update_ai(self, player, platforms):
        # 如果被冰冻，不更新AI
        if self.frozen:
            super().update(platforms)
            return
        
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
        
        # 攻击判定
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
        pygame.display.set_caption("Stickman - Frostmourne")
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
        self.tutorial_text = "F = FROSTMOURNE! (Full screen ice)"
        
        # 特效计时器
        self.shake_timer = 0
        self.frost_effect_timer = 0
        
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
    
    def frostmourne_aoe(self):
        """霜之哀伤全屏伤害"""
        # 对所有敌人造成伤害并冰冻
        for enemy in self.enemies[:]:
            # 全屏伤害50点
            enemy.take_damage(50, 1 if enemy.x < self.player.x else -1)
            # 冰冻2秒
            enemy.freeze(120)
            
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += 100
                self.kill_count += 1
        
        # 屏幕震动效果
        self.shake_timer = 10
        
        # 播放冰霜特效
        self.frost_effect_timer = 20
    
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
    
    def handle_collisions(self):
        # 玩家攻击判定
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
        
        # 冰霜碎片碰撞
        for shard in self.player.ice_shards[:]:
            shard_rect = pygame.Rect(shard.x-3, shard.y-3, 6, 6)
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if shard_rect.colliderect(enemy_rect):
                    enemy.take_damage(10, 1 if enemy.x < shard.x else -1)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                        self.kill_count += 1
                    if shard in self.player.ice_shards:
                        self.player.ice_shards.remove(shard)
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
        
        # 更新特效计时器
        if self.shake_timer > 0:
            self.shake_timer -= 1
        
        if self.frost_effect_timer > 0:
            self.frost_effect_timer -= 1
    
    def draw(self):
        # 屏幕震动偏移
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
        
        # 天空背景（冰霜特效时变蓝）
        if self.frost_effect_timer > 0:
            self.screen.fill((150, 200, 255))
        else:
            self.screen.fill(SKY_BLUE)
        
        # 绘制冰霜特效（全屏冰花）
        if self.frost_effect_timer > 0:
            for _ in range(50):
                fx = random.randint(0, SCREEN_WIDTH)
                fy = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (fx, fy), random.randint(1, 3))
        
        # 绘制云朵
        for i in range(3):
            cloud_x = (i * 300 - self.camera_x * 0.5) % (SCREEN_WIDTH + 200) - 100 + shake_x
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
        
        # UI文字（不受震动影响）
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}/4", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        # 霜之哀伤技能图标
        self.player.frostmourne.draw_cd_icon(self.screen, SCREEN_WIDTH - 70, 10)
        
        # 技能说明
        skill_desc = self.font.render("F = Frostmourne", True, DARK_BLUE)
        self.screen.blit(skill_desc, (SCREEN_WIDTH - 200, 70))
        
        if self.kill_count == 0:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 250, 20))
        
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
                    
                    elif event.key == pygame.K_j and not self.game_over and not self.win:
                        self.player.attack()
                    
                    # 霜之哀伤！按F键
                    elif event.key == pygame.K_f and not self.game_over and not self.win:
                        if self.player.use_frostmourne():
                            self.frostmourne_aoe()
                    
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
