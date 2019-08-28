'''
00 01 02 03 04
05 06 07 08 09
10 11 12 13 14
15 16 17 18 19
20 21 22 23 24

Place one first. Place the next and so on. Recurse down, trying every configuration.

Every piece has 4 configurations. Horizontal, vertical, forward, backward.
Try them in this order:
* horizontal forward
* horizontal backward
* vertical forward
* vertical backward

Then move onto the next anchor position, following incremental order in the above grid. This
moves like a book, originating at the upper left then favoring right then down.

Vertical positioning is the same anchor for that piece, but then instead of +1 for each next
square, it's +5.

There are 9 pieces, mapped numerically as follows:
* 1 = six pointed star
* 2 = five pointed star
* 3 = whirlwind
* 4 = triangle
* 5 = circle

0 means that the slot hasn't been filled yet.

Fail fast if any configuration violates, ignoring the rest of the piece placement.
'''

initial_grid = 0*25

pieces = (
    (1, 2, 3),
    (5, 3, 1),
    (2, 4, 3),
    (4, 2, 5),
    (1, 5, 4),
    (5, 2, 3),
    (3, 1, 2),
    (4, 1),
    (4, 5),
)

angles = ['horizontal', 'vertical']
flips = [False, True]
orientations = itertools.product(angles, flips)


def check_grid(grid):
    """Given a 5x5 grid, returns a bool if any rows or columns violate (False = fail).
    Note that this does not check the FINAL grid, it simply checks that each placed
    piece did not violate the duplicate constraint in any row or column (therefore this
    should be called after every placement).

    Args:
        grid (list) = current 5x5 matrix

    Returns:
        bool = False if the grid violates, True if still good
    """
    rows = [grid[x:x+5] for x in range(5)]
    cols = [grid[x::5] for x in range(5)]
    for array in rows + cols:
        array = filter(lambda x: x != 0, array)
        if len(array) != len(set(array)):
            return False
    return True


def place_piece(grid, piece, origin, angle, flip):
    """
    Args:
        grid (list) = current 5x5 matrix
        piece (tuple) = piece to place
        angle (str) = 'horizontal' or 'vertical'
        flip (bool) = reversed numbers on piece if true
    """
    position = origin
    increment = 1 if angle == 'horizontal' else 5
    if flip is True:
        piece = piece[::-1]
    for number in piece:
        grid[position] = number
        position += increment
    return grid


def recurse_moves(grid):
    for piece in pieces:
        upperest_leftest = grid.index(0)
        for orientation in orientations:
            old_grid = grid
            new_grid = place_piece(grid, piece, upperest_leftest, *orientation)
            if check_grid(new_grid):
                # place next piece
            else:



def main():
    recurse_moves(initial_grid)
