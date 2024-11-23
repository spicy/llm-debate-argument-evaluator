import pygame as pg
from pygame.sprite import Sprite
from pygame import gfxdraw
import math
import asyncio

import random # TEMP

from utils.logger import logger

from visualization.observer import DebateTreeSubject, Observer

class Node(Sprite):
    def __init__(self, x, y, node_data):
        super().__init__()
        # self.parent = 0
        self.image = pg.Surface([100, 100])
        self.image.set_colorkey((0, 0, 0))
        self.node_data = node_data

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

        # Mouse position
        self.x, self.y = 0, 0
        self.mouse_pressed = False
        self.node_selected = False

        pg.init()
        self.screen = pg.display.set_mode((1280, 720))
        self.surface = pg.Surface([3000, 3000])
        self.source = pg.Rect(0, 0, 1280, 720)
        
        pg.display.set_caption("Tree Renderer")
        
        self.font = pg.font.SysFont('Arial', 30)
        self.text = self.font.render("Testing", True, (0, 0, 0))

    async def start(self, quit_event):
        await self.main_loop(quit_event)

    def update(self, subject):
        # Update debate_tree based on new information
        for node_data in subject.debate_tree.items():
            if node_data not in self.debate_tree_subject:
                new_node = Node(random.randint(0, 1280) - self.source.x, random.randint(0, 720) - self.source.y, node_data)
                self.nodes.add(new_node)
        
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
                                if node.rect.collidepoint((self.x, self.y)):
                                    self.node = node
                                    self.node_selected = True
                                    
                            logger.debug("Left Click")
                            logger.debug("Node clicked")
                        else:
                            self.node = None
                            self.node_selected = False

                if event.type == pg.MOUSEMOTION:
                    self.x = event.pos[0] - self.source.x
                    self.y = event.pos[1] - self.source.y

                if event.type == pg.MOUSEBUTTONUP:
                    self.mouse_pressed = False
                    logger.debug("Mouse Up")
                
                if event.type == pg.KEYDOWN:
                    # Remove any possible typing keys not to accidently press them while typing quit
                    if event.key == pg.K_q:
                        quit_event.set()
                    if event.key == pg.K_UP:
                        self.source.y += 100
                    if event.key == pg.K_DOWN:
                        self.source.y -= 100

                    if event.key == pg.K_LEFT:
                        self.source.x += 100
                    if event.key == pg.K_RIGHT:
                        self.source.x -= 100
                    
                    if event.key == pg.K_MINUS:
                        self.source.width /= 2
                        self.source.height /= 2
                    
                    if event.key == pg.K_EQUALS:
                        self.source.width *= 2
                        self.source.height *= 2
                
            
            if self.node_selected:
                self.text = self.font.render(f"Argument: Node argument x:{self.node.rect.centerx} y:{self.node.rect.centery} pretend this is long and covers alot but it might go off screen\n But how about this this is taking forvere lol trying to go over the line", True, (0, 0, 0))
                self.node.rect.center = (self.x, self.y)

            self.surface.fill((52, 58, 64))
            self.screen.fill((33, 37, 41))

            self.nodes.update()

            # line(self.points, 640, 360, self.x, self.y)
            for node in self.nodes:
                if node.node_data[2]["parent"] != -1:
                    for parent_node in self.nodes:
                        if node.node_data[2]["parent"] == parent_node.node_data[1]:
                            pg.draw.line(self.surface, (233, 236, 239), (node.rect.centerx, node.rect.centery), (parent_node.rect.centerx, parent_node.rect.centery), 5)

            pg.draw.line(self.surface, (233, 236, 239), (640, 360), (self.x, self.y), 5)
            self.nodes.draw(self.surface)
            
            # for p in self.points:
            #     gfxdraw.pixel(self.screen, p[0], p[1], (255, 255, 255))

            self.screen.blit(self.surface, self.source)
            self.screen.blit(self.text, (0, 600))
            
            self.clear()
            pg.display.flip()
            await asyncio.sleep(1/60)

        pg.quit()
