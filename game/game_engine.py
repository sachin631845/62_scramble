import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = [
            "PYTHON",
            "PYGAME",
            "PLANET",
            "ROCKET",
            "GALAXY",
            "STREAM",
            "PUZZLE",
            "ALGORITHM"
        ]

        self.secret_word = ""
        self.scrambled_word = ""

        # Task 2: Hint system
        self.hint_positions = []
        self.hint_penalty = 0

        # Task 3: 30-second timer
        self.round_time = 30
        self.time_left = 30
        self.round_start_time = pygame.time.get_ticks()
        self.time_up = False
        self.time_up_time = 0

        # Task 4: Interactive letter tiles
        self.letter_tiles = []
        self.tile_rects = []
        self.selected_tile = None

        self.score = 0
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(
            width // 2 - 130,
            210,
            160,
            46
        )

        self.submit_btn = pygame.Rect(
            width // 2 + 45,
            250,
            95,
            46
        )

        self.hint_btn = pygame.Rect(
            width // 2 + 150,
            250,
            80,
            46
        )

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.next_round()

    def scramble_string(self, word):
        letters = list(word)

        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)

            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(
            self.secret_word
        )

        self.input_box.clear()

        # Reset hints
        self.hint_positions = []
        self.hint_penalty = 0

        # Reset timer
        self.time_left = self.round_time
        self.round_start_time = pygame.time.get_ticks()
        self.time_up = False
        self.time_up_time = 0

        # Reset tiles
        self.letter_tiles = list(self.scrambled_word)
        self.tile_rects = []
        self.selected_tile = None

    def use_hint(self):
        if self.time_up:
            return

        for i in range(len(self.secret_word)):
            if i not in self.hint_positions:
                self.hint_positions.append(i)
                self.hint_penalty += 1

                self.feedback_msg = (
                    f"Hint: letter {i + 1} revealed."
                )

                self.feedback_color = (100, 200, 255)
                return

        self.feedback_msg = (
            "All letters are already revealed!"
        )

        self.feedback_color = (240, 170, 50)

    def submit_guess(self):
        if self.time_up:
            return

        # Task 4:
        # The guess is the current order of the tiles
        guess = "".join(self.letter_tiles)

        # Task 1:
        # Compare against the actual secret word
        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += 1

            self.feedback_msg = (
                f"CORRECT! '{self.secret_word}' is right."
            )

            self.feedback_color = (80, 230, 110)

            self.next_round()

        else:
            self.feedback_msg = (
                "WRONG GUESS! Try again."
            )

            self.feedback_color = (240, 80, 80)

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if self.time_up:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                # Submit button
                if self.submit_btn.collidepoint(event.pos):
                    self.submit_guess()

                # Hint button
                elif self.hint_btn.collidepoint(event.pos):
                    self.use_hint()

                # Letter tiles
                else:
                    for i in range(len(self.letter_tiles)):

                        if (
                            i < len(self.tile_rects)
                            and self.tile_rects[i].collidepoint(
                                event.pos
                            )
                        ):

                            if self.selected_tile is None:

                                # Select first tile
                                self.selected_tile = i

                            else:

                                # Swap selected tile
                                # with clicked tile
                                selected = self.selected_tile

                                (
                                    self.letter_tiles[selected],
                                    self.letter_tiles[i]
                                ) = (
                                    self.letter_tiles[i],
                                    self.letter_tiles[selected]
                                )

                                self.selected_tile = None

                            break

    def update(self):
        if self.time_up:

            # Wait 1.5 seconds before next round
            if (
                pygame.time.get_ticks()
                - self.time_up_time
                >= 1500
            ):
                self.next_round()

            return

        # Calculate elapsed time
        elapsed = (
            pygame.time.get_ticks()
            - self.round_start_time
        ) / 1000

        self.time_left = max(
            0,
            self.round_time - elapsed
        )

        # Time has expired
        if self.time_left <= 0:

            self.time_left = 0
            self.time_up = True
            self.time_up_time = pygame.time.get_ticks()

            self.feedback_msg = (
                f"TIME UP! The word was "
                f"'{self.secret_word}'."
            )

            self.feedback_color = (255, 100, 80)

    def render(self, screen):
        screen.fill((26, 30, 38))

        # --------------------------------
        # Title
        # --------------------------------

        title_surf = self.font_title.render(
            "Word Scramble Arena",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                25
            )
        )

        # --------------------------------
        # Score
        # --------------------------------

        score_surf = self.font_msg.render(
            f"Score: {self.score}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2
                - score_surf.get_width() // 2,
                70
            )
        )

        # --------------------------------
        # Timer text
        # --------------------------------

        timer_surf = self.font_msg.render(
            f"Time: {self.time_left:.1f}s",
            True,
            (255, 255, 255)
        )

        screen.blit(
            timer_surf,
            (
                self.width // 2
                - timer_surf.get_width() // 2,
                100
            )
        )

        # --------------------------------
        # Timer bar
        # --------------------------------

        bar_width = 300
        bar_height = 12

        bar_x = (
            self.width // 2
            - bar_width // 2
        )

        bar_y = 125

        pygame.draw.rect(
            screen,
            (70, 70, 80),
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            ),
            border_radius=6
        )

        progress = (
            self.time_left
            / self.round_time
        )

        progress_width = int(
            bar_width * progress
        )

        if progress_width > 0:
            pygame.draw.rect(
                screen,
                (80, 200, 120),
                (
                    bar_x,
                    bar_y,
                    progress_width,
                    bar_height
                ),
                border_radius=6
            )

        # --------------------------------
        # Task 4: Letter tiles
        # --------------------------------

        tile_size = 55
        tile_gap = 8

        total_width = (
            len(self.letter_tiles)
            * tile_size
            + (
                len(self.letter_tiles) - 1
            ) * tile_gap
        )

        start_x = (
            self.width // 2
            - total_width // 2
        )

        tile_y = 155

        # Clear and rebuild tile rectangles
        self.tile_rects = []

        for i, letter in enumerate(
            self.letter_tiles
        ):

            x = start_x + i * (
                tile_size + tile_gap
            )

            rect = pygame.Rect(
                x,
                tile_y,
                tile_size,
                tile_size
            )

            self.tile_rects.append(rect)

            # Selected tile
            if self.selected_tile == i:
                tile_color = (255, 180, 60)
            else:
                tile_color = (60, 100, 160)

            pygame.draw.rect(
                screen,
                tile_color,
                rect,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                (220, 220, 220),
                rect,
                width=2,
                border_radius=8
            )

            letter_surf = self.font_word.render(
                letter,
                True,
                (255, 255, 255)
            )

            screen.blit(
                letter_surf,
                (
                    rect.centerx
                    - letter_surf.get_width() // 2,
                    rect.centery
                    - letter_surf.get_height() // 2
                )
            )

        # --------------------------------
        # Hint display
        # --------------------------------

        if (
            self.hint_positions
            and not self.time_up
        ):

            hint_display = ""

            for i, letter in enumerate(
                self.secret_word
            ):

                if i in self.hint_positions:
                    hint_display += letter + " "
                else:
                    hint_display += "_ "

            hint_surf = self.font_msg.render(
                "Hint: " + hint_display.strip(),
                True,
                (100, 200, 255)
            )

            screen.blit(
                hint_surf,
                (
                    self.width // 2
                    - hint_surf.get_width() // 2,
                    220
                )
            )

        # --------------------------------
        # Submit button
        # --------------------------------

        pygame.draw.rect(
            screen,
            (50, 150, 85),
            self.submit_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.submit_btn,
            width=2,
            border_radius=6
        )

        btn_text = self.font_btn.render(
            "SUBMIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            btn_text,
            (
                self.submit_btn.centerx
                - btn_text.get_width() // 2,
                self.submit_btn.centery
                - btn_text.get_height() // 2
            )
        )

        # --------------------------------
        # Hint button
        # --------------------------------

        pygame.draw.rect(
            screen,
            (70, 110, 180),
            self.hint_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.hint_btn,
            width=2,
            border_radius=6
        )

        hint_btn_text = self.font_btn.render(
            "HINT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            hint_btn_text,
            (
                self.hint_btn.centerx
                - hint_btn_text.get_width() // 2,
                self.hint_btn.centery
                - hint_btn_text.get_height() // 2
            )
        )

        # --------------------------------
        # Feedback
        # --------------------------------

        feedback_surf = self.font_msg.render(
            self.feedback_msg,
            True,
            self.feedback_color
        )

        screen.blit(
            feedback_surf,
            (
                self.width // 2
                - feedback_surf.get_width() // 2,
                285
            )
        )
