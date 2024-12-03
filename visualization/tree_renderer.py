import asyncio
import random

import pygame as pg
from pygame.sprite import Sprite

from utils.logger import logger
from visualization.observer import DebateTreeSubject, Observer

# Font used for all text
pg.init()
font = pg.font.SysFont("Arial", 30)


class Node(Sprite):
    def __init__(self, x, y, node_data):
        super().__init__()
        self.image = pg.Surface([100, 100])
        self.image.fill((255, 0, 0))
        self.image.set_colorkey((255, 0, 0))
        self.node_data = node_data

        self.color = self._score_to_color(node_data[2]["evaluation"])
        self.text = font.render(f"{node_data[1]}", True, (0, 0, 0))

        pg.draw.circle(self.image, (self.color), (50, 50), 50)
        self.image.blit(self.text, (40, 35))

        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def _score_to_color(self, score: float):
        r = max(0, min(255, int(255 * (1 - score))))
        g = max(0, min(255, int(255 * score)))
        return (r, g, 0)


class TreeRenderer(Observer):
    def __init__(self, debate_tree_subject: DebateTreeSubject):
        self.debate_tree_subject = debate_tree_subject
        self.debate_tree_subject.attach(self)

        # Points and nodes
        self.nodes = []
        self.node = None

        # Mouse position
        self.x, self.y = 0, 0
        self.mouse_pressed = False
        self.node_selected = False

        self.screen = pg.display.set_mode((1280, 720))
        self.surface = pg.Surface([3000, 3000])
        self.source = pg.Rect(0, 0, 1280, 720)

        pg.display.set_caption("Tree Renderer")

        self.text = font.render("Testing", True, (0, 0, 0))
        self.score = font.render("Score: 0.0", True, (0, 0, 0))

    async def start(self, quit_event):
        await self.main_loop(quit_event)

    def update(self, subject):
        # Update debate_tree based on new information
        self.nodes = []
        for node_id, node_data in subject.debate_tree.items():
            new_node = Node(
                random.randint(0, 1280) - self.source.x,
                random.randint(0, 720) - self.source.y,
                node_data,
            )
            self.nodes.append(new_node)

        logger.info("Complete adding new nodes to modified renderer")

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
                self.text = font.render(
                    f"Argument: {self.node.node_data[2]["argument"]}",
                    True,
                    (255, 255, 255),
                )
                self.score = font.render(
                    f"Score: {int(self.node.node_data[2]["evaluation"] * 10000) / 100.00} / 100.00",
                    True,
                    (255, 255, 255),
                )
                self.node.rect.center = (self.x, self.y)

            # Draw backgrounds
            self.surface.fill((52, 58, 64))
            self.screen.fill((33, 37, 41))

            for node in self.nodes:
                if node.node_data[2]["parent"] != -1:
                    pg.draw.line(
                        self.surface,
                        (233, 236, 239),
                        (node.rect.centerx, node.rect.centery),
                        (
                            self.nodes[node.node_data[2]["parent"]].rect.centerx,
                            self.nodes[node.node_data[2]["parent"]].rect.centery,
                        ),
                        5,
                    )

            pg.draw.line(self.surface, (233, 236, 239), (640, 360), (self.x, self.y), 5)

            for node in self.nodes:
                self.surface.blit(node.image, node.rect)

            self.screen.blit(self.surface, self.source)
            self.screen.blit(self.text, (0, 600))
            self.screen.blit(self.score, (0, 650))

            pg.display.flip()
            await asyncio.sleep(1 / 60)

        pg.quit()
