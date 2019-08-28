"""
This program is divided into two parts. The first ignores the symbols
and treats the pieces as blank shapes. It finds all permutations of the
valid placements of these pieces, then once it has that
significantly-smaller dataset, it brute forces the actual symbol
placement of the pieces into those constraints.

Here is the entire state space, and order, of that recursion:

-> piece: 1,2,3,4,5,6,7,8,9
  -> anchor: upperest leftest
    -> size: 3, 2
      -> angle: horizontal, vertical

The second part Blah blah FILL THIS IN
"""
from copy import deepcopy
from pprint import pprint


def place_shape(grid, anchor, size, angle, ident):
    """Places a piece. This does not do any logical analysis, it is
    simply told to place a piece.

    Args:
        grid (list of lists): current board
        anchor (tuple of 2 ints): indexed from 1
        size (int): 2 or 3
        angle (str): horizontal or vertical
        ident (int): identifier for piece

    Returns:
        (list of lists): grid

    Raises:
        ValueError if placement is on top of another piece
        IndexError if placement is off the board
    """
    row_anchor = anchor[0] - 1
    col_anchor = anchor[1] - 1
    new_grid = deepcopy(grid)
    if angle == 'horizontal':
        cells = [(row_anchor, col_anchor + shift) for shift in range(size)]
    else:
        cells = [(row_anchor + shift, col_anchor) for shift in range(size)]
    for row, col in cells:
        if new_grid[row][col] != 0:
            raise ValueError('a piece is already taking that spot')
        new_grid[row][col] = ident
    return new_grid


def find_new_anchor(grid):
    """Finds the most upper-left cell in the current grid.

    Args:
        grid (list of lists): current board

    Returns:
        (tuple of 2 ints): anchor indexed from 1

    Raises:
        ValueError if grid is full
    """
    (x, y) = (0, 0)
    for row, cols in enumerate(grid):
        if 0 in cols:
             y = cols.index(0) + 1
             x = row + 1
             break
    if x == 0 and y == 0:
        raise ValueError('grid is full')
    return (x, y)


def try_shape(grid, ident, remaining_pieces):
    """The recursive portion. Walks down the placement of each piece,
    checking validity and appending to a global array for acceptable
    grid fillings. It does not consider directionality, since there
    aren't that many. We can deduplicate during the symbol solution part.

    Args:
        grid (list of lists): current board
        ident (int): identifier for piece
        remainining_pieces (dict with keys 3 and 2): the number of
            remaining pieces for each type, 3x1 and 2x1.
    """
    global grids
    anchor = find_new_anchor(grid)
    sizes = []
    if remaining_pieces[3] != 0:
        sizes.append(3)
    if remaining_pieces[2] != 0:
        sizes.append(2)
    for size in sizes:
        for angle in ['horizontal', 'vertical']:
            try:
                new_grid = place_shape(grid, anchor, size, angle, ident)
                if ident == 9:
                    grids.append(new_grid)
                    pprint(new_grid)
                new_remainders = remaining_pieces.copy()
                new_remainders[size] -= 1
                try_shape(new_grid, ident + 1, new_remainders)
            except (ValueError, IndexError):
                continue


def main():
    global grids; grids = []
    initial_conditions = {
        'grid': [[0 for x in range(5)] for y in range(5)],
        'ident': 1,
        'remaining_pieces': {3: 7, 2: 2},
    }
    try_shape(**initial_conditions)



'''
There are 9 pieces, mapped numerically as follows:
* 1 = six pointed star
* 2 = five pointed star
* 3 = whirlwind
* 4 = triangle
* 5 = circle

0 means that the slot hasn't been filled yet.
'''
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
