import pygame as pg
from pygame.sprite import Sprite
from pygame import gfxdraw
import math
import asyncio

import random # TEMP

from utils.logger import logger

from visualization.observer import DebateTreeSubject, Observer

class Node(Sprite):
    def __init__(self, x, y,):
        super().__init__()
        # self.parent = 0
        self.image = pg.Surface([100, 100])
        self.image.set_colorkey((0, 0, 0))

        pg.draw.circle(self.image, ((0, 0, 255)), (50, 50), 50)

        self.rect = self.image.get_rect()
        self.rect.center = x, y

# def line(points, x1: float, y1: float, x2: float, y2: float):
#     dy: float = y2 - y1
#     dx: float = x2 - x1

#     length: int = int(math.sqrt(dy * dy + dx * dx))
#     angle: float = math.atan2(dy, dx)

#     for i in range(length):
#         x = int(x1 + i * math.cos(angle))
#         y = int(y1 + i * math.sin(angle))
#         points.append((x - 1, y - 1))
#         points.append((x, y))
#         points.append((x + 1, y + 1))

class ModifiedRenderer(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)

        # Points and nodes
        self.points = []
        self.connections = [] # Connections between nodes
        self.nodes = pg.sprite.Group()
        self.node = None

        # TEMP test nodes
        for _ in range(10):
            new_node = Node(random.randint(0, 1280), random.randint(0, 720))
            self.nodes.add(new_node)

        # Mouse position
        self.x, self.y = 0, 0
        self.mouse_pressed = False
        self.node_selected = False

        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Tree Renderer")
        
        self.font = pg.font.SysFont('Arial', 30)
        self.text = self.font.render("Testing", True, (0, 0, 0))

    async def start(self, quit_event):
        await self.main_loop(quit_event)

    def update(self, subject):
        # Update debate_tree based on new information
        for node in subject:
            if node not in self.debate_tree_subject:
                # Handle new nodes
                pass
        
        # After set the new debate_tree_subject
        self.debate_tree_subject = subject
    
    def clear(self):
        self.points = []

    async def main_loop(self, quit_event):
        while not asyncio.Event.is_set(quit_event):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quit_event.set()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse_pressed = True
                    if pg.mouse.get_pressed()[0]:
                        if not self.node_selected:
                            for node in self.nodes:
                                if node.rect.collidepoint(event.pos):
                                    self.node = node
                                    self.node_selected = True
                                    
                            logger.debug("Left Click")
                            logger.debug("Node clicked")
                        else:
                            self.node = None
                            self.node_selected = False
                    if pg.mouse.get_pressed()[2]:
                        self.node = None
                        self.node_selected = False
                        logger.debug("Right Click")
                        logger.debug("Node Dropped")
                if event.type == pg.MOUSEMOTION:
                    self.x, self.y = event.pos
                if event.type == pg.MOUSEBUTTONUP:
                    self.mouse_pressed = False
                    logger.debug("Mouse Up")
                    pass
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        quit_event.set()
            
            if self.node_selected:
                self.text = self.font.render(f"Argument: Node argument x:{self.node.rect.centerx} y:{self.node.rect.centery} pretend this is long and covers alot but it might go off screen\n But how about this this is taking forvere lol trying to go over the line", True, (0, 0, 0))
                self.node.rect.center = (self.x, self.y)


            self.screen.fill((52, 58, 64))

            self.nodes.update()

            # line(self.points, 640, 360, self.x, self.y)
            pg.draw.line(self.screen, (233, 236, 239), (640, 360), (self.x, self.y), 5)

            self.nodes.draw(self.screen)
            
            # for p in self.points:
            #     gfxdraw.pixel(self.screen, p[0], p[1], (255, 255, 255))

            self.screen.blit(self.text, (0, 600))
            
            self.clear()
            pg.display.flip()
            await asyncio.sleep(1/60)

        pg.quit()
