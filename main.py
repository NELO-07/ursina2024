from pydoc import visiblename

from pygame.transform import rotate
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

Entity.default_shader = lit_with_shadows_shader

# window.fullscreen = True
# 벽 생성 함수
def create_wall(position, scale, color=color.gray):  # color 인자 추가
    return Entity(model='cube', color=color, scale=scale, position=position, collider='box')

# 바닥 생성 함수
def create_floor(position, scale):
    return Entity(model='plane', scale=scale, position=position, texture='white_cube',
                  texture_scale=(scale[0] // 2, scale[2] // 2), collider='box')

# 각 층의 내부 구조를 다르게 설정하는 함수
def create_interior_for_floor(floor_number, floor_height):
    if floor_number == 1:
        # 1층: 넓은 공간 (튜토리얼 용도)
        pass  # 구조물이 없는 넓은 공간으로 설정
    elif floor_number == 2:
        # 2층: ㄹ자 모양의 구조
        pass
        create_wall(position=(0, floor_height + 5, -15), scale=(40, 10, 1))
        create_wall(position=(-15, floor_height + 5, 10), scale=(1, 10, 20))
        create_wall(position=(15, floor_height + 5, 15), scale=(1, 10, 20))
    elif floor_number == 3:
        # 3층: 재단과 기둥 2개
        pass
        create_wall(position=(-10, floor_height + 5, 10), scale=(2, 10, 2), color=color.white)  # 기둥 1
        create_wall(position=(10, floor_height + 5, 10), scale=(2, 10, 2), color=color.white)  # 기둥 2
    elif floor_number == 4:
        # 4층: ㄹ자 모양의 반대 구조
        pass
        create_wall(position=(0, floor_height + 5, 15), scale=(40, 10, 1))
        create_wall(position=(15, floor_height + 5, -10), scale=(1, 10, 20))
        create_wall(position=(-15, floor_height + 5, -15), scale=(1, 10, 20))
    elif floor_number == 5:
        # 5층: 멋진 재단과 기둥 2개
        pass
        create_wall(position=(-10, floor_height + 5, 10), scale=(3, 10, 3), color=color.white)  # 기둥 1
        create_wall(position=(10, floor_height + 5, 10), scale=(3, 10, 3), color=color.white)  # 기둥 2

# 탑을 구성할 함수
def create_tower(floors=5, height_per_floor=10):
    for i in range(floors):
        floor_height = i * height_per_floor

        # 바닥 생성
        floor = create_floor(position=(0, floor_height, 0), scale=(50, 1, 50))

        # 천장 생성
        ceiling = create_floor(position=(0, floor_height + height_per_floor, 0), scale=(50, 1, 50))
        ceiling.rotation_x = 180

        # 외벽 설정
        create_wall(position=(24.75, floor_height + 5, 0), scale=(1, 10, 50))
        create_wall(position=(-24.75, floor_height + 5, 0), scale=(1, 10, 50))
        create_wall(position=(0, floor_height + 5, 24.75), scale=(50, 10, 1))
        create_wall(position=(0, floor_height + 5, -24.75), scale=(50, 10, 1))

        # 각 층의 내부 구조 생성
        create_interior_for_floor(i + 1, floor_height)

create_tower(floors=5)  # 5층짜리 탑 생성

# 플레이어와 카메라 설정ddd
# editor_camera = EditorCamera(enabled=False, ignore_paused=True)

class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_hp = 100
        self.hp = self.max_hp

        # Add HP label
        self.hp_label = Text(text='HP', parent=camera.ui, position=(-0.75, 0.45), origin=(-0.5, 0), scale=2,
                             color=color.white)
        self.gun_label = Text(text='30' , parent=camera.ui, position=(-0.75, 0.35), origin=(-0.5, 0), scale=2,
                             color=color.white)

        self.health_bar = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.3, 0.02, 0.02),
                                 position=(-.65, 0.453), origin=(-0.5, 0))

    def take_damage(self, amount):
        self.hp -= amount
        self.health_bar.scale_x = self.hp / self.max_hp * 0.3
        if self.hp <= 0:
            print("플레이어가 사망했습니다!")
            application.quit()


