import pygame as pg
from pygame.sprite import Sprite
from pygame import gfxdraw
import asyncio

from utils.logger import logger

from visualization.observer import DebateTreeSubject, Observer

class Node(Sprite):
    def __init__(self):
        super().__init__()
        self.parent = 0


# def line(points, x1: float, y1: float, x2: float, y2: float):
#     dy: float = y2 - y1
#     dx: float = x2 - x1

#     length: int = int(math.sqrt(dy * dy + dx * dx))
#     angle: float = math.atan2(dy, dx)

#     for i in range(length):
#         points.append((int(x1 + i * math.cos(angle)), int(y1 + i * math.sin(angle))))

class ModifiedRenderer(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)
        self.points = []
        self.running = True
        self.x, self.y = 0, 0

        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Tree Renderer")
        
        self.font = pg.font.SysFont('Arial', 30)
        self.text = self.font.render("Testing", True, (0, 0, 0))

    async def start(self):
        await self.main_loop()

    def update(self, subject):
        # Update debate_tree based on new information
        pass
    
    def clear(self):
        self.points = []

    async def main_loop(self):
        while(self.running):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    logger.debug("Down")
                if event.type == pg.MOUSEMOTION:
                    self.x, self.y = pg.mouse.get_pos()
                if event.type == pg.MOUSEBUTTONUP:
                    logger.debug("Mouse Up")
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.running = False

            self.screen.fill((255, 255, 255))

            # line(self.points, 1280, 0, x, y)
            pg.draw.line(self.screen, (100, 100, 100), (640, 360), (self.x, self.y), 5)

            for p in self.points:
                gfxdraw.pixel(self.screen, p[0], p[1], (0, 0, 0))
            pg.draw.circle(self.screen, (0, 0, 255), (self.x, self.y), 75)
            pg.draw.circle(self.screen, (0, 0, 0), (640, 360), 50)
            self.screen.blit(self.text, (0, 600))
            
            self.clear()
            pg.display.flip()
            await asyncio.sleep(1/60)
            
        pg.quit()
