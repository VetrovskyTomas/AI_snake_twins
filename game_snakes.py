from world import GameWorld

if __name__ == '__main__':
    game = GameWorld()
    # game loop
    while True:
        # draw game
        game.update_game()

    print('Final Score', score)
    pygame.quit()