# 기존의 player 설정을 이 클래스로 교체
player = Player(position=(0, 1, 0), model='cube', color=color.orange, origin_y=-.5, speed=8, collider='box')
# 총 설정
gun = Entity(model='gun6.glb', parent=camera, position=(0.5, -0.4, 1.2), scale=(1.5,1.5,1.5), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=0.9,y=0.1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

# 쏠 수 있는 객체의 부모 엔티티 생성
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

reloading = False

def update():
    global reloading
    if held_keys['left mouse'] and not application.paused:
        shoot()
    if held_keys['e'] and can_shoot:
        shoot_skill1()
    if held_keys['r'] and not application.paused:
        if not reloading:
            reloading = True
            print('재장전 중...')
            gun.animate('rotation_z', 60, duration=1, curve=curve.linear)
            invoke(hold_gun, delay=1)

    # 층 이동 기능 추가
    if held_keys['1']:
        player.position = (0, 1, 0)  # 1층
    elif held_keys['2']:
        player.position = (0, 11, 0)  # 2층
    elif held_keys['3']:
        player.position = (0, 21, 0)  # 3층
    elif held_keys['4']:
        player.position = (0, 31, 0)  # 4층
    elif held_keys['5']:
        player.position = (0, 41, 0)  # 5층


#총 가만히 두는 함수
def hold_gun():
    invoke(reset_gun, delay=1)

def reset_gun():
    gun.animate('rotation_z', 0, duration=1, curve=curve.linear)
    invoke(recharge, delay=1)

class Skill(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.direction = Vec3(0, 0, 0)
        self.speed = 0

    def update(self):
        self.position += self.direction * self.speed * time.dt
        # Raycast를 통해 아래쪽 바닥과의 충돌을 감지
        hit_info = raycast(self.position, direction=Vec3(0, -1, 0), distance=self.scale_y / 2 + 0.1, ignore=(self,))
        if hit_info.hit and hit_info.entity == floor:
            # skill1을 삭제하고 그 자리에 plane을 생성
            destroy(self)
            Entity(model='plane', color=color.blue, scale=8, position=hit_info.world_point)


can_shoot = True

def set_can_shoot_true():
    global can_shoot
    can_shoot = True

def shoot_skill1():
    global can_shoot
    can_shoot = False

    skill1 = Skill()
    skill1.model = 'sphere'
    skill1.texture = None
    skill1.scale = 1
    skill1.position = player.position + Vec3(0, 2, 0) + camera.forward
    skill1.direction = camera.forward
    skill1.speed = 10
    skill1.collider = 'box'
    invoke(set_can_shoot_true, delay=5)

def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if player.gun_label.text == '0':
            player.gun_label.color = color.red
            print('재장전을 해야합니다.')
        else:
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= 10
                mouse.hovered_entity.blink(color.red)

            player.gun_label.text = str(int(player.gun_label.text) - 1)

def recharge():
    global reloading
    player.gun_label.color = color.white
    player.gun_label.text = '30'
    reloading = False

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='goblin_1.glb', scale=(4,4,4), origin_y=-.25, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=.6, x=-.06, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack_cooldown = False

    def update(self):
        if application.paused:
            return

        dist = distance_xz(player.position, self.position)
        if dist > 60:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 1
            elif not self.attack_cooldown:
                self.attack()

    def attack(self):
        self.attack_cooldown = True
        player.take_damage(10)  # 플레이어에게 10 데미지
        print("적이 플레이어를 공격합니다!")
        invoke(self.reset_attack_cooldown, delay=3)  # 2초마다 공격

    def reset_attack_cooldown(self):
        self.attack_cooldown = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

class Enemy2(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='goblin_bow.glb', scale=(4,4,4), origin_y=-.25, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=0.6, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack_cooldown = False

    def update(self):
        if application.paused:
            return

        dist = distance_xz(player.position, self.position)
        if dist > 60:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 20:
                self.position += self.forward * time.dt * 1
            elif not self.attack_cooldown:
                self.attack()

    def attack(self):
        self.attack_cooldown = True
        player.take_damage(10)  # 플레이어에게 10 데미지
        print("적이 플레이어를 공격합니다!")
        invoke(self.reset_attack_cooldown, delay=2)  # 2초마다 공격

    def reset_attack_cooldown(self):
        self.attack_cooldown = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
# 적 생성
class Enemy3(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='slim.glb', scale=(2,2,2), origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=0.4, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 50
        self.hp = self.max_hp
        self.attack_cooldown = False

    def update(self):
        if application.paused:
            return

        dist = distance_xz(player.position, self.position)
        if dist > 60:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 1
            elif not self.attack_cooldown:
                self.attack()

    def attack(self):
        self.attack_cooldown = True
        player.take_damage(10)  # 플레이어에게 10 데미지
        print("적이 플레이어를 공격합니다!")
        invoke(self.reset_attack_cooldown, delay=2)  # 2초마다 공격

    def reset_attack_cooldown(self):
        self.attack_cooldown = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

class Boss(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='golem.glb', scale=(10,10,-10), origin_y=-0.3, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=.5, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 2000
        self.hp = self.max_hp
        self.attack_cooldown = False

    def update(self):
        if application.paused:
            return

        dist = distance_xz(player.position, self.position)
        if dist > 60:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 1
            elif not self.attack_cooldown:
                self.attack()

    def attack(self):
        self.attack_cooldown = True
        player.take_damage(10)  # 플레이어에게 10 데미지
        print("적이 플레이어를 공격합니다!")
        invoke(self.reset_attack_cooldown, delay=2)  # 2초마다 공격

    def reset_attack_cooldown(self):
        self.attack_cooldown = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

enemies = [Boss(x=0, z=10)]

# 이미지 추가 (플레이어의 시점에 오버레이로 표시)
overlay_image = Entity(parent=camera.ui, model='quad', texture='stop', scale=1)

overlay_image.alpha_setter(0)

def pause_input(key):
    global pause
    if key == 'tab':    # press tab to toggle edit/play mode
        pause = not pause

        player.cursor.enabled = not pause
        gun.enabled = not pause
        mouse.locked = not pause

        application.paused = pause

        overlay_image.alpha_setter(abs(overlay_image.alpha_getter()*255 - 255))

print(type(player))
pause_handler = Entity(ignore_paused=True, input=pause_input)

# 조명 추가
light = PointLight(parent=camera, position=(0, 2, -1.5))
ambient_light = AmbientLight(color=color.rgba(100, 100, 100, 0.5))
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))
Sky()

app.run()