import random
import pygame
from game.text_box import TextBox


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = [
            "MOON",
            "GOLD",
            "INDIA",
            "ROCK",
            "FORM",
            "WEEK"
        ]

        self.secret_word = ""
        self.scrambled_word = ""

        # -----------------------------
        # Hint system
        # -----------------------------

        self.hint_positions = []
        self.hint_penalty = 0

        # Positions fixed by hints
        self.locked_positions = set()

        # -----------------------------
        # Timer
        # -----------------------------

        self.round_time = 30
        self.time_left = 30
        self.round_start_time = pygame.time.get_ticks()

        self.time_up = False
        self.time_up_time = 0

        # -----------------------------
        # Interactive letter tiles
        # -----------------------------

        self.letter_tiles = []
        self.tile_rects = []

        self.selected_tile = None
        self.dragging_tile = None
        self.drag_pos = None

        # -----------------------------
        # Score
        # -----------------------------

        self.score = 0.0

        # -----------------------------
        # Feedback
        # -----------------------------

        self.feedback_msg = (
            "Unscramble the letters above!"
        )

        self.feedback_color = (
            210,
            215,
            225
        )

        # -----------------------------
        # Text box
        # -----------------------------

        self.input_box = TextBox(
            width // 2 - 130,
            210,
            160,
            46
        )

        # -----------------------------
        # Buttons
        # -----------------------------

        self.submit_btn = pygame.Rect(
            width // 2 - 105,
            310,
            95,
            46
        )

        self.hint_btn = pygame.Rect(
            width // 2 + 10,
            310,
            80,
            46
        )

        # -----------------------------
        # Fonts
        # -----------------------------

        self.font_title = pygame.font.SysFont(
            None,
            40
        )

        self.font_word = pygame.font.SysFont(
            None,
            52
        )

        self.font_msg = pygame.font.SysFont(
            None,
            26
        )

        self.font_btn = pygame.font.SysFont(
            None,
            24
        )

        self.font_instruction = pygame.font.SysFont(
            None,
            18
        )

        # Start first round
        self.next_round()

    # =========================================================
    # SCRAMBLE WORD
    # =========================================================

    def scramble_string(self, word):
        letters = list(word)

        while True:
            random.shuffle(letters)

            shuffled = "".join(letters)

            if shuffled != word or len(word) <= 1:
                return shuffled

    # =========================================================
    # NEXT ROUND
    # =========================================================

    def next_round(self):
        self.secret_word = random.choice(
            self.words
        )

        self.scrambled_word = self.scramble_string(
            self.secret_word
        )

        # Reset input
        self.input_box.clear()

        # Reset hints
        self.hint_positions = []
        self.hint_penalty = 0
        self.locked_positions = set()

        # Reset timer
        self.time_left = self.round_time
        self.round_start_time = pygame.time.get_ticks()

        self.time_up = False
        self.time_up_time = 0

        # Reset tiles
        self.letter_tiles = list(
            self.scrambled_word
        )

        self.tile_rects = []

        self.selected_tile = None
        self.dragging_tile = None
        self.drag_pos = None

        # Reset feedback
        self.feedback_msg = (
            "Unscramble the letters above!"
        )

        self.feedback_color = (
            210,
            215,
            225
        )

    # =========================================================
    # HINT
    # =========================================================

    def use_hint(self):
        if self.time_up:
            return

        # Find the first position that is not fixed
        for target_pos in range(
            len(self.secret_word)
        ):

            if target_pos in self.locked_positions:
                continue

            correct_letter = (
                self.secret_word[target_pos]
            )

            source_pos = None

            # Find the correct letter among
            # the tiles that are not locked
            for i, letter in enumerate(
                self.letter_tiles
            ):

                if i in self.locked_positions:
                    continue

                if letter == correct_letter:
                    source_pos = i
                    break

            if source_pos is not None:

                # If the correct letter is already
                # in the correct position
                if source_pos != target_pos:

                    (
                        self.letter_tiles[target_pos],
                        self.letter_tiles[source_pos]
                    ) = (
                        self.letter_tiles[source_pos],
                        self.letter_tiles[target_pos]
                    )

                # Lock this position
                self.locked_positions.add(
                    target_pos
                )

                self.hint_positions.append(
                    target_pos
                )

                self.hint_penalty += 1

                self.feedback_msg = (
                    f"Hint used! Position "
                    f"{target_pos + 1} fixed."
                )

                self.feedback_color = (
                    100,
                    200,
                    255
                )

                return

        self.feedback_msg = (
            "All letters are already fixed!"
        )

        self.feedback_color = (
            240,
            170,
            50
        )

    # =========================================================
    # SUBMIT GUESS
    # =========================================================

    def submit_guess(self):
        if self.time_up:
            return

        # Build the guess from the actual tiles
        guess = "".join(
            self.letter_tiles
        )

        # -----------------------------
        # Correct answer
        # -----------------------------

        if guess == self.secret_word:

            # Maximum = 4 points
            #
            # Every hint deducts:
            # 4 / number of letters
            #
            # Example:
            # 4-letter word
            # 1 hint = 1 point deduction
            #
            # 8-letter word
            # 1 hint = 0.5 point deduction

            penalty_per_hint = (
                4 / len(self.secret_word)
            )

            points_earned = max(
                0,
                4 - (
                    self.hint_penalty
                    * penalty_per_hint
                )
            )

            self.score += points_earned

            # Remove unnecessary decimal
            # for whole numbers
            if points_earned.is_integer():
                points_text = str(
                    int(points_earned)
                )
            else:
                points_text = f"{points_earned:.2f}"

            self.feedback_msg = (
                f"CORRECT! +{points_text} points."
            )

            self.feedback_color = (
                80,
                230,
                110
            )

            self.time_up = True
            self.time_up_time = pygame.time.get_ticks()

        # -----------------------------
        # Wrong answer
        # -----------------------------

        else:

            self.feedback_msg = (
                "WRONG GUESS! Try again."
            )

            self.feedback_color = (
                240,
                80,
                80
            )

    # =========================================================
    # HANDLE EVENTS
    # =========================================================

    def handle_event(self, event):

        if self.time_up:
            return

        # -----------------------------
        # Mouse button down
        # -----------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                # Submit button
                if self.submit_btn.collidepoint(
                    event.pos
                ):
                    self.submit_guess()
                    return

                # Hint button
                if self.hint_btn.collidepoint(
                    event.pos
                ):
                    self.use_hint()
                    return

                # Check tiles
                for i, rect in enumerate(
                    self.tile_rects
                ):

                    if rect.collidepoint(
                        event.pos
                    ):

                        # Locked tile cannot move
                        if i in self.locked_positions:
                            return

                        self.selected_tile = i
                        self.dragging_tile = i
                        self.drag_pos = event.pos

                        return

        # -----------------------------
        # Mouse movement
        # -----------------------------

        elif event.type == pygame.MOUSEMOTION:

            if self.dragging_tile is not None:

                self.drag_pos = event.pos

        # -----------------------------
        # Mouse button release
        # -----------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if (
                event.button == 1
                and self.dragging_tile is not None
            ):

                dragged_tile = (
                    self.dragging_tile
                )

                target_tile = None

                # Find tile under mouse
                for i, rect in enumerate(
                    self.tile_rects
                ):

                    if rect.collidepoint(
                        event.pos
                    ):

                        target_tile = i
                        break

                # Swap tiles
                if (
                    target_tile is not None
                    and target_tile != dragged_tile
                    and target_tile not in self.locked_positions
                ):

                    (
                        self.letter_tiles[
                            dragged_tile
                        ],
                        self.letter_tiles[
                            target_tile
                        ]
                    ) = (
                        self.letter_tiles[
                            target_tile
                        ],
                        self.letter_tiles[
                            dragged_tile
                        ]
                    )

                    self.feedback_msg = (
                        "Letters rearranged. Keep going!"
                    )

                    self.feedback_color = (
                        210,
                        215,
                        225
                    )

                # Reset dragging
                self.dragging_tile = None
                self.drag_pos = None
                self.selected_tile = None

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):

        # If round has ended
        if self.time_up:

            if (
                pygame.time.get_ticks()
                - self.time_up_time
                >= 2000
            ):

                self.next_round()

            return

        # Calculate elapsed time
        elapsed = (
            pygame.time.get_ticks()
            - self.round_start_time
        ) / 1000

        # Update remaining time
        self.time_left = max(
            0,
            self.round_time - elapsed
        )

        # Time expired
        if self.time_left <= 0:

            self.time_left = 0

            self.time_up = True

            self.time_up_time = (
                pygame.time.get_ticks()
            )

            self.feedback_msg = (
                f"TIME UP! The word was "
                f"'{self.secret_word}'."
            )

            self.feedback_color = (
                255,
                100,
                80
            )

    # =========================================================
    # RENDER
    # =========================================================

    def render(self, screen):

        # Background
        screen.fill(
            (26, 30, 38)
        )

        # =====================================================
        # INSTRUCTIONS
        # =====================================================

        instruction1 = self.font_instruction.render(
            "Each correct submission earns 4 points.",
            True,
            (210, 215, 225)
        )

        instruction2 = self.font_instruction.render(
            "Each hint reduces the score based on word length.",
            True,
            (210, 215, 225)
        )

        instruction3 = self.font_instruction.render(
            "Example: 4-letter word + 1 hint = 3 points.",
            True,
            (210, 215, 225)
        )

        instruction4 = self.font_instruction.render(
            "All the best!",
            True,
            (255, 220, 80)
        )

        screen.blit(
            instruction1,
            (
                self.width // 2
                - instruction1.get_width() // 2,
                8
            )
        )

        screen.blit(
            instruction2,
            (
                self.width // 2
                - instruction2.get_width() // 2,
                28
            )
        )

        screen.blit(
            instruction3,
            (
                self.width // 2
                - instruction3.get_width() // 2,
                48
            )
        )

        screen.blit(
            instruction4,
            (
                self.width // 2
                - instruction4.get_width() // 2,
                68
            )
        )

        # =====================================================
        # TITLE
        # =====================================================

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
                90
            )
        )

        # =====================================================
        # SCORE
        # =====================================================

        if self.score.is_integer():
            score_text = f"Score: {int(self.score)}"
        else:
            score_text = f"Score: {self.score:.2f}"

        score_surf = self.font_msg.render(
            score_text,
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2
                - score_surf.get_width() // 2,
                135
            )
        )

        # =====================================================
        # TIMER
        # =====================================================

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
                170
            )
        )

        # =====================================================
        # TIMER PROGRESS BAR
        # =====================================================

        bar_width = 360
        bar_height = 14

        bar_x = (
            self.width // 2
            - bar_width // 2
        )

        bar_y = 200

        pygame.draw.rect(
            screen,
            (70, 70, 80),
            (
                bar_x,
                bar_y,
                bar_width,
                bar_height
            ),
            border_radius=7
        )

        progress = (
            self.time_left
            / self.round_time
        )

        progress_width = int(
            bar_width * progress
        )

        if progress_width > 0:

            if self.time_left <= 5:
                timer_color = (
                    240,
                    80,
                    80
                )
            else:
                timer_color = (
                    80,
                    200,
                    120
                )

            pygame.draw.rect(
                screen,
                timer_color,
                (
                    bar_x,
                    bar_y,
                    progress_width,
                    bar_height
                ),
                border_radius=7
            )

        # =====================================================
        # LETTER TILES
        # =====================================================

        tile_size = 55
        tile_gap = 8

        total_width = (
            len(self.letter_tiles)
            * tile_size
            + (
                len(self.letter_tiles) - 1
            )
            * tile_gap
        )

        start_x = (
            self.width // 2
            - total_width // 2
        )

        tile_y = 235

        self.tile_rects = []

        # Draw normal tiles
        for i, letter in enumerate(
            self.letter_tiles
        ):

            x = (
                start_x
                + i * (
                    tile_size
                    + tile_gap
                )
            )

            rect = pygame.Rect(
                x,
                tile_y,
                tile_size,
                tile_size
            )

            self.tile_rects.append(
                rect
            )

            # Don't draw the original tile
            # while dragging it
            if self.dragging_tile == i:
                continue

            # -----------------------------
            # Locked tile
            # -----------------------------

            if i in self.locked_positions:

                tile_color = (
                    70,
                    160,
                    100
                )

                border_color = (
                    255,
                    255,
                    255
                )

                border_width = 3

            # -----------------------------
            # Selected tile
            # -----------------------------

            elif self.selected_tile == i:

                tile_color = (
                    255,
                    180,
                    60
                )

                border_color = (
                    255,
                    255,
                    255
                )

                border_width = 4

            # -----------------------------
            # Normal tile
            # -----------------------------

            else:

                tile_color = (
                    60,
                    100,
                    160
                )

                border_color = (
                    220,
                    220,
                    220
                )

                border_width = 2

            pygame.draw.rect(
                screen,
                tile_color,
                rect,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                border_color,
                rect,
                width=border_width,
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

        # =====================================================
        # DRAGGED TILE
        # =====================================================

        if (
            self.dragging_tile is not None
            and self.drag_pos is not None
        ):

            letter = self.letter_tiles[
                self.dragging_tile
            ]

            drag_rect = pygame.Rect(
                0,
                0,
                tile_size,
                tile_size
            )

            drag_rect.center = (
                self.drag_pos
            )

            pygame.draw.rect(
                screen,
                (255, 180, 60),
                drag_rect,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                drag_rect,
                width=3,
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
                    drag_rect.centerx
                    - letter_surf.get_width() // 2,
                    drag_rect.centery
                    - letter_surf.get_height() // 2
                )
            )

        # =====================================================
        # SUBMIT BUTTON
        # =====================================================

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

        # =====================================================
        # HINT BUTTON
        # =====================================================

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

        # =====================================================
        # FEEDBACK MESSAGE
        # =====================================================

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
                375
            )
        )
