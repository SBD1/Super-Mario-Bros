import curses
import pyfiglet  # Importando o pyfiglet
import pygame
import os
from phase import get_inimigo_by_fase, get_blocos_by_fase
from matriz import gera_matriz
import random

class Bloco:
    def __init__(self, tipo, mapa):
        self.tipo = tipo  # Tipo pode ser 'Moeda', 'Flor de Fogo', 'Boomerang', ou 'Vida'
        self.posicao = self.gerar_posicao_aleatoria(mapa)

    def gerar_posicao_aleatoria(self, mapa):
        while True:
            x = random.randint(0, len(mapa) - 1)
            y = random.randint(0, len(mapa[0]) - 1)
            if mapa[x][y] != 'M':  # Garantir que a posição não seja ocupada pelo Mario
                return [x, y]
    
    def interagir(self, mario):
        if self.tipo == "Moeda":
            mario.pontos += 10
            print("Você encontrou uma moeda! +10 pontos.")
        elif self.tipo == "Flor de Fogo":
            print("Você encontrou uma Flor de Fogo!")
            # Aqui você pode adicionar lógica para adicionar a Flor de Fogo ao inventário de Mario ou permitir que ele a use
        elif self.tipo == "Boomerang":
            print("Você encontrou um Boomerang!")
            # Aqui você pode adicionar lógica para permitir que Mario use o Boomerang
        elif self.tipo == "Vida":
            mario.vida += 20
            print("Você encontrou uma Vida! +20 de vida.")

