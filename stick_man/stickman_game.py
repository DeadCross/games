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
    """霜之哀伤 - 冰冻技能"""
    def __init__(self):
        self.cooldown = 0
        self.max_cooldown = 90  # 1.5秒CD
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
    """冰霜碎片"""
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
        self.can_fly = True  # 所有火柴人都能飞
        self.flying = False
        self.on_ground = True
        self.facing_right = True
        self.health = 100 if is_player else 30
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
        
        if is_player:
            self.frostmourne = Frostmourne()
            self.ice_shards = []
        
    def update(self, platforms):
        # 冰冻效果
        if self.frozen:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.frozen = False
                # 解除冰冻后恢复正常颜色
            if not self.is_player:
                # 冰冻时不能移动
                self.vel_x = 0
                self.vel_y = 0
                return
        
        # 飞行控制
        if self.flying:
            # 飞行时重力减小
            self.vel_y += GRAVITY * 0.3
            # 飞行时速度更快
            if abs(self.vel_x) < self.speed * 1.5:
                pass
        else:
            self.vel_y += GRAVITY
        
        # 应用速度
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 地面碰撞
        if self.y + self.height >= GROUND_Y:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.flying = False
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
                self.flying = False
        
        # 边界限制
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y + self.height > SCREEN_HEIGHT:
            self.health = 0
        
        # 更新攻击计时
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.is_attacking = False
        
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
        
        if self.is_player:
            self.frostmourne.update()
            for shard in self.ice_shards[:]:
                if not shard.update():
                    self.ice_shards.remove(shard)
    
    def fly(self):
        """飞行功能"""
        if self.can_fly:
            self.flying = True
            self.vel_y = -8
            self.on_ground = False
    
    def stop_fly(self):
        """停止飞行"""
        self.flying = False
    
    def use_frostmourne(self):
        if self.is_player and self.frostmourne.use():
            # 创建冰霜碎片特效
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
    
    def freeze(self, duration=90):
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
        
        # 冰冻效果
        if self.frozen:
            pygame.draw.rect(screen, ICE_BLUE, (screen_x-2, self.y-2, self.width+4, self.height+4), 3)
        
        # 飞行效果（翅膀）
        if self.flying and not self.frozen:
            wing_color = (200, 200, 200, 100)
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
        
        # 身体各部分
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
        
        if abs(self.vel_x) > 1 and self.on_ground and not self.frozen:
            leg_offset = 5 * math.sin(pygame.time.get_ticks() * 0.01)
            left_leg = (head_x - 10, self.y + 60 + leg_offset)
            right_leg = (head_x + 10, self.y + 60 - leg_offset)
        else:
            left_leg = (head_x - 10, self.y + 60)
            right_leg = (head_x + 10, self.y + 60)
        
        color = self.color if self.knockback_timer <= 0 else RED
        if self.frozen:
            color = ICE_BLUE
        
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
        
        # 霜之哀伤光环
        if self.is_player and self.frostmourne.active:
            for i in range(3):
                radius = 30 + i * 10
                pygame.draw.circle(screen, ICE_BLUE, (head_x, head_y + 30), radius, 2)
        
        # 血条
        bar_width = 40
        bar_height = 6
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (screen_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, self.y - 15, bar_width * health_percent, bar_height))
        
        if self.is_player:
            for shard in self.ice_shards:
                shard.draw(screen, camera_x)

