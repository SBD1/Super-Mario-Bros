def mario_battle_turn(stdscr, character):
    curses.curs_set(0)  # Ocultar o cursor
    stdscr.nodelay(1)   # Não bloquear para entrada
    stdscr.timeout(200) # Atualizar a tela a cada 200ms
    
    score = 0
    lives = 3
    mario_position = 1
    obstacles = [random.randint(10, SCENARIO_WIDTH - 1)]
    mario_y = GROUND_LEVEL  # Altura atual do Mario
    jumping = False         # Indica se o Mario está pulando
    jump_phase = 0          # Fases do pulo (subindo/descendo)

    while lives > 0:
        stdscr.clear()
        
        # Gera o cenário
        scenario = generate_scenario(obstacles)
        ground_line = scenario[:mario_position] + character + scenario[mario_position + 1:]
        air_line = " " * mario_position + character + " " * (SCENARIO_WIDTH - mario_position - 1)
        
        # Mostra o cenário com Mario na posição correta
        if mario_y == GROUND_LEVEL:
            stdscr.addstr(0, 0, " " * SCENARIO_WIDTH)  # Linha de cima vazia
            stdscr.addstr(1, 0, ground_line)          # Mario no chão
        else:
            stdscr.addstr(0, 0, air_line)             # Mario no ar
            stdscr.addstr(1, 0, scenario)            # Obstáculos no chão

        stdscr.addstr(2, 0, f"Score: {score}  |  Lives: {lives}")
        
        # Atualiza obstáculos
        obstacles = [pos - 1 for pos in obstacles if pos - 1 > 0]
        if random.random() < 0.3:
            obstacles.append(SCENARIO_WIDTH - 1)

        # Detecta colisão
        if mario_y == GROUND_LEVEL and mario_position in obstacles:
            lives -= 1
            stdscr.addstr(3, 0, "Você bateu no obstáculo!")
        else:
            stdscr.addstr(3, 0, "Correndo...")

        # Pulo
        if jumping:
            if jump_phase < 2:  # Subindo
                mario_y = 0
                jump_phase += 1
            else:  # Descendo
                mario_y = GROUND_LEVEL
                jumping = False
                jump_phase = 0

        # Entrada do jogador
        key = stdscr.getch()
        if key == ord(' '):  # Barra de espaço para pular
            if mario_y == GROUND_LEVEL:  # Só pode pular se estiver no chão
                jumping = True
        elif key == ord('q'):  # 'q' para sair
            break

        # Atualiza score
        score += 1

        stdscr.refresh()
        time.sleep(0.1)

    # Fim de jogo
    stdscr.clear()
    stdscr.addstr(0, 0, f"Game Over! Sua pontuação final foi: {score}")
    stdscr.refresh()
    time.sleep(2)
