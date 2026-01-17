import pygame
import random
import sys

# Simple garbage-truck game using Pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (50, 180, 50)
TRUCK_COLOR = (40, 120, 40)
GARBAGE_COLOR = (150, 100, 40)

TRUCK_W, TRUCK_H = 34, 60
GARBAGE_SIZE = 12
TOTAL_GARBAGE = 15

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Garbage Truck Collector')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)


def make_garbage(n):
    # placeholder if sidewalks not provided
    items = []
    for _ in range(n):
        x = random.randint(100, WINDOW_WIDTH - 120)
        y = random.randint(100, WINDOW_HEIGHT - 100)
        rect = pygame.Rect(x, y, GARBAGE_SIZE, GARBAGE_SIZE)
        items.append(rect)
    return items


def make_garbage_on_sidewalks(n, sidewalk_rects):
    items = []
    if not sidewalk_rects:
        return make_garbage(n)
    for _ in range(n):
        area = random.choice(sidewalk_rects)
        # ensure garbage fits inside area (allow minimal margins)
        if area.width < GARBAGE_SIZE or area.height < GARBAGE_SIZE:
            continue
        x_min = area.left
        x_max = area.right - GARBAGE_SIZE
        y_min = area.top
        y_max = area.bottom - GARBAGE_SIZE
        if x_min > x_max or y_min > y_max:
            continue
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        items.append(pygame.Rect(x, y, GARBAGE_SIZE, GARBAGE_SIZE))
    # if we couldn't place enough (small sidewalks), fill remaining randomly on sidewalks
    # fill remaining by trying sidewalks until we have enough or attempts exhausted
    attempts = 0
    while len(items) < n and sidewalk_rects and attempts < n * 4:
        attempts += 1
        area = random.choice(sidewalk_rects)
        if area.width < GARBAGE_SIZE or area.height < GARBAGE_SIZE:
            continue
        x_min = area.left
        x_max = area.right - GARBAGE_SIZE
        y_min = area.top
        y_max = area.bottom - GARBAGE_SIZE
        if x_min > x_max or y_min > y_max:
            continue
        x = random.randint(x_min, x_max)
        y = random.randint(y_min, y_max)
        items.append(pygame.Rect(x, y, GARBAGE_SIZE, GARBAGE_SIZE))
    return items


def is_point_in_any_rect(point, rects):
    x, y = point
    for r in rects:
        if r.collidepoint(x, y):
            return True
    return False


def generate_city_layout():
    # returns (road_rects, sidewalk_rects, building_rects)
    road_rects = []
    sidewalk_rects = []
    building_rects = []
    road_w = 80
    sidewalk_w = 14
    # vertical roads
    for x in range(100, WINDOW_WIDTH, 200):
        r = pygame.Rect(x, 80, road_w, WINDOW_HEIGHT - 160)
        road_rects.append(r)
        # sidewalks on both sides
        left = pygame.Rect(r.left - sidewalk_w, r.top, sidewalk_w, r.height)
        right = pygame.Rect(r.right, r.top, sidewalk_w, r.height)
        sidewalk_rects.extend([left, right])
    # horizontal roads
    for y in range(160, WINDOW_HEIGHT, 180):
        r = pygame.Rect(80, y, WINDOW_WIDTH - 160, road_w)
        road_rects.append(r)
        top = pygame.Rect(r.left, r.top - sidewalk_w, r.width, sidewalk_w)
        bottom = pygame.Rect(r.left, r.bottom, r.width, sidewalk_w)
        sidewalk_rects.extend([top, bottom])

    # buildings in blocks between roads
    block_color = (120, 110, 100)
    for bx in range(10, WINDOW_WIDTH - 100, 200):
        for by in range(90, WINDOW_HEIGHT - 120, 180):
            b_w = 80
            b_h = 60
            building_rects.append(pygame.Rect(bx, by, b_w, b_h))

    return road_rects, sidewalk_rects, building_rects


def draw_city_background(surface):
    # Deprecated: this function is replaced by the layout-driven draw in main
    surface.fill((40, 160, 40))


def draw_truck(surface, rect):
    # top-down truck body
    pygame.draw.rect(surface, TRUCK_COLOR, rect, border_radius=4)
    # small front indicator (windshield) is drawn by caller via facing vector
    # add a darker outline
    pygame.draw.rect(surface, (10, 70, 120), rect, 2, border_radius=4)