class Enemy(StickMan):
    def __init__(self, x, y):
        super().__init__(x, y, RED, False)
        self.speed = 2
        self.ai_timer = 0
    
    def update_ai(self, player, platforms):
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
            
            # 敌人也会飞
            if abs(distance) < 150 and not self.on_ground:
                self.fly()
        else:
            if self.ai_timer <= 0:
                self.vel_x = random.choice([-self.speed, self.speed])
                self.ai_timer = random.randint(60, 180)
            else:
                self.ai_timer -= 1
        
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
        pygame.display.set_caption("Stickman - Frostmourne (Flying Edition)")
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
        self.enemy_spawn_timer = 0
        self.max_enemies = 8  # 最多同时存在8个敌人
        self.tutorial_text = "F = Freeze | SPACE = Jump/Fly | J = Attack"
        
        # 特效
        self.shake_timer = 0
        self.frost_effect_timer = 0
        
        # 创建平台
        self.platforms.append(Platform(0, GROUND_Y, SCREEN_WIDTH * 2, 20, DARK_GRAY))
        self.platforms.append(Platform(200, 450, 100, 20))
        self.platforms.append(Platform(500, 400, 100, 20))
        self.platforms.append(Platform(800, 350, 100, 20))
        self.platforms.append(Platform(1100, 450, 100, 20))
        
        # 初始敌人
        for i in range(3):
            self.spawn_enemy()
    
    def spawn_enemy(self):
        """生成敌人"""
        if len(self.enemies) < self.max_enemies:
            x = random.randint(200, SCREEN_WIDTH * 2 - 200)
            y = random.randint(100, GROUND_Y - 100)
            new_enemy = Enemy(x, y)
            self.enemies.append(new_enemy)
    
    def frostmourne_aoe(self):
        """霜之哀伤 - 冰冻+少量伤害"""
        frozen_count = 0
        for enemy in self.enemies:
            if not enemy.frozen:
                # 冰冻敌人，造成少量伤害
                enemy.take_damage(5, 1 if enemy.x < self.player.x else -1)
                enemy.freeze(90)  # 冰冻1.5秒
                frozen_count += 1
        
        # 屏幕震动
        self.shake_timer = 8
        self.frost_effect_timer = 15
        
        return frozen_count
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.game_over:
            # 移动
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            else:
                self.player.vel_x *= 0.8
            
            # 飞行（按住空格飞行）
            if keys[pygame.K_SPACE]:
                self.player.fly()
            else:
                self.player.stop_fly()
    
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
        
        # 冰霜碎片碰撞
        for shard in self.player.ice_shards[:]:
            shard_rect = pygame.Rect(shard.x-3, shard.y-3, 6, 6)
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if shard_rect.colliderect(enemy_rect):
                    enemy.take_damage(8, 1 if enemy.x < shard.x else -1)
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
        
        # 相机跟随
        self.camera_x = self.player.x - SCREEN_WIDTH // 2 + self.player.width // 2
        self.camera_x = max(0, min(self.camera_x, SCREEN_WIDTH * 2 - SCREEN_WIDTH))
        
        # 无限生成敌人
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60 and len(self.enemies) < self.max_enemies:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()
        
        # 检查游戏结束
        if self.player.health <= 0:
            self.game_over = True
        
        # 更新特效
        if self.shake_timer > 0:
            self.shake_timer -= 1
        if self.frost_effect_timer > 0:
            self.frost_effect_timer -= 1
    
    def draw(self):
        # 屏幕震动
        shake_x = random.randint(-3, 3) if self.shake_timer > 0 else 0
        shake_y = random.randint(-3, 3) if self.shake_timer > 0 else 0
        
        # 背景
        if self.frost_effect_timer > 0:
            self.screen.fill((150, 200, 255))
        else:
            self.screen.fill(SKY_BLUE)
        
        # 冰霜特效
        if self.frost_effect_timer > 0:
            for _ in range(30):
                fx = random.randint(0, SCREEN_WIDTH)
                fy = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (fx, fy), random.randint(1, 3))
        
        # 云朵
        for i in range(3):
            cloud_x = (i * 300 - self.camera_x * 0.5) % (SCREEN_WIDTH + 200) - 100 + shake_x
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 50))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 100, 60))
        
        # 平台
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
        
        # 敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # 玩家
        self.player.draw(self.screen, self.camera_x)
        
        # UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 50))
        
        kills_text = self.font.render(f"Kills: {self.kill_count}", True, BLACK)
        self.screen.blit(kills_text, (10, 90))
        
        enemies_text = self.font.render(f"Enemies: {len(self.enemies)}", True, BLACK)
        self.screen.blit(enemies_text, (10, 130))
        
        # 飞行提示
        fly_text = self.font.render("HOLD SPACE = FLY", True, DARK_BLUE)
        self.screen.blit(fly_text, (SCREEN_WIDTH - 200, 10))
        
        # 技能图标
        self.player.frostmourne.draw_cd_icon(self.screen, SCREEN_WIDTH - 70, 50)
        
        # 技能说明
        skill_desc = self.font.render("F = Freeze", True, DARK_BLUE)
        self.screen.blit(skill_desc, (SCREEN_WIDTH - 200, 110))
        
        if self.kill_count < 5:
            tutorial = self.font.render(self.tutorial_text, True, BLACK)
            self.screen.blit(tutorial, (SCREEN_WIDTH // 2 - 250, 20))
        
        # 游戏结束
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
            
            kills_text = self.font.render(f"Total Kills: {self.kill_count}", True, WHITE)
            kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(kills_text, kills_rect)
            
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j and not self.game_over:
                        self.player.attack()
                    
                    elif event.key == pygame.K_f and not self.game_over:
                        if self.player.use_frostmourne():
                            frozen = self.frostmourne_aoe()
                            if frozen > 0:
                                print(f"Froze {frozen} enemies!")  # 调试信息
                    
                    elif event.key == pygame.K_r and self.game_over:
                        self.init_game()
                    
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
