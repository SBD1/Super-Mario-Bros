import curses
import random
import time

class Instancia:
    def __init__(self, id_personagem, vidaAtual, moedaAtual, pontosAtual):
        self.id = id_personagem
        self.vida = vidaAtual
        self.moedas = moedaAtual
        self.pontos = pontosAtual

SCENARIO_WIDTH = 20
OBSTACLE = "|"
ENEMY = "E"
GROUND_LEVEL = 1  
ENEMY_MOVE_DELAY = 10  

ITEMS = {"F": "Fireball", "I": "Ice Flower", "B": "Boomerang", "S": "Starman"}

def generate_scenario(obstacles, enemies, items):
    scenario = [" "] * SCENARIO_WIDTH
    for pos in obstacles:
        scenario[pos] = OBSTACLE
    for pos in enemies:
        scenario[pos] = ENEMY
    for pos, item in items.items():
        scenario[pos] = item
    return "".join(scenario)

def mario_battle_turn(stdscr, character):
    curses.curs_set(0)  
    stdscr.nodelay(1)   
    stdscr.timeout(200) 

    score = 0
    lives = 3
    mario_position = 1
    obstacles = [random.randint(10, SCENARIO_WIDTH - 1)]
    enemies = [random.randint(5, SCENARIO_WIDTH - 1)]
    items = {random.randint(5, SCENARIO_WIDTH - 1): random.choice(list(ITEMS.keys()))}  
    mario_y = GROUND_LEVEL  
    jumping = False  
    jump_phase = 0  
    enemy_move_timer = 0  
    difficulty = 1  
    collected_items = []  
    invincible_timer = 0  

    while lives > 0:
        stdscr.clear()
        
        if invincible_timer > 0:
            invincible_timer -= 1

        scenario = generate_scenario(obstacles, enemies, items)
        ground_line = scenario[:mario_position] + character + scenario[mario_position + 1:]
        air_line = " " * mario_position + character + " " * (SCENARIO_WIDTH - mario_position - 1)

        if mario_y == GROUND_LEVEL:
            stdscr.addstr(0, 0, " " * SCENARIO_WIDTH)
            stdscr.addstr(1, 0, ground_line)
        else:
            stdscr.addstr(0, 0, air_line)
            stdscr.addstr(1, 0, scenario)

        stdscr.addstr(2, 0, f"Score: {score}  |  Lives: {lives}  |  Items: {', '.join([ITEMS[i] for i in collected_items])}  |  Invincible: {invincible_timer}")
        
        obstacles = [pos - 1 for pos in obstacles if pos - 1 > 0]
        enemies = [pos + 1 for pos in enemies if pos + 1 < SCENARIO_WIDTH]
        items = {pos - 1: item for pos, item in items.items() if pos - 1 > 0}

        if random.random() < 0.3 + 0.1 * difficulty:
            obstacles.append(SCENARIO_WIDTH - 1)
        if random.random() < 0.2 + 0.1 * difficulty:
            enemies.append(SCENARIO_WIDTH - 1)
        if random.random() < 0.1:
            items[random.randint(5, SCENARIO_WIDTH - 1)] = random.choice(list(ITEMS.keys()))

        enemy_move_timer += 1
        if enemy_move_timer >= ENEMY_MOVE_DELAY - difficulty:
            enemies = [pos + 1 if random.choice([True, False]) else pos - 1 for pos in enemies]
            enemy_move_timer = 0

        if mario_y == GROUND_LEVEL:
            if mario_position in obstacles:
                if jumping:
                    obstacles.remove(mario_position)
                    score += 5
                    stdscr.addstr(3, 0, "Você pulou sobre o obstáculo!")
                else:
                    lives -= 1
                    stdscr.addstr(3, 0, "Você bateu no obstáculo!")
            elif mario_position in enemies:
                if "S" in collected_items:
                    enemies.remove(mario_position)
                    stdscr.addstr(3, 0, "Você derrotou o inimigo com a Estrela!")
                elif jumping:
                    enemies.remove(mario_position)
                    score += 10
                    stdscr.addstr(3, 0, "Você pulou no inimigo e derrotou-o!")
                else:
                    lives -= 1
                    stdscr.addstr(3, 0, "Você bateu no inimigo!")
            elif mario_position in items:
                collected_items.append(items[mario_position])
                stdscr.addstr(3, 0, f"Você pegou {ITEMS[items[mario_position]]}!")
                if items[mario_position] == "S":
                    invincible_timer = 20
                del items[mario_position]
        else:
            stdscr.addstr(3, 0, "Correndo...")

        if jumping:
            if jump_phase < 2:
                mario_y = 0
                jump_phase += 1
            else:
                mario_y = GROUND_LEVEL
                jumping = False
                jump_phase = 0

        key = stdscr.getch()
        if key == ord(' '):
            if mario_y == GROUND_LEVEL:
                jumping = True
        elif key == ord('q'):
            break
        elif key == ord('a'):
            if mario_position > 0:
                mario_position -= 1
        elif key == ord('d'):
            if mario_position < SCENARIO_WIDTH - 1:
                mario_position += 1
        elif key == ord('f') and "F" in collected_items:
            if enemies:
                enemies.pop(0)
                stdscr.addstr(3, 0, "Fireball derrotou um inimigo!")
        elif key == ord('i') and "I" in collected_items:
            if enemies:
                enemies[0] = -1  
                stdscr.addstr(3, 0, "Inimigo congelado!")
        elif key == ord('b') and "B" in collected_items:
            if enemies:
                enemies.pop()
                stdscr.addstr(3, 0, "Boomerang acertou um inimigo!")

        if score > 50:
            difficulty = 2
        if score > 100:
            difficulty = 3

        score += 1

        stdscr.refresh()
        time.sleep(0.1)

    stdscr.clear()
    stdscr.addstr(0, 0, f"Fim do Jogo! Sua pontuação final foi: {score}")
    stdscr.refresh()
    time.sleep(2)
