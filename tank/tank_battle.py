import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

class Tank:
    def __init__(self, x, y, color, direction='UP'):
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.speed = 5
        self.size = 30
        self.bullets = []
        self.shoot_delay = 0
        self.health = 3
        
    def move(self, keys, walls):
        new_x, new_y = self.x, self.y
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = 'LEFT'
            new_x -= self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = 'RIGHT'
            new_x += self.speed
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = 'UP'
            new_y -= self.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = 'DOWN'
            new_y += self.speed
            
        # 边界检查
        if 0 <= new_x <= SCREEN_WIDTH - self.size:
            # 碰撞检测
            tank_rect = pygame.Rect(new_x, self.y, self.size, self.size)
            collision = False
            for wall in walls:
                if tank_rect.colliderect(wall.rect):
                    collision = True
                    break
            if not collision:
                self.x = new_x
                
        if 0 <= new_y <= SCREEN_HEIGHT - self.size:
            tank_rect = pygame.Rect(self.x, new_y, self.size, self.size)
            collision = False
            for wall in walls:
                if tank_rect.colliderect(wall.rect):
                    collision = True
                    break
            if not collision:
                self.y = new_y
    
    def shoot(self):
        if self.shoot_delay <= 0:
            bullet = Bullet(self.x + self.size//2, self.y + self.size//2, self.direction)
            self.bullets.append(bullet)
            self.shoot_delay = 20
    
    def update(self):
        if self.shoot_delay > 0:
            self.shoot_delay -= 1
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)
    
    def draw(self, screen):
        # 绘制坦克主体
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        
        # 绘制炮管
        barrel_length = 20
        if self.direction == 'UP':
            pygame.draw.line(screen, self.color, 
                           (self.x + self.size//2, self.y + self.size//2),
                           (self.x + self.size//2, self.y - barrel_length), 5)
        elif self.direction == 'DOWN':
            pygame.draw.line(screen, self.color,
                           (self.x + self.size//2, self.y + self.size//2),
                           (self.x + self.size//2, self.y + self.size + barrel_length), 5)
        elif self.direction == 'LEFT':
            pygame.draw.line(screen, self.color,
                           (self.x + self.size//2, self.y + self.size//2),
                           (self.x - barrel_length, self.y + self.size//2), 5)
        elif self.direction == 'RIGHT':
            pygame.draw.line(screen, self.color,
                           (self.x + self.size//2, self.y + self.size//2),
                           (self.x + self.size + barrel_length, self.y + self.size//2), 5)
        
        # 绘制履带装饰
        pygame.draw.rect(screen, (100, 100, 100), (self.x-5, self.y, 5, self.size))
        pygame.draw.rect(screen, (100, 100, 100), (self.x+self.size, self.y, 5, self.size))

class EnemyTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, RED, random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT']))
        self.speed = 3
        self.move_timer = 0
        self.shoot_timer = random.randint(30, 90)
        self.ai_movement()
    
    def ai_movement(self):
        self.move_timer = random.randint(30, 90)
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    
    def update_ai(self, walls):
        if self.move_timer <= 0:
            self.ai_movement()
        else:
            self.move_timer -= 1
        
        # 移动
        if self.direction == 'UP':
            self.y -= self.speed
        elif self.direction == 'DOWN':
            self.y += self.speed
        elif self.direction == 'LEFT':
            self.x -= self.speed
        elif self.direction == 'RIGHT':
            self.x += self.speed
        
        # 边界检查
        if self.x < 0:
            self.x = 0
            self.ai_movement()
        elif self.x > SCREEN_WIDTH - self.size:
            self.x = SCREEN_WIDTH - self.size
            self.ai_movement()
            
        if self.y < 0:
            self.y = 0
            self.ai_movement()
        elif self.y > SCREEN_HEIGHT - self.size:
            self.y = SCREEN_HEIGHT - self.size
            self.ai_movement()
        
        # 碰撞检测
        tank_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        for wall in walls:
            if tank_rect.colliderect(wall.rect):
                # 回退移动
                if self.direction == 'UP':
                    self.y += self.speed
                elif self.direction == 'DOWN':
                    self.y -= self.speed
                elif self.direction == 'LEFT':
                    self.x += self.speed
                elif self.direction == 'RIGHT':
                    self.x -= self.speed
                self.ai_movement()
                break
        
        # 射击
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = random.randint(30, 90)
        else:
            self.shoot_timer -= 1
        
        super().update()
    
    def shoot(self):
        if self.shoot_delay <= 0:
            bullet = Bullet(self.x + self.size//2, self.y + self.size//2, self.direction)
            self.bullets.append(bullet)
            self.shoot_delay = 30

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 8
        self.size = 5
        
    def update(self):
        if self.direction == 'UP':
            self.y -= self.speed
        elif self.direction == 'DOWN':
            self.y += self.speed
        elif self.direction == 'LEFT':
            self.x -= self.speed
        elif self.direction == 'RIGHT':
            self.x += self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
    
    def off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BROWN
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.init_game()
    
    def init_game(self):
        self.player = Tank(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, GREEN)
        self.enemies = []
        self.walls = []
        self.game_over = False
        
        # 创建墙壁
        wall_positions = [
            (200, 200, 20, 100), (400, 300, 100, 20),
            (600, 150, 20, 100), (100, 400, 100, 20),
            (700, 450, 20, 100), (300, 500, 100, 20)
        ]
        for x, y, w, h in wall_positions:
            self.walls.append(Wall(x, y, w, h))
        
        # 创建敌人
        for i in range(5):
            x = random.randint(50, SCREEN_WIDTH - 80)
            y = random.randint(50, 200)
            self.enemies.append(EnemyTank(x, y))
    
    def handle_collisions(self):
        # 子弹与墙壁碰撞
        for bullet in self.player.bullets[:]:
            for wall in self.walls:
                if bullet.get_rect().colliderect(wall.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
        
        # 子弹与敌人碰撞
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                if bullet.get_rect().colliderect(enemy_rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # 敌方子弹与玩家碰撞
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                player_rect = pygame.Rect(self.player.x, self.player.y, 
                                         self.player.size, self.player.size)
                if bullet.get_rect().colliderect(player_rect):
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.game_over = True
                    break
        
        # 敌方子弹与墙壁碰撞
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                for wall in self.walls:
                    if bullet.get_rect().colliderect(wall.rect):
                        if bullet in enemy.bullets:
                            enemy.bullets.remove(bullet)
                        break
        
        # 玩家与敌方坦克碰撞
        for enemy in self.enemies:
            player_rect = pygame.Rect(self.player.x, self.player.y, 
                                     self.player.size, self.player.size)
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
            if player_rect.colliderect(enemy_rect):
                # 弹开敌方坦克
                if self.player.x < enemy.x:
                    enemy.x += 10
                else:
                    enemy.x -= 10
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        self.player.shoot()
                    elif event.key == pygame.K_r and self.game_over:
                        self.init_game()
            
            if not self.game_over:
                # 获取按键
                keys = pygame.key.get_pressed()
                
                # 更新玩家
                self.player.move(keys, self.walls)
                self.player.update()
                
                # 更新敌人AI
                for enemy in self.enemies:
                    enemy.update_ai(self.walls)
                
                # 处理碰撞
                self.handle_collisions()
                
                # 生成新敌人
                if len(self.enemies) < 5 and random.randint(1, 100) < 2:
                    x = random.randint(50, SCREEN_WIDTH - 80)
                    y = random.randint(50, 150)
                    self.enemies.append(EnemyTank(x, y))
            
            # 绘制
            self.screen.fill(BLACK)
            
            # 绘制墙壁
            for wall in self.walls:
                wall.draw(self.screen)
            
            # 绘制玩家
            if not self.game_over:
                self.player.draw(self.screen)
                for bullet in self.player.bullets:
                    bullet.draw(self.screen)
            
            # 绘制敌人
            for enemy in self.enemies:
                enemy.draw(self.screen)
                for bullet in enemy.bullets:
                    bullet.draw(self.screen)
            
            # 显示信息
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
            self.screen.blit(health_text, (10, 50))
            
            if self.game_over:
                game_over_text = self.font.render("GAME OVER - Press R to restart", True, RED)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(game_over_text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
