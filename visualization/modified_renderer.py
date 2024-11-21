import pygame as pg
from pygame import gfxdraw
import asyncio
import math

import random # testing

from utils.logger import logger

from visualization.observer import DebateTreeSubject, Observer

def line(points, x1: float, y1: float, x2: float, y2: float):
    dy: float = y2 - y1
    dx: float = x2 - x1

    length: int = int(math.sqrt(dy * dy + dx * dx))
    angle: float = math.atan2(dy, dx)

    for i in range(length):
        points.append((int(x1 + i * math.cos(angle)), int(y1 + i * math.sin(angle))))

class ModifiedRenderer(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)
        self.points = []
        self.running = True
        
        for _ in range(100):
            self.points.append((random.randint(0, 1280), random.randint(0, 720)))

        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Tree Renderer")
        

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
                    logger.debug("Mouse Down")
                if event.type == pg.MOUSEBUTTONUP:
                    logger.debug("Mouse Up")



            x, y = pg.mouse.get_pos()

            self.screen.fill((255, 255, 255))

            line(self.points, 0, 0, x, y)

            for p in self.points:
                gfxdraw.pixel(self.screen, p[0], p[1], (0, 0, 0))
            pg.draw.circle(self.screen, (0, 0, 255), (x, y), 75)
            
            self.clear()
            pg.display.flip()
            await asyncio.sleep(1/60)
        pg.quit()
