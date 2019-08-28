"""A programmatic solution to fivesquared, a puzzle from Israel.

www.thinkingames.com

First, this program ignores the symbols and treats the pieces as blank shapes.
It finds all permutations of the valid placements of these pieces, then once
it has that significantly-smaller dataset, it brute forces the actual symbol
placement of the pieces into those constraints.

Here is the entire state space, and order, of that iteration:

-> piece: 1,2,3,4,5,6,7,8,9
  -> anchor: upperest leftest
    -> size: 3, 2
      -> angle: horizontal, vertical

The second part uses iteration as well (not recursion). Blah blah FILL THIS IN
"""
from copy import deepcopy
from pprint import pprint


def place_piece(grid, anchor, size, angle, ident):
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

    print('placed piece {} size {} in {} position starting at {}'
            .format(ident, size, angle, anchor))
    pprint(new_grid)
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


def try_piece(grid, ident):
    """This is the logical analysis wrapper around place_piece,
    deciding what is valid (via exception) and trying permutations.

    Args:
        grid (list of lists): current board
        ident (int): identifier for piece

    Returns:
        (list of lists): grid
    """
    anchor = find_new_anchor(grid)
    for size in [3, 2]:
        for angle in ['horizontal', 'vertical']:
            try:
                grid = place_piece(grid, anchor, size, angle, ident)
                return grid
            except (ValueError, IndexError):
                continue
    print('no pieces could be placed.')


def main():
    grid_size =5
    grid = [[0 for x in range(grid_size)] for y in range(grid_size)]
    for ident in [1,2,3,4,5,6,7,8,9]:
        grid = try_piece(grid, ident)
