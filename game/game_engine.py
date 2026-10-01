import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.score = 0
        self.total_attempts = 0
        self.streak = 0
        self.feedback_msg = "Solve the card and press Enter!"
        self.feedback_color = (200, 205, 215)

        self.num_a = 0
        self.num_b = 0
        self.operator = "+"

        self.time_limit_ms = 10000
        self.card_start_ms = 0

        box_w, box_h = 130, 44
        self.input_box = TextBox(width // 2 - 110, 230, box_w, box_h)
        self.submit_btn = pygame.Rect(width // 2 + 30, 230, 90, box_h)

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_card = pygame.font.SysFont(None, 56)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.generate_new_card()

    def generate_new_card(self):
        self.num_a = random.randint(3, 15)
        self.num_b = random.randint(2, 12)
        self.operator = random.choice(["+", "-", "*", "/"])
        if self.operator == "-" and self.num_a < self.num_b:
            self.num_a, self.num_b = self.num_b, self.num_a
        elif self.operator == "/":
            self.num_a = self.num_b * random.randint(2, 12)

        self.input_box.clear()
        self.card_start_ms = pygame.time.get_ticks()

    def compute_expected_answer(self):
        if self.operator == "+":
            return self.num_a + self.num_b
        if self.operator == "-":
            return self.num_a - self.num_b
        if self.operator == "*":
            return self.num_a * self.num_b
        return self.num_a // self.num_b

    def score_multiplier(self):
        if self.streak >= 5:
            return 3
        if self.streak >= 3:
            return 2
        return 1

    def submit_answer(self):
        val_str = self.input_box.text.strip()
        if not val_str or val_str == "-":
            self.feedback_msg = "Type an answer first!"
            self.feedback_color = (240, 175, 40)
            return

        user_answer = int(val_str)
        expected = self.compute_expected_answer()
        self.total_attempts += 1

        if user_answer == expected:
            self.streak += 1
            points = self.score_multiplier()
            self.score += points
            self.feedback_msg = f"CORRECT! {self.num_a} {self.operator} {self.num_b} = {expected} (+{points})"
            self.feedback_color = (80, 230, 110)
            self.generate_new_card()
        else:
            self.streak = 0
            self.feedback_msg = f"WRONG! Expected {expected}."
            self.feedback_color = (240, 75, 75)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_answer()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_answer()

    def time_left_ms(self):
        elapsed = pygame.time.get_ticks() - self.card_start_ms
        return max(0, self.time_limit_ms - elapsed)

    def update(self):
        if self.time_left_ms() > 0:
            return

        self.total_attempts += 1
        self.streak = 0
        self.feedback_msg = f"TIME'S UP! Answer was {self.compute_expected_answer()}."
        self.feedback_color = (240, 75, 75)
        self.generate_new_card()

    def render(self, screen):
        screen.fill((25, 29, 37))

        title_surf = self.font_title.render("Math Flashcards Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 18))

        hud_text = f"Score: {self.score}  |  Attempts: {self.total_attempts}  |  Streak: {self.streak} (x{self.score_multiplier()})"
        score_surf = self.font_hud.render(hud_text, True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 58))

        card_rect = pygame.Rect(self.width // 2 - 130, 95, 260, 110)
        pygame.draw.rect(screen, (240, 242, 245), card_rect, border_radius=12)
        pygame.draw.rect(screen, (85, 120, 175), card_rect, width=3, border_radius=12)

        card_str = f"{self.num_a}  {self.operator}  {self.num_b}"
        card_surf = self.font_card.render(card_str, True, (25, 30, 42))
        screen.blit(card_surf, (card_rect.centerx - card_surf.get_width() // 2, card_rect.centery - card_surf.get_height() // 2))

        time_frac = self.time_left_ms() / self.time_limit_ms
        timer_bg = pygame.Rect(card_rect.x, card_rect.bottom + 8, card_rect.width, 10)
        timer_fill = pygame.Rect(timer_bg.x, timer_bg.y, int(timer_bg.width * time_frac), timer_bg.height)
        timer_color = (80, 200, 110) if time_frac > 0.3 else (240, 75, 75)
        pygame.draw.rect(screen, (60, 65, 78), timer_bg, border_radius=5)
        pygame.draw.rect(screen, timer_color, timer_fill, border_radius=5)

        self.input_box.render(screen)

        pygame.draw.rect(screen, (45, 140, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (215, 225, 220), self.submit_btn, width=2, border_radius=6)
        btn_txt = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_txt, (self.submit_btn.centerx - btn_txt.get_width() // 2, self.submit_btn.centery - btn_txt.get_height() // 2))

        msg_surf = self.font_hud.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 295))