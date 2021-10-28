# -*- coding: utf8 -*-
import pygame
import random

X_SIZE = 1200
Y_SIZE = 800
WIN_SIZE = (X_SIZE, Y_SIZE)

# Game colors
COLOR_BACKGROUND = (85, 170, 85)

# Other constants
SUITS = {'Heart': 1, 'Diamond': 2, 'Club': 3, 'Spade': 0}
VALUES52 = {'Ace': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9,
            'Jack': 10, 'Queen': 11, 'King': 12}
VALUES36 = {'Ace': 0, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9,
            'Jack': 10, 'Queen': 11, 'King': 12}

IMG_SIZE_CARD_SCALED_X = 169
IMG_SIZE_CARD_SCALED_Y = 253
IMG_SIZE_CARD = (IMG_SIZE_CARD_SCALED_X, IMG_SIZE_CARD_SCALED_Y)
IMG_CARD_SHEET = pygame.image.load('cards.png')
IMG_CARD_BACK = pygame.image.load('card_back.png')
img_card_sheet = None
img_card_back = None

trump_suit = None

STATE_GAME_SHUFFLE = 100

STATE_DECK_SHUFFLE = 1000
STATE_DECK_GAME_ON = 1010


def get_image(suit, value):
    offset_x = 14
    offset_y = 14
    size_x = 182.16
    size_y = 266
    i = VALUES36[value]
    j = SUITS[suit]
    img = img_card_sheet.subsurface(pygame.Rect((offset_x + int(size_x * i), offset_y + size_y * j), IMG_SIZE_CARD))
    img = pygame.transform.scale(img, (IMG_SIZE_CARD_SCALED_X, IMG_SIZE_CARD_SCALED_Y))
    color = img.get_at((0, 0))
    img.set_colorkey(color)
    return img


def rank(card):
    """
    Card ordering function. Used to sort cards in player hands by suits and values
    :param card: Card for which rank is being computed
    :return: Card rank. Higher rank is the righter sorted position of the card
    """
    rk = card.rank()
    if card.suit == trump_suit:
        return rk * 100
    else:
        return rk * 10 * SUITS[card.suit]


# Класс карта
class Card:
    def __init__(self, suit, value, show_face=False):
        self.suit = suit
        self.value = value
        self.show_face = show_face
        self.img_face = get_image(self.suit, self.value)

    def __str__(self):
        return self.suit + " " + self.value

    def __repr__(self):
        return self.suit + " " + self.value

    def rank(self):
        """
        Returns rank of the card. Higher rank card beats lower rank card of the same suit
        :return: Rank of the card
        """
        return (VALUES36[self.value] + 13) % 14

    def beats(self, card):
        """
        Checks whether this cards beats the card coming as input
        :param card: Card to be checked if it is beaten by this card
        :return: True if this card beats input card; False otherwise. If suits are different then return False unless
        this card has a trump suit
        """
        this_value = self.rank()
        other_value = card.rank()
        if self.suit == card.suit:
            return this_value > other_value
        else:
            return self.suit == trump_suit

    def draw(self, surface, x, y, sx=1.0, sy=1.0, angle=0.0):
        if self.show_face:
            img = self.img_face
        else:
            img = img_card_back
        w = img.get_width()
        h = img.get_height()
        img = pygame.transform.scale(img, (int(w*sx), int(h*sy)))
        img = pygame.transform.rotate(img, angle)
        surface.blit(img, (x, y))


class Cards:
    def __init__(self, cards):
        self.cards = cards

    def draw(self, surface, x, y):
        xx = x
        for card in self.cards:
            card.draw(surface, xx, y)
            xx += IMG_SIZE_CARD_SCALED_X / 5


class Deck36(Cards):
    def __init__(self):
        cards = list()
        for suit in SUITS:
            for value in VALUES36:
                cards.append(Card(suit, value))
        super(Deck36, self).__init__(cards)
        self.state = STATE_DECK_SHUFFLE

    def shuffle(self):
        random.shuffle(self.cards)
        global trump_suit
        trump_suit = self.cards[-1].suit

    def draw_deck_and_trump_card(self, surface, x, y):
        """
        Draws deck at bottom of which there is a trump card facing up
        :param surface: Surface to draw on
        :param x: left coordinate of the deck
        :param y: Upper coordinate of the deck
        :return: None
        """
        n = len(self.cards)
        if n > 0:
            self.cards[-1].draw(surface, x, y + (IMG_SIZE_CARD_SCALED_Y - IMG_SIZE_CARD_SCALED_X) / 2)
            if n < 10:
                nn = n
            else:
                nn = 10

            xx = x
            for i in range(nn - 1):
                self.cards[-i - 2].draw(surface, xx, y)
                xx += 3

    def draw_shuffle(self, surface, x, y):
        """
        Draws cards being shuffled
        :param surface: Surface to draw on
        :param x: left coordinate of the deck
        :param y: Upper coordinate of the deck
        :return: None
        """
        x1 = x
        y1 = y
        x2 = x+100
        y2 = y
        n = int(len(self.cards)/2)
        aa = n/2
        for i in range(n):
            card_left = self.cards[i]
            card_right = self.cards[-i]
            card_left.draw(surface, x1, y1, angle=aa)
            card_right.draw(surface, x2, y2, angle=-aa)
            x1 += 3
            x2 -= 3
            aa += 0.5

    def draw(self, surface, x, y):
        if self.state == STATE_DECK_GAME_ON:
            self.draw_deck_and_trump_card(surface, x, y)
        elif self.state == STATE_DECK_SHUFFLE:
            self.draw_shuffle(surface, x, y)


class Player(Cards):
    def __init__(self, cards, show_face=False):
        super(Player, self).__init__(cards)
        self.trump_suit = trump_suit
        for card in self.cards:
            card.show_face = show_face

    def sort(self):
        self.cards = sorted(self.cards, key=rank)

    def draw(self, surface, x, y):
        n = len(self.cards)
        xx = x
        for i in range(n):
            self.cards[i].draw(surface, xx, y)
            xx += IMG_SIZE_CARD_SCALED_X / 8


class GameEngine:
    def __init__(self):
        self.deck = Deck36()
        self.human = None
        self.ai = None
        self.state = STATE_GAME_SHUFFLE

    def update(self):
        """
        Called on every frame update. Intended for game engine state update
        :return: None
        """

    def draw(self, surface):
        surface.fill(COLOR_BACKGROUND)
        self.deck.draw(surface, 10, 300)
        if self.human is not None:
            self.human.draw(surface, 10, 10)
        if self.ai is not None:
            self.ai.draw(surface, 10, 500)


def main():
    # Initialize PyGame
    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Cards")
    clock = pygame.time.Clock()

    # Initialize sprite sheet
    global img_card_sheet
    img_card_sheet = IMG_CARD_SHEET.convert()
    global img_card_back
    img_card_back = IMG_CARD_BACK.convert()
    color = img_card_back.get_at((0, 0))
    img_card_back.set_colorkey(color)
    img_card_back = pygame.transform.scale(img_card_back, (IMG_SIZE_CARD_SCALED_X, IMG_SIZE_CARD_SCALED_Y))

    # Create game
    game = GameEngine()

    do_game = True
    while do_game:
        clock.tick(10)
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                do_game = False

        # Redraw
        game.draw(screen)
        pygame.display.flip()

    # Освобождаем память по окончании игры
    pygame.quit()


if __name__ == "__main__":
    main()
