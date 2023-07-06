#!/usr/bin/env python3

import os
import time
import pygame

from modules.gui_utils import *
from modules.marker import Marker
from modules.client import Client

# Setup pygame
pygame.init()
pygame.key.set_repeat(200, 25)
pygame.display.set_caption("MineCClicker!")
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

# Setup client
HOST = os.environ.get('HOST', None) or "127.0.0.1"
PORT = int(os.environ.get('PORT', None) or 9999)
CLIENT = Client(HOST, PORT)

# Game global variables
CURRENT_USER = None
CURRENT_BOARD = None

def main_menu():

    global CURRENT_USER

    # Title
    TITLE = Text(text="MAIN MENU")

    # Buttons
    SIGNUP_BUTTON = Button(text_input="SIGNUP", pos=(CENTER, 300))
    LOGIN_BUTTON = Button(text_input="LOGIN", pos=(CENTER, 400))
    CREATE_BOARD_BUTTON = Button(text_input="CREATE BOARD", pos=(CENTER, 500))
    LOAD_BOARD_BUTTON = Button(text_input="LOAD BOARD", pos=(CENTER, 600))
    PLAY_BUTTON = Button(text_input="PLAY", pos=(CENTER, 700))
    QUIT_BUTTON = Button(text_input="QUIT", pos=(CENTER, 800))
    buttons = [SIGNUP_BUTTON, LOGIN_BUTTON, CREATE_BOARD_BUTTON, LOAD_BOARD_BUTTON, PLAY_BUTTON, QUIT_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        # Render background and title
        SCREEN.fill(BG_COLOR)
        TITLE.render(SCREEN)
        render_image(SCREEN, LOGO, (275, 100))
        render_image(SCREEN, LOGO, (725, 100))

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if QUIT_BUTTON.checkForInput(event.pos):
                    gui_quit()
                if SIGNUP_BUTTON.checkForInput(event.pos):
                    gui_signup()
                    break
                if LOGIN_BUTTON.checkForInput(event.pos):
                    gui_login()
                    break
                
                # All the remaining commands require login
                if CURRENT_USER is None:
                    gui_message("You must be logged in!")
                    break

                if CREATE_BOARD_BUTTON.checkForInput(event.pos):
                    gui_create_board()
                    break
                if LOAD_BOARD_BUTTON.checkForInput(event.pos):
                    gui_load_board()
                    break
                if PLAY_BUTTON.checkForInput(event.pos):
                    if CURRENT_BOARD is None:
                        gui_message("You must load a board!")
                        break
                    _, msg = gui_play()
                    gui_message(msg)
                    break

        pygame.display.flip()

def gui_signup():

    # Title
    TITLE = Text(text="SIGNUP USER")

    # Input texts
    username = TextInput(placeholder="Username", y=250)
    password = TextInput(placeholder="Password", y=350)
    
    # Buttons
    SEND_BUTTON = Button(text_input="SEND", pos=(CENTER, 550))
    MENU_BUTTON = Button(text_input="MAIN MENU", pos=(CENTER, 650))
    buttons = [SEND_BUTTON, MENU_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        # Render background and title
        SCREEN.fill(BG_COLOR)
        TITLE.render(SCREEN)

        # Render input texts
        events = pygame.event.get()
        username.render(events, SCREEN)
        password.render(events, SCREEN)

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Handle clicks on input texts
                username.click(event.pos)
                password.click(event.pos)

                if MENU_BUTTON.checkForInput(event.pos):
                    return

                if SEND_BUTTON.checkForInput(event.pos):
                    if not username.isValid or not password.isValid:
                        continue
                    # Send signup request
                    res, msg = CLIENT.signup(username.value, password.value)
                    if not res:
                        gui_message(msg)
                    else:
                        gui_message("User signed up!")
                    return

        pygame.display.flip()
    
def gui_login():

    global CURRENT_USER

    # Title
    TITLE = Text(text="LOGIN USER")
    
    # Input texts
    username = TextInput(placeholder="Username", y=250)
    password = TextInput(placeholder="Password", y=350)

    # Buttons
    SEND_BUTTON = Button(text_input="SEND", pos=(CENTER, 550))
    MENU_BUTTON = Button(text_input="MAIN MENU", pos=(CENTER, 650))
    buttons = [SEND_BUTTON, MENU_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        # Render background and title
        SCREEN.fill(BG_COLOR)
        TITLE.render(SCREEN)

        # Render input texts
        events = pygame.event.get()
        username.render(events, SCREEN)
        password.render(events, SCREEN)

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Handle clicks on input texts
                username.click(event.pos)
                password.click(event.pos)

                if MENU_BUTTON.checkForInput(event.pos):
                    return

                if SEND_BUTTON.checkForInput(event.pos):
                    if not username.isValid or not password.isValid:
                        continue
                    # Send login request
                    res, msg = CLIENT.login(username.value, password.value)
                    if not res:
                        gui_message(msg)
                    else:
                        gui_message(f"Welcome back!")
                        CURRENT_USER = username.value
                    return  

        pygame.display.flip()

def gui_create_board():
    
    # Title
    TITLE = Text(text="CREATE BOARD")
    
    # Input texts
    name = TextInput(placeholder="Name", y=250)
    secret = TextInput(placeholder="Secret", y=350)
    seed = NumericInput(placeholder="Seed", y=450, max_value=2**64)
    board_dim = NumericInput(placeholder="Board dimension", y=550, max_value=BOARD_MAX_DIMENSION)
    num_bombs = NumericInput(placeholder="Number of bombs", y=650, max_value=BOARD_MAX_DIMENSION*BOARD_MAX_DIMENSION)

    # Buttons
    SEND_BUTTON = Button(text_input="SEND", pos=(CENTER, 750))
    MENU_BUTTON = Button(text_input="MAIN MENU", pos=(CENTER, 850))
    buttons = [SEND_BUTTON, MENU_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        # Render background and title
        SCREEN.fill(BG_COLOR)
        TITLE.render(SCREEN)

        # Render input texts
        events = pygame.event.get()
        name.render(events, SCREEN)
        secret.render(events, SCREEN)
        seed.render(events, SCREEN)
        board_dim.render(events, SCREEN)
        num_bombs.render(events, SCREEN)

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Handle clicks on input texts
                name.click(event.pos)
                secret.click(event.pos)
                seed.click(event.pos)
                board_dim.click(event.pos)
                num_bombs.click(event.pos)
                        
                if MENU_BUTTON.checkForInput(event.pos):
                    return

                if SEND_BUTTON.checkForInput(event.pos):
                    if not name.isValid or not secret.isValid or not seed.isValid or not board_dim.isValid or not num_bombs.isValid:
                        continue
                    if num_bombs.value > board_dim.value*board_dim.value:
                        gui_message("Too many bombs!")
                        return
                    # Send create board request
                    res, msg = CLIENT.create_board(name.value, secret.value, seed.value, board_dim.value, num_bombs.value)
                    if not res:
                        gui_message(msg)
                    else:
                        gui_message(f"Board created!")
                    return

        pygame.display.flip()
        
def gui_load_board():

    global CURRENT_BOARD
    
    # Title
    TITLE = Text("LOAD BOARD")
    
    # Input texts
    boardname = TextInput(placeholder="Name", y=250)

    # Buttons
    SEND_BUTTON = Button(text_input="SEND", pos=(CENTER, 550))
    MENU_BUTTON = Button(text_input="MAIN MENU", pos=(CENTER, 650))
    buttons = [SEND_BUTTON, MENU_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        # Render background and title
        SCREEN.fill(BG_COLOR)
        TITLE.render(SCREEN)

        # Render input texts
        events = pygame.event.get()
        boardname.render(events, SCREEN)

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)

        # Handle events
        for event in events:
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Handle clicks on input texts
                boardname.click(event.pos)

                if MENU_BUTTON.checkForInput(event.pos):
                    return

                if SEND_BUTTON.checkForInput(event.pos):
                    if not boardname.isValid:
                        continue
                    # Send load board request
                    res, msg = CLIENT.load_board(boardname.value)
                    if not res:
                        gui_message(msg)
                    else:
                        gui_message(f"Board loaded!")
                        CURRENT_BOARD = boardname.value
                    return  

        pygame.display.flip()

def gui_play():

    # Send play request
    res, msg = CLIENT.play()
    if not res:
        return res, msg
    
    # Initialize game
    game_seed, board_dim, num_bombs = msg
    flags_left = num_bombs
    board = [ [ Marker.COVERED for _ in range(board_dim) ] for _ in range(board_dim) ]
    graphic_board = [ [ None for _ in range(board_dim) ] for _ in range(board_dim) ]
    update_board = True
    game_over = False
    
    # Render background and logo
    SCREEN.fill(BG_COLOR)
    render_image(SCREEN, LOGO, (CENTER, 50))

    # Render seed info
    SCREEN.blit(SEED, SEED.get_rect(center=(250, 40)))
    SEED_TEXT = Text(text=f"{game_seed}", font_size=20, center=(250, 60), color=TEXT_COLOR)
    SEED_TEXT.render(SCREEN)

    # Render flags info
    SCREEN.blit(FLAG, SEED.get_rect(center=(750, 40)))
    FLAGS_TEXT = Text(text=f"{flags_left}/{num_bombs}", font_size=20, center=(750, 60), color=FLAGS_COLOR)
    FLAGS_TEXT.render(SCREEN)
    
    # Buttons
    CHECK_BUTTON = Button(text_input="CHECK BOMBS", pos=(CENTER, 950), font=25)
    buttons = [CHECK_BUTTON]
    
    while True:
        CLOCK.tick(FPS)

        if update_board and not game_over:
            render_board(SCREEN, board_dim, board, graphic_board)
            update_board = False
        
        if game_over:
            time.sleep(0.2)
            render_game_over(SCREEN, board_dim, board, graphic_board)
            time.sleep(2)
            return None, "BOOOOOOOM!"

        # Render buttons
        render_buttons(SCREEN, pygame.mouse.get_pos(), buttons)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                if CHECK_BUTTON.checkForInput(event.pos):
                    # Send check win request
                    res, msg = CLIENT.check_win(board)
                    return res, msg

                if not check_inside(event.pos, board_dim):
                    continue

                # Get cell coordinates
                row, col = get_coords(event.pos, board_dim)

                # Left click: uncover cell
                if event.button == PygameClick.LEFT.value:

                    # Check if cell is still uncovered
                    if not check_move(board, row, col):
                        continue

                    # Send uncover request
                    res, msg = CLIENT.uncover(row, col)
                    if not res:
                        return res, msg
                    
                    cell, curr_board = msg
                    board[row][col] = Marker(cell) if cell in Marker.values() else cell
                    update_board = True
                    if board[row][col] == Marker.BOMB:
                        for row in range(board_dim):
                            for col in range(board_dim):
                                if curr_board[row][col] == Marker.BOMB:
                                    board[row][col] = Marker.BOMB
                        game_over = True
                    break

                # Right click: flag or unflag cell
                elif event.button == PygameClick.RIGHT.value:
                    
                    if board[row][col] == Marker.FLAG:
                        if flags_left == num_bombs:
                            continue
                        board[row][col] = Marker.COVERED
                        flags_left += 1
                    elif board[row][col] == Marker.COVERED:
                        if flags_left == 0:
                            continue
                        board[row][col] = Marker.FLAG
                        flags_left -= 1
                    else:
                        continue
                    
                    update_board = True

                    # Update flags info
                    FLAGS_TEXT = Text(text=f"    {flags_left}/{num_bombs}    ", font_size=20, center=(750, 60), color=FLAGS_COLOR)
                    FLAGS_TEXT.render(SCREEN)
                    break
        
        pygame.display.flip()

def gui_message(message, submessage=None):

    SCREEN.fill(BG_COLOR)

    MESSAGE = Text(message, font_size=40)
    MESSAGE.render(SCREEN)

    if submessage:
        SUBMESSAGE = Text(submessage, center=(CENTER, 190), font_size=35)
        SUBMESSAGE.render(SCREEN)

    MENU_BUTTON = Button(text_input="MAIN MENU", pos=(CENTER, 350))
    QUIT_BUTTON = Button(text_input="QUIT", pos=(CENTER, 450))

    while True:
        CLOCK.tick(FPS)
        pos = pygame.mouse.get_pos()

        # Render buttons
        for button in [MENU_BUTTON, QUIT_BUTTON]:
            button.changeColor(pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gui_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if QUIT_BUTTON.checkForInput(pos):
                    gui_quit()
                if MENU_BUTTON.checkForInput(pos):
                    return

        pygame.display.flip()

def gui_quit():
        
    CLIENT.quit()
    pygame.quit()
    exit()

if __name__ == "__main__":
    main_menu()



