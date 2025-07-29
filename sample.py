import pygame
pygame.init()
pygame.mixer.init()
sound = pygame.mixer.Sound('background.wav')
sound.play()
pygame.time.wait(54000)  # Let it play for 9 seconds