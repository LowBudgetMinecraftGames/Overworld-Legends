import math
import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.window import Window

class OverworldLegendsGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_x = 200
        self.player_y = 300
        self.player_radius = 25
        self.player_hp = 100
        self.base_x = 100
        self.base_y = 300
        self.base_hp = 500
        self.base_max_hp = 500
        self.golems = []
        self.enemies = []
        self.rally_point = None
        self.resources = 100
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        self.joystick_center_x = 150
        self.joystick_center_y = 150
        self.joystick_radius = 80
        self.joystick_dir_x = 0
        self.joystick_dir_y = 0
        self.joystick_touch_id = None
        for _ in range(3):
            self.golems.append({'x': self.base_x + random.randint(30, 80), 'y': self.base_y + random.randint(-50, 50), 'hp': 40, 'max_hp': 40, 'state': 'FOLLOW'})
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_down(self, touch):
        if self.game_over: return True
        dist_to_joystick = math.hypot(touch.x - self.joystick_center_x, touch.y - self.joystick_center_y)
        if dist_to_joystick <= self.joystick_radius and self.joystick_touch_id is None:
            self.joystick_touch_id = touch.id
            self.update_joystick(touch.x, touch.y)
            return True
        btn_x, btn_y, btn_w, btn_h = self.width - 180, 40, 140, 80
        if btn_x <= touch.x <= btn_x + btn_w and btn_y <= touch.y <= btn_y + btn_h:
            if self.resources >= 30:
                self.resources -= 30
                self.golems.append({'x': self.player_x, 'y': self.player_y, 'hp': 40, 'max_hp': 40, 'state': 'FOLLOW'})
            return True
        rec_x, rec_y, rec_w, rec_h = self.width - 340, 40, 140, 80
        if rec_x <= touch.x <= rec_x + rec_w and rec_y <= touch.y <= rec_y + rec_h:
            self.rally_point = None
            for golem in self.golems: golem['state'] = 'FOLLOW'
            return True
        if touch.x > 300 or touch.y > 300:
            self.rally_point = (touch.x, touch.y)
            for golem in self.golems: golem['state'] = 'RALLY'
            return True

    def on_touch_move(self, touch):
        if touch.id == self.joystick_touch_id:
            self.update_joystick(touch.x, touch.y)
            return True

    def on_touch_up(self, touch):
        if touch.id == self.joystick_touch_id:
            self.joystick_touch_id = None
            self.joystick_dir_x = 0
            self.joystick_dir_y = 0
            return True

    def update_joystick(self, tx, ty):
        dx = tx - self.joystick_center_x
        dy = ty - self.joystick_center_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.joystick_dir_x = dx / dist
            self.joystick_dir_y = dy / dist

    def update(self, dt):
        if self.game_over: return
        self.frame_count += 1
        if self.frame_count % 180 == 0:
            self.resources += 20
            for _ in range(random.randint(1, 3)):
                self.enemies.append({'x': self.width - 50, 'y': random.randint(100, self.height - 100), 'hp': 30, 'max_hp': 30})
        player_speed = 5
        self.player_x += self.joystick_dir_x * player_speed
        self.player_y += self.joystick_dir_y * player_speed
        self.player_x = max(self.player_radius, min(self.width - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(self.height - self.player_radius, self.player_y))
        for golem in self.golems:
            closest_enemy = None
            closest_dist = 180
            for enemy in self.enemies:
                d = math.hypot(enemy['x'] - golem['x'], enemy['y'] - golem['y'])
                if d < closest_dist:
                    closest_dist = d
                    closest_enemy = enemy
            if closest_enemy:
                dx, dy = closest_enemy['x'] - golem['x'], closest_enemy['y'] - golem['y']
                golem['x'] += (dx / closest_dist) * 3.5
                golem['y'] += (dy / closest_dist) * 3.5
                if closest_dist < 40: closest_enemy['hp'] -= 0.6
            elif golem['state'] == 'FOLLOW':
                d_to_p = math.hypot(self.player_x - golem['x'], self.player_y - golem['y'])
                if d_to_p > 60:
                    golem['x'] += ((self.player_x - golem['x']) / d_to_p) * 4
                    golem['y'] += ((self.player_y - golem['y']) / d_to_p) * 4
            elif golem['state'] == 'RALLY' and self.rally_point:
                d_to_r = math.hypot(self.rally_point[0] - golem['x'], self.rally_point[1] - golem['y'])
                if d_to_r > 10:
                    golem['x'] += ((self.rally_point[0] - golem['x']) / d_to_r) * 4
                    golem['y'] += ((self.rally_point[1] - golem['y']) / d_to_r) * 4
        for enemy in self.enemies:
            t_x, t_y, t_obj = self.base_x, self.base_y, None
            c_dist = math.hypot(self.base_x - enemy['x'], self.base_y - enemy['y'])
            d_p = math.hypot(self.player_x - enemy['x'], self.player_y - enemy['y'])
            if d_p < c_dist and d_p < 250:
                c_dist, t_x, t_y, t_obj = d_p, self.player_x, self.player_y, 'PLAYER'
            for golem in self.golems:
                d_g = math.hypot(golem['x'] - enemy['x'], golem['y'] - enemy['y'])
                if d_g < c_dist and d_g < 200:
                    c_dist, t_x, t_y, t_obj = d_g, golem['x'], golem['y'], golem
            if c_dist > 5:
                enemy['x'] += ((t_x - enemy['x']) / c_dist) * 2.2
                enemy['y'] += ((t_y - enemy['y']) / c_dist) * 2.2
            if c_dist < 45:
                if t_obj == 'PLAYER': self.player_hp -= 0.4
                elif isinstance(t_obj, dict): t_obj['hp'] -= 0.5
                elif t_x == self.base_x: self.base_hp -= 0.6
        self.golems = [g for g in self.golems if g['hp'] > 0]
        for enemy in self.enemies[:]:
            if enemy['hp'] <= 0:
                self.enemies.remove(enemy)
                self.score += 10
                self.resources += 15
        if self.player_hp <= 0 or self.base_hp <= 0: self.game_over = True
        self.canvas.clear()
        self.draw_game()

    def draw_game(self):
        with self.canvas:
            Color(60/255, 163/255, 85/255)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
            Color(117/255, 28/255, 28/255)
            Rectangle(pos=(self.width - 180, 0), size=(180, self.height))
            Color(241/255, 196/255, 15/255)
            Rectangle(pos=(self.base_x - 50, self.base_y - 50), size=(100, 100))
            if self.base_hp < self.base_max_hp:
                Color(1, 0, 0)
                Rectangle(pos=(self.base_x - 50, self.base_y + 60), size=(100, 8))
                Color(0, 1, 0)
                Rectangle(pos=(self.base_x - 50, self.base_y + 60), size=(100 * (self.base_hp / self.base_max_hp), 8))
            if self.rally_point:
                Color(1, 1, 1, 0.6)
                Line(circle=(self.rally_point[0], self.rally_point[1], 15), width=2)
            Color(149/255, 165/255, 166/255)
            for golem in self.golems: Ellipse(pos=(golem['x'] - 15, golem['y'] - 15), size=(30, 30))
            Color(231/255, 76/255, 60/255)
            for enemy in self.enemies: Ellipse(pos=(enemy['x'] - 18, enemy['y'] - 18), size=(36, 36))
            Color(52/255, 152/255, 219/255)
            Ellipse(pos=(self.player_x - self.player_radius, self.player_y - self.player_radius), size=(self.player_radius*2, self.player_radius*2))
            Color(0.2, 0.2, 0.2, 0.4)
            Ellipse(pos=(self.joystick_center_x - self.joystick_radius, self.joystick_center_y - self.joystick_radius), size=(self.joystick_radius*2, self.joystick_radius*2))
            Color(0.8, 0.8, 0.8, 0.7)
            knob_x = self.joystick_center_x + (self.joystick_dir_x * 40) - 20
            knob_y = self.joystick_center_y + (self.joystick_dir_y * 40) - 20
            Ellipse(pos=(knob_x, knob_y), size=(40, 40))
            Color(44/255, 62/255, 80/255, 0.8)
            Rectangle(pos=(self.width - 340, 40), size=(140, 80))
            Color(39/255, 174/255, 96/255, 0.8)
            Rectangle(pos=(self.width - 180, 40), size=(140, 80))
            if self.game_over:
                Color(0, 0, 0, 0.8)
                Rectangle(pos=(0, 0), size=(self.width, self.height))

class OverworldLegendsApp(App):
    def build(self): return OverworldLegendsGame()

if __name__ == '__main__':
    Window.size = (1280, 720)
    OverworldLegendsApp().run()
          
