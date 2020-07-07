import pygame, sys

pygame.init()

surface = pygame.display.set_mode((350, 250), pygame.RESIZABLE)
pygame.display.set_caption("Example resizable window")

while True:
    surface.fill((255,255,255))

    # shape to check window resizable.
    pygame.draw.rect(surface, (200,0,0), (surface.get_width()/3,
      surface.get_height()/3, surface.get_width()/3,
      surface.get_height()/3))

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            surface = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)