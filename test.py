from pydoc import visiblename

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

Entity.default_shader = lit_with_shadows_shader

window.fullscreen = True
# 바닥
floor = Entity(model='plane', scale=(100, 1, 100), texture='white_cube', texture_scale=(50, 50), collider='box')

# 천장
ceiling = Entity(model='plane', scale=(100, 1, 100), position=(0, 10, 0), texture='white_cube', texture_scale=(50, 50), collider='box')
ceiling.rotation_x = 180  # 천장을 위로 향하게

# 벽 생성 함수
def create_wall(position, scale):
    return Entity(model='cube', color=color.gray, scale=scale, position=position, collider='box')

pause = False

# 외벽 설정
wall_1 = create_wall(position=(49.5, 5, 0), scale=(1, 10, 100))
wall_2 = create_wall(position=(-49.5, 5, 0), scale=(1, 10, 100))
wall_3 = create_wall(position=(0, 5, 49.5), scale=(100, 10, 1))
wall_4 = create_wall(position=(0, 5, -49.5), scale=(100, 10, 1))

# 내부 구조물 생성
internal_wall_1 = create_wall(position=(0, 5, -30), scale=(80, 10, 1))
internal_wall_2 = create_wall(position=(-30, 5, 20), scale=(1, 10, 40))
internal_wall_3 = create_wall(position=(30, 5, 30), scale=(1, 10, 40))

# 출입구 생성
doorway = create_wall(position=(0, 1, -49.5), scale=(5, 2, 1))
doorway.color = color.black

# 플레이어와 카메라 설정
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
gun = Entity(model='cube', parent=camera, position=(.5, -0.25, .25), scale=(.3, .2, 1), origin_z=-.5, color=color.red, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)

# 쏠 수 있는 객체의 부모 엔티티 생성
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

def update():
    if held_keys['left mouse'] and not application.paused:
        shoot()
    if held_keys['e'] and can_shoot:
        shoot_skill1()

        # player.position = Vec3(-0.113553, 0.00100005, -46.7277)

class Skill(Entity):
    def update(self):
        self.position += self.direction * self.speed * time.dt
        if distance(self.position, player.position) > 20:
            destroy(self)

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


class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='goblin_1.glb', scale=(4,4,4), origin_y=-.25, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5, .1, .1))
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack_cooldown = False

    def update(self):
        if application.paused:
            return

        dist = distance_xz(player.position, self.position)
        if dist > 40:
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

# 적 생성
enemies = [Enemy(x=x*20 - 40, z=random.randint(-40, 40)) for x in range(5)]

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