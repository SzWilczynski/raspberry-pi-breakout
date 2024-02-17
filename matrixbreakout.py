import numpy as np
import matrixgame

PALLET_RADIUS = 1
PALLET_VELOCITY = 2
PALLET_STICK_TIME = 1
GAME_OVER_TIME = 3
BOARD_SIZE = 8
X = 0
Y = 1


class BreakoutGame(matrixgame.MatrixGameInterface):
    ball_pos = (0, 0)
    ball_vel = (0, 0)
    blocks = []
    pallet_center_pos = 0
    pallet_stick_timer = 0
    game_over_timer = 0

    def __init__(self):
        self.pallet_stick_timer = 0
        self.game_over_timer = 0
        self.blocks = []
        for x in range(BOARD_SIZE//2):
            for y in range(BOARD_SIZE//4):
                self.blocks.append((x, (BOARD_SIZE//2)-1-y))
        self.pallet_center_pos = BOARD_SIZE//2
        self.ball_pos = (BOARD_SIZE//2, 1)
        self.ball_vel = (1, 1)

    def __find_block_at_pos(self, pos):
        pos = (pos[X]//2, pos[Y]//2)
        for index, block in enumerate(self.blocks):
            if block == pos:
                return index
        return None

    @staticmethod
    def __add_coord_tuples(first, second):
        return np.add(np.array(first), np.array(second))

    def __update_ball(self):
        # game area bounds collision
        if (self.ball_pos[X] == 0 and self.ball_vel[X] == -1) or (self.ball_pos[X] == BOARD_SIZE-1 and self.ball_vel[X] == 1):
            self.ball_vel = (-self.ball_vel[X], self.ball_vel[Y])
        if self.ball_pos[Y] == BOARD_SIZE-1 and self.ball_vel[Y] == 1:
            self.ball_vel = (self.ball_vel[X], -self.ball_vel[Y])
        if self.ball_pos[Y] == 0:
            self.game_over_timer = GAME_OVER_TIME
            return

        # blocks collision
        hit_a_block = False
        block = self.__find_block_at_pos(self.__add_coord_tuples(self.ball_pos, (self.ball_vel[X], 0)))
        if block is not None:
            self.blocks.pop(block)
            self.ball_vel = (-self.ball_vel[X], self.ball_vel[Y])
            hit_a_block = True
        block = self.__find_block_at_pos(self.__add_coord_tuples(self.ball_pos, (0, self.ball_vel[Y])))
        if block is not None:
            self.blocks.pop(block)
            self.ball_vel = (self.ball_vel[X], -self.ball_vel[Y])
            hit_a_block = True
        if not hit_a_block:
            block = self.__find_block_at_pos(self.__add_coord_tuples(self.ball_pos, (self.ball_vel[X], self.ball_vel[Y])))
            if block is not None:
                self.blocks.pop(block)
                self.ball_vel = (-self.ball_vel[X], -self.ball_vel[Y])
                hit_a_block = True
        if hit_a_block and len(self.blocks) == 0:
            self.game_over_timer = GAME_OVER_TIME
            return

        self.ball_pos = self.__add_coord_tuples(self.ball_pos, self.ball_vel)

        # bottom/palette collision
        if self.ball_pos[Y] == 1:
            if abs(self.ball_pos[X]-self.pallet_center_pos) <= PALLET_RADIUS:
                self.ball_pos = (self.ball_pos[X], 1)
                self.ball_vel = (self.ball_vel[X], 1)
                self.pallet_stick_timer = PALLET_STICK_TIME

    def update(self, inputs):
        # skip updates if game ended, restart shortly after
        if self.game_over_timer > 0:
            self.game_over_timer -= 1
            if self.game_over_timer == 0:
                self.__init__()
            return

        (left_input, right_input) = inputs
        if left_input:
            self.pallet_center_pos = max(PALLET_RADIUS, self.pallet_center_pos-PALLET_VELOCITY)
            if self.pallet_stick_timer > 0:
                self.ball_pos = (max(0, self.ball_pos[X]-PALLET_VELOCITY), 1)
                self.ball_vel = (-1, 1)
        elif right_input:
            self.pallet_center_pos = min(BOARD_SIZE-PALLET_RADIUS-1, self.pallet_center_pos+PALLET_VELOCITY)
            if self.pallet_stick_timer > 0:
                self.ball_pos = (min(BOARD_SIZE-1, self.ball_pos[X]+PALLET_VELOCITY), 1)
                self.ball_vel = (1, 1)

        if self.pallet_stick_timer > 0:
            self.pallet_stick_timer -= 1
        else:
            self.__update_ball()

    def board_matrix(self):
        board = np.zeros(BOARD_SIZE, np.byte)
        board[self.ball_pos[Y]] |= 1 << self.ball_pos[X]

        pallet_horizontal = 0
        for i in range(2*PALLET_RADIUS+1):
            pallet_horizontal = pallet_horizontal << 1
            pallet_horizontal |= 1
        pallet_offset = self.pallet_center_pos - PALLET_RADIUS
        board[0] |= pallet_horizontal << pallet_offset

        for block in self.blocks:
            block_horizontal = 3 << block[X]*2
            board[block[Y]*2] |= block_horizontal
            board[block[Y]*2+1] |= block_horizontal
        if self.game_over_timer % 2 == 1:
            board = np.invert(board)

        # rotate the board
        rotated = np.zeros(BOARD_SIZE, np.byte)
        for column in range(BOARD_SIZE):
            bit_pos = 1 << column
            for row in range(BOARD_SIZE):
                extracted_bit = (board[row] & bit_pos) >> column
                rotated[column] |= extracted_bit << BOARD_SIZE-1-row

        return rotated
