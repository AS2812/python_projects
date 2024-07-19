import random
import pygame
import time

pygame.font.init()

Width, Height = 800, 600
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Dodge")
BG = pygame.transform.scale(pygame.image.load("BG.png"), (Width, Height))

PlayerImg = pygame.image.load("alien.png")
PlayerImg = pygame.transform.scale(PlayerImg, (80, 120))

StarImg = pygame.image.load("star.png")
StarImg = pygame.transform.scale(StarImg, (30, 30))

PlayerWidth = PlayerImg.get_width()
PlayerHeight = PlayerImg.get_height()
PlayerVel = 5
StarWidth = StarImg.get_width()
StarHeight = StarImg.get_height()
StarVel = 3
Font = pygame.font.SysFont("comicsans", 30)


PlayerMask = pygame.mask.from_surface(PlayerImg)
StarMask = pygame.mask.from_surface(StarImg)

def draw(player, elapsed_time, Stars):
    Win.blit(BG, (0, 0))
    time_text = Font.render(f"Time: {round(elapsed_time)}s", 1, "white")
    Win.blit(time_text, (10, 10))
    Win.blit(PlayerImg, (player.x, player.y))
    for Star in Stars:
        Win.blit(StarImg, (Star.x, Star.y))
    pygame.display.update()

def main():
    run = True
    Start_time = time.time()
    clock = pygame.time.Clock()
    player = pygame.Rect(200, Height - PlayerHeight, PlayerWidth, PlayerHeight)

    Star_add_increment = 2000
    Star_count = 0
    Stars = []
    hit = False
    while run:

        Star_count += clock.tick(60)
        elapsed_time = time.time() - Start_time

        if Star_count > Star_add_increment:
            for _ in range(3):
                Star_X = random.randint(0, Width - StarWidth)
                Star = pygame.Rect(Star_X, -StarHeight, StarWidth, StarHeight)
                Stars.append(Star)

            Star_add_increment = max(200, Star_add_increment - 50)
            Star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - PlayerVel >= 0:
            player.x -= PlayerVel
        if keys[pygame.K_RIGHT] and player.x + PlayerVel + PlayerWidth <= Width:
            player.x += PlayerVel

        for Star in Stars[:]:
            Star.y += StarVel
            if Star.y > Height:
                Stars.remove(Star)
            else:
                offset = (Star.x - player.x, Star.y - player.y)
                if PlayerMask.overlap(StarMask, offset):
                    Stars.remove(Star)
                    hit = True
                    break

        if hit:
            lostText = Font.render("You Lost!", 1, "white")
            Win.blit(lostText, (Width / 2 - lostText.get_width() / 2, Height / 2 - lostText.get_height() / 2))
            pygame.display.update()
            pygame.time.wait(4000)
            break

        draw(player, elapsed_time, Stars)

    pygame.quit()

if __name__ == "__main__":
    main()