def draw_ui(surface, score, remaining):
    score_surf = font.render(f'Score: {score}', True, BLACK)
    left_surf = font.render(f'Remaining: {remaining}', True, BLACK)
    surface.blit(score_surf, (10, 10))
    surface.blit(left_surf, (10, 36))


def main():
    # truck position is stored as its center point (x,y)
    truck_pos = [WINDOW_WIDTH // 2, WINDOW_HEIGHT - TRUCK_H // 2 - 10]
    speed = 4
    # generate static layout (roads, sidewalks, buildings)
    road_rects, sidewalk_rects, building_rects = generate_city_layout()
    garbage = make_garbage_on_sidewalks(TOTAL_GARBAGE, sidewalk_rects)
    score = 0
    running = True
    paused = False
    win = False
    # facing vector for a simple front indicator (0,-1 up, 1,0 right, etc.)
    facing = (0, -1)
    # base truck surface (points upward) - draw cab + cargo box for a garbage truck look
    base_truck = pygame.Surface((TRUCK_W, TRUCK_H), pygame.SRCALPHA)
    base_truck.fill((0, 0, 0, 0))
    # layout: top = cab, bottom = cargo box
    cargo_h = int(TRUCK_H * 0.6)
    cab_h = TRUCK_H - cargo_h
    # cab (front)
    pygame.draw.rect(base_truck, TRUCK_COLOR, (0, 0, TRUCK_W, cab_h), border_radius=3)
    # cargo box (rear) - slightly darker
    cargo_color = (20, 90, 30)
    pygame.draw.rect(base_truck, cargo_color, (0, cab_h, TRUCK_W, cargo_h), border_radius=3)
    # side stripe on cargo (yellow) to resemble garbage truck markings
    stripe_h = max(4, int(cargo_h * 0.25))
    pygame.draw.rect(base_truck, (220, 200, 0), (4, cab_h + 6, TRUCK_W - 8, stripe_h), border_radius=2)
    # rear hatch/loader detail
    pygame.draw.rect(base_truck, (30, 30, 30), (TRUCK_W - 18, cab_h + 4, 10, cargo_h - 8), border_radius=2)
    # small roof window/windshield on cab
    ws_w, ws_h = TRUCK_W // 2, max(4, cab_h // 2)
    ws_x = (TRUCK_W - ws_w) // 2
    pygame.draw.rect(base_truck, (200, 230, 255), (ws_x, 2, ws_w, ws_h), border_radius=2)
    # wheels (top-down circles) - left/right near cargo bottom
    wheel_x1 = 6
    wheel_x2 = TRUCK_W - 6
    wheel_y = TRUCK_H - 6
    pygame.draw.circle(base_truck, BLACK, (wheel_x1, wheel_y), 4)
    pygame.draw.circle(base_truck, BLACK, (wheel_x2, wheel_y), 4)
    # outline
    pygame.draw.rect(base_truck, (10, 70, 40), (0, 0, TRUCK_W, TRUCK_H), 2, border_radius=3)

    pickups = []  # active pickup animations
    last_truck_pos = truck_pos[:]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r and win:
                    # restart (spawn again on sidewalks)
                    garbage = make_garbage_on_sidewalks(TOTAL_GARBAGE, sidewalk_rects)
                    score = 0
                    win = False
                elif event.key == pygame.K_SPACE and not paused and not win:
                    # attempt pickup: only if truck is stationary (didn't move since last frame)
                    if truck_pos[0] == last_truck_pos[0] and truck_pos[1] == last_truck_pos[1]:
                        # find overlapping garbage
                        overlapping = [g for g in garbage if rotated_rect.colliderect(g)]
                        if overlapping:
                            g = overlapping[0]
                            # start pickup animation: move from garbage rect center to truck cargo area
                            start = g.copy()
                            end_pos = rotated_rect.center
                            pickups.append({'start': start, 'end': end_pos, 'progress': 0.0})
                            # remove the static garbage so it won't be drawn
                            try:
                                garbage.remove(g)
                            except ValueError:
                                pass

        keys = pygame.key.get_pressed()
        prev_pos = truck_pos[:]
        if not paused and not win:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                truck_pos[0] -= speed
                facing = (-1, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                truck_pos[0] += speed
                facing = (1, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                truck_pos[1] -= speed
                facing = (0, -1)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                truck_pos[1] += speed
                facing = (0, 1)

        # create rotated sprite and clamp the truck so rotated rect stays on screen
        angle = 0
        if facing == (0, -1):
            angle = 0
        elif facing == (1, 0):
            angle = -90
        elif facing == (0, 1):
            angle = 180
        elif facing == (-1, 0):
            angle = 90
        rotated = pygame.transform.rotate(base_truck, angle)
        rotated_rect = rotated.get_rect(center=truck_pos)
        # clamp by adjusting center if rotated rect goes out of bounds
        if rotated_rect.left < 0:
            truck_pos[0] += -rotated_rect.left
            rotated_rect = rotated.get_rect(center=truck_pos)
        if rotated_rect.right > WINDOW_WIDTH:
            truck_pos[0] -= (rotated_rect.right - WINDOW_WIDTH)
            rotated_rect = rotated.get_rect(center=truck_pos)
        if rotated_rect.top < 60:
            truck_pos[1] += (60 - rotated_rect.top)
            rotated_rect = rotated.get_rect(center=truck_pos)
        if rotated_rect.bottom > WINDOW_HEIGHT:
            truck_pos[1] -= (rotated_rect.bottom - WINDOW_HEIGHT)
            rotated_rect = rotated.get_rect(center=truck_pos)

        # if the truck center is not on any road, revert movement
        # we check truck_pos (the center) against road_rects
        if not is_point_in_any_rect(truck_pos, road_rects):
            # revert to previous pos
            truck_pos = prev_pos[:]
            rotated_rect = rotated.get_rect(center=truck_pos)

        # collision detection - highlight potential pickups but do not auto-remove
        overlapping = []
        if not paused and not win:
            overlapping = [g for g in garbage if rotated_rect.colliderect(g)]

        # draw scene: grass, buildings, roads, sidewalks
        draw_city_background(screen)
        # buildings
        for b in building_rects:
            pygame.draw.rect(screen, (120, 110, 100), b)
        # roads and center markings
        for r in road_rects:
            pygame.draw.rect(screen, (60, 60, 60), r)
            if r.width > r.height:
                for x in range(r.left + 10, r.right, 30):
                    pygame.draw.rect(screen, (200, 200, 200), (x, r.centery - 2, 16, 4))
            else:
                for y in range(r.top + 10, r.bottom, 30):
                    pygame.draw.rect(screen, (200, 200, 200), (r.centerx - 2, y, 4, 16))
        # sidewalks
        for s in sidewalk_rects:
            pygame.draw.rect(screen, (200, 200, 170), s)

        # garbage items (on sidewalks)
        for g in garbage:
            pygame.draw.rect(screen, GARBAGE_COLOR, g)
        # highlight overlapping garbage when truck overlaps
        for g in overlapping:
            pygame.draw.rect(screen, (255, 255, 255), g, 2)

        # update pickup animations
        for p in pickups[:]:
            p['progress'] += 0.06
            if p['progress'] >= 1.0:
                pickups.remove(p)
                score += 1
                continue
            t = p['progress']
            sx = p['start'].centerx
            sy = p['start'].centery
            ex, ey = p['end']
            cx = int(sx + (ex - sx) * t)
            cy = int(sy + (ey - sy) * t)
            size = max(2, int(GARBAGE_SIZE * (1 - 0.6 * t)))
            alpha = int(255 * (1 - t))
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            surf.fill((GARBAGE_COLOR[0], GARBAGE_COLOR[1], GARBAGE_COLOR[2], alpha))
            screen.blit(surf, (cx - size//2, cy - size//2))

        # draw rotated truck sprite
        screen.blit(rotated, rotated_rect)

        # show pickup hint when stationary and overlapping
        if overlapping and truck_pos[0] == last_truck_pos[0] and truck_pos[1] == last_truck_pos[1]:
            hint = font.render('Press SPACE to pick up', True, BLACK)
            screen.blit(hint, (rotated_rect.centerx - hint.get_width()//2, rotated_rect.top - 22))
        draw_ui(screen, score, len(garbage))

        if len(garbage) == 0 and not win:
            win = True

        if paused:
            pause_surf = font.render('Paused - press P to resume', True, BLACK)
            screen.blit(pause_surf, (WINDOW_WIDTH // 2 - pause_surf.get_width() // 2, WINDOW_HEIGHT // 2))

        if win:
            win_surf = font.render('All garbage collected! Press R to restart', True, BLACK)
            screen.blit(win_surf, (WINDOW_WIDTH // 2 - win_surf.get_width() // 2, WINDOW_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

        # update last_truck_pos for next frame to detect stationary
        last_truck_pos[0], last_truck_pos[1] = truck_pos[0], truck_pos[1]

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