def exibir_mapa(stdscr, player, mapa, mundo, fase, blocos):
    stdscr.clear() 
    
    if mapa is None:
        stdscr.addstr(0, 0, "Erro: Mapa não carregado corretamente.")
        stdscr.refresh()
        return

    altura, largura = stdscr.getmaxyx()

    titulo_ascii = pyfiglet.figlet_format(f"{mundo.name} - {fase.name}", font="small")

    titulo_x = (largura // 2) - (len(titulo_ascii.split("\n")[0]) // 2)

    for i, linha in enumerate(titulo_ascii.split("\n")):
        stdscr.addstr(i, titulo_x, linha)

    mapa_inicio_x = (largura // 2) - (len(mapa[0]) * 2 // 2) 
    mapa_inicio_y = (altura // 2) - (len(mapa) // 2)
    
    for i in range(len(mapa)):
        for j in range(len(mapa[i])):
            if [i, j] == player.posicao:
                stdscr.addstr(mapa_inicio_y + i, mapa_inicio_x + j * 2, "M") 
            elif mapa[i][j] == 'X':  
                stdscr.addstr(mapa_inicio_y + i, mapa_inicio_x + j * 2, "X")
            elif mapa[i][j] == 'I':  
                stdscr.addstr(mapa_inicio_y + i, mapa_inicio_x + j * 2, "I")
            elif mapa[i][j] == 'C':  
                stdscr.addstr(mapa_inicio_y + i, mapa_inicio_x + j * 2, "C")
            else:
                stdscr.addstr(mapa_inicio_y + i, mapa_inicio_x + j * 2, ".") 

    for bloco in blocos:
        bloco_x, bloco_y = bloco.posicao
        stdscr.addstr(mapa_inicio_y + bloco_x, mapa_inicio_x + bloco_y * 2, "B", curses.color_pair(2) | curses.A_BOLD) 

    stdscr.refresh()



def turno_batalha(stdscr, player, inimigo, mapa, items, music_channel):
    if inimigo.derrotado:
        return True

    stdscr.clear()
    stdscr.addstr(0, 0, f"Início do turno de {player.name}! Vida: {player.vida}, Pontos: {player.pontos}")
    stdscr.addstr(1, 0, f"Inimigo: {inimigo.nome}, Vida: {inimigo.vida}")
    stdscr.addstr(3, 0, "Escolha sua ação: [Q] Pular, [E] Desviar")
    
    for i, item in enumerate(items):
        stdscr.addstr(5 + i, 0, f"[{i + 1}] {item.tipo} - Efeito: {item.efeito}")
    
    stdscr.refresh()

    while True:
        key = stdscr.getch()

        if ord('1') <= key < ord('1') + len(items):
            chosen_index = key - ord('1')
            item = items[chosen_index]
            dano = player.atacar(item, inimigo)
            stdscr.addstr(10, 0, f"{inimigo.nome} sofreu {dano} de dano pelo {item.tipo}!")
            player.pontos += inimigo.pontos
            break
        
        elif key == ord('q') or key == ord('Q'):
            inimigo.perder_vida(inimigo.vida) 
            stdscr.addstr(10, 0, f"{inimigo.nome} foi derrotado!")
            player.pontos += inimigo.pontos
            break

        elif key == ord('e') or key == ord('E'):
            player.desviar(mapa)
            break

        stdscr.refresh()

        if inimigo.vida <= 0:
            stdscr.addstr(12, 0, f"{inimigo.nome} foi derrotado! Você ganhou {inimigo.pontos} pontos.")
            stdscr.refresh()
            curses.napms(2000)
            mapa[inimigo.posicao[0]][inimigo.posicao[1]] = 'X'
            return True  

        if player.vida <= 0:
            stdscr.addstr(14, 0, f"{player.name} perdeu toda a sua vida. Game Over!")
            stdscr.refresh()
            curses.napms(2000)

            music_channel.stop()
            death_music_path = os.path.join(os.path.dirname(__file__), "death.mp3")
            pygame.mixer.music.load(death_music_path)
            pygame.mixer.music.play()
            
            stdscr.clear()
            stdscr.addstr(0, 0, "Deseja continuar? Sim [S], Não [N]")
            stdscr.refresh()

            while True:
                key = stdscr.getch()
                if key == ord('s') or key == ord('S'):
                    if player.salvou_checkpoint:
                        player.posicao = player.checkpoint[:]
                        player.vida = 100 
 
                        mapa[inimigo.posicao[0]][inimigo.posicao[1]] = 'I'
                        pygame.mixer.music.stop()

                        music_path = os.path.join(os.path.dirname(__file__), "mario_music.mp3")
                        music_channel.play(pygame.mixer.Sound(music_path), loops=-1)
                        return True  
                    else:
                        stdscr.addstr(1, 0, "Você precisa passar pelo Checkpoint!")
                        stdscr.refresh()
                        curses.napms(3000)
                        player.vida = 100
                        player.posicao = [0, 0]
                        pygame.mixer.music.stop()

                        music_path = os.path.join(os.path.dirname(__file__), "mario_music.mp3")
                        music_channel.play(pygame.mixer.Sound(music_path), loops=-1)
                        return True  
                        
                elif key == ord('n') or key == ord('N'):
                    return False  
                else:
                    stdscr.addstr(1, 0, "Escolha inválida! Pressione S ou N.")
                    stdscr.refresh()
                    curses.napms(1000)  

        stdscr.refresh()
        curses.napms(1000)

        if not inimigo.derrotado:
            dano_inimigo = inimigo.atacar()
            player.vida -= dano_inimigo
            stdscr.addstr(16, 0, f"{inimigo.nome} atacou {player.name} causando {dano_inimigo} de dano!")
            stdscr.refresh()

    return True


def entrar_fase(stdscr, player, mundo, fase):
    from character import get_block_item, get_inventory_items, insert_item_into_inventory
    curses.curs_set(0)  # Desabilitar o cursor
    stdscr.nodelay(1)  # Não bloquear na espera de uma tecla
    stdscr.timeout(100)  # Timeout para obter uma tecla

    fim_fase = [7, 7]  # Definição do final da fase

    # Criando o mapa (matriz) 8x8
    mapa = gera_matriz()
    player.mapa = mapa  # Definindo o mapa do jogador
    inimigos = get_inimigo_by_fase(fase.id_phase, mapa)  # Pegando inimigos na fase
    blocos = get_blocos_by_fase(fase.id_phase, mapa)  # Pegando blocos na fase

    pygame.mixer.init()
    pygame.mixer.set_num_channels(2)

    music_channel = pygame.mixer.Channel(0)
    music_path = os.path.join(os.path.dirname(__file__), "mario_music.mp3")
    music_channel.play(pygame.mixer.Sound(music_path), loops=-1)

    stdscr.clear()
    stdscr.addstr(0, 0, f"Escolha a direção de {player.name} para começar a fase:")
    stdscr.addstr(1, 0, "Pressione as setas esquerda (←) ou direita (→) para escolher")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            player.posicao = [0, 0]
            break
        elif key == curses.KEY_LEFT:
            player.posicao = [7, 0]
            break

    while player.vida > 0:
        exibir_mapa(stdscr, player, mapa, mundo, fase, blocos)

        # Verifica se o jogador chegou ao fim da fase
        if player.posicao == fim_fase:
            player.pontos += 100
            stdscr.clear()
            stdscr.addstr(0, 0, f"Parabéns! {player.name} completou a fase com {player.pontos} pontos!")
            stdscr.refresh()
            curses.napms(2000)

            music_channel.stop()

            music_path = os.path.join(os.path.dirname(__file__), "music_ending.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            return "venceu"

        row = 10

        for bloco in blocos:
            if player.posicao == bloco.posicao:
                player.pontos += 10
                stdscr.addstr(row, 0, f"{player.name} encontrou um bloco!")
                row += 1
                stdscr.addstr(row, 0, "[1] Bater no bloco")
                row += 1
                stdscr.addstr(row, 0, "[2] Ignorar bloco")
                stdscr.refresh()

                sound_channel = pygame.mixer.Channel(1)
             #   block_hit_sound = os.path.join(os.path.dirname(__file__), "block_hit.mp3")
             #  sound_channel.play(pygame.mixer.Sound(block_hit_sound))

                curses.napms(4000)
                choice = stdscr.getkey()

                if choice == "1":
                    stdscr.addstr(row + 1, 0, "Você bateu no bloco!")
                    stdscr.refresh()
                    stdscr.getch()  # Pausa para o usuário ler a mensagem

                    item_description = get_block_item(bloco, player)
                    stdscr.addstr(row + 1, 0, f"{item_description}")
                    curses.napms(3000)
                    stdscr.refresh()
                    stdscr.refresh()  # Atualiza a tela para exibir a descrição do item

                    if item_description:
                        stdscr.addstr(row + 3, 0, f"Você encontrou: {item_description}!")
                        row += 1
                        curses.napms(3000)
                        stdscr.refresh()
                    else:
                        stdscr.addstr(row + 3, 0, "O bloco estava vazio.")
                        curses.napms(3000)
                        stdscr.refresh()
                    
                    stdscr.refresh()  # Atualiza a tela para exibir a mensagem de encontro
                    stdscr.getch()  # Pausa para o usuário ler a mensagem

                    stdscr.addstr(row, 0, "Itens no seu inventário:")
                    curses.napms(3000)
                    stdscr.refresh()  # Atualiza a tela para exibir o cabeçalho do inventário

                    inventory_items = get_inventory_items(player.id)
                    if isinstance(inventory_items, list):
                        for i, item in enumerate(inventory_items):
                            stdscr.addstr(row + 5 + i, 0, f"{item.tipo} (Efeito: {item.efeito}) - {item.quantidade} unidades")
                            curses.napms(3000)
                            stdscr.refresh()
                    else:
                        stdscr.addstr(row + 5, 0, inventory_items)
                        curses.napms(3000)
                        stdscr.refresh()
                    
                    stdscr.refresh()  # Atualiza a tela para exibir os itens do inventário
                    stdscr.getch()  # Pausa para o usuário ler o inventário

                    mapa[bloco.posicao[0]][bloco.posicao[1]] = '.'
                    blocos.remove(bloco)
                    break

                elif choice == "2": 
                    stdscr.addstr(row + 1, 0, "Você ignorou o bloco.")
                    stdscr.refresh()
                    stdscr.getch()
                    break 
        key = stdscr.getch()

        if key == curses.KEY_UP:
            player.mover("UP", mapa)
        elif key == curses.KEY_DOWN:
            player.mover("DOWN", mapa)
        elif key == curses.KEY_LEFT:
            player.mover("LEFT", mapa)
        elif key == curses.KEY_RIGHT:
            player.mover("RIGHT", mapa)

        # Verifica se encontrou um inimigo
        for inimigo in inimigos:
            if player.posicao == inimigo.posicao:
                inventory_items = get_inventory_items(player.id)
                batalha_ativa = turno_batalha(stdscr, player, inimigo, mapa, inventory_items, music_channel)
                if not batalha_ativa:
                    break

    stdscr.clear()
    stdscr.addstr(0, 0, "Game Over! Você perdeu todas as vidas.")
    stdscr.refresh()
    curses.napms(2000)
    return "perdeu"