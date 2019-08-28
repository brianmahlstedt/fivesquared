#!/usr/bin/env python3
"""
This program is divided into two parts. The first ignores the symbols
and treats the pieces as blank shapes. It finds all permutations of the
valid placements of these pieces, then once it has that
significantly-smaller dataset, it brute forces the actual symbol
placement of the pieces into those constraints. It does both segments
recursively.
"""
from copy import deepcopy
from pprint import pprint


class BoardFullError(Exception):
    def __init__(self):
        super().__init__('The board is full.')


class CellFullError(Exception):
    def __init__(self):
        super().__init__('A piece is already taking that spot.')


class OffBoardError(Exception):
    def __init__(self):
        super().__init__('That location is off the board.')


class PieceSizeError(Exception):
    def __init__(self):
        super().__init__('Piece must be same size as slot.')


def find_new_anchor(grid):
    """Finds the most upper-left cell in the current grid.

    Args:
        grid (list of lists): current board

    Returns:
        (tuple of 2 ints): anchor indexed from 1

    Raises:
        BoardFullError if board is full
    """
    (x, y) = (0, 0)
    for row, cols in enumerate(grid):
        if 0 in cols:
             y = cols.index(0) + 1
             x = row + 1
             break
    if x == 0 and y == 0:
        raise BoardFullError
    return (x, y)


def find_slots_from_layout(layout):
    """Converts a filled matrix of rows and columns with placed shapes
    into slots.

    Args:
        layout (list of lists): inner lists are col entries, outers are rows

    Returns:
        (list of lists of tuples): ordered list of coords for placed pieces
    """
    slots = [[] for i in range(9)]
    for row_index, row in enumerate(layout):
        for col_index, ident in enumerate(row):
            slots[ident-1].append((row_index+1, col_index+1))
    return slots


def extract_symbols(lst):
    """Takes a row or column of idents or alphanumeric symbols and just
    extracts the symbols (letters).

    Args:
        lst (list): list of strings representing the cells in a row or col
            e.g. ['1a', '1b', '1c', 2, 2]

    Returns:
        (list): just the letters from the input
            e.g. ['a', 'b', 'c']
    """
    return [char
            for item in lst if isinstance(item, str)
            for char in item if not char.isdigit()]


def check_grid(grid):
    """Determines if any rows or columns violate the sudoku condition.
    This checks for strings (letters) in the layout, because those
    represent the symbols. A grid with just numbers is valid because
    those integers represent shape placement, not symbols, so it can't be
    falsy.

    Args:
        grid (list of lists): current board

    Returns:
        bool = False if the grid violates, True if currently valid
    """
    for row in grid:
        row_symbols = extract_symbols(row)
        if len(row_symbols) != len(set(row_symbols)):
            return False
    for col_index in range(5):
        col = [row[col_index] for row in grid]
        col_symbols = extract_symbols(col)
        if len(col_symbols) != len(set(col_symbols)):
            return False
    return True


def place_shape(grid, anchor, size, angle, ident):
    """Places a shape. This does not do any logical analysis, it is
    simply told to place a shape. It does not include any information about
    symbols, just shapes (1, 1, 1, 2, 2...).

    Args:
        grid (list of lists): current board
        anchor (tuple of 2 ints): indexed from 1
        size (int): 2 or 3
        angle (str): horizontal or vertical
        ident (int): identifier for piece

    Returns:
        (list of lists): grid with numbers identifying which shape is where

    Raises:
        CellFullError if placement is on top of another shape
        OffBoardError if placement is off the board
    """
    row_anchor = anchor[0] - 1
    col_anchor = anchor[1] - 1
    new_grid = deepcopy(grid)
    if angle == 'horizontal':
        cells = [(row_anchor, col_anchor + shift) for shift in range(size)]
    else:
        cells = [(row_anchor + shift, col_anchor) for shift in range(size)]
    for row, col in cells:
        try:
            val = new_grid[row][col]
        except IndexError:
            raise OffBoardError
        if val != 0:
            raise CellFullError
        new_grid[row][col] = ident
    return new_grid


def try_shape(grid, ident, remaining_shapes):
    """The recursive target. Walks down the placement of each shape,
    checking validity and appending to a global array for acceptable
    grid layouts. It does not consider directionality, since there
    aren't that many. We can deduplicate during the symbol solution part.

    Here is the entire state space, and order, of that recursion:
    -> piece: 1, 2, 3, 4, 5, 6, 7, 8, 9
      -> anchor: upperest leftest
        -> size: 3, 2
          -> angle: horizontal, vertical

    Args:
        grid (list of lists): current board
        ident (int): identifier for piece
        remaining_shapes (dict with keys 3 and 2): the number of
            remaining shapes for each type, 3x1 and 2x1
    """
    global grids
    anchor = find_new_anchor(grid)
    sizes = []
    if remaining_shapes[3] != 0:
        sizes.append(3)
    if remaining_shapes[2] != 0:
        sizes.append(2)
    for size in sizes:
        for angle in ['horizontal', 'vertical']:
            try:
                new_grid = place_shape(grid, anchor, size, angle, ident)
                if ident == 9:
                    grids.append(new_grid)
                new_remaining_shapes = remaining_shapes.copy()
                new_remaining_shapes[size] -= 1
                try_shape(new_grid, ident + 1, new_remaining_shapes)
            except (BoardFullError, CellFullError, OffBoardError):
                continue


def place_piece(layout, slot, piece, orientation):
    """Places a piece. This does not do any logical analysis, it is
    simply told to place a piece. It includes symbol information
    (1a, 1c, 1d, 2e, 2b...) where the numbers match the same piece, and
    the letters indicate the symbol there. We don't need anchoring behavior
    here because the provided slot is already known. If a piece is flipped,
    it simply reverses the order of the provided piece tuple.

    Args:
        layout (list of lists): current board - a placed symbol has a string
            for its cell because its an alphanumeric, whereas a cell without a
            symbol is still an int for the shape ident
            e.g. [['1e', '1c', '1d', 2, 2], [...], [...], [...], [...]]
        slot (list of tuples): list of coordinates for each cell in piece slot
            e.g. [(1, 1), (1, 2), (1, 3)]
        piece (tuple of strings): letters denote symbols
            e.g. ('a', 'b', 'c')
        orientation (string): normal or flipped

    Returns:
        (list of lists): grid with numbers and symbols identifying which
            piece and which symbols are where

    Raises:
        CellFullError if placement is on top of another piece (this should
            never happen here)
        PieceSizeError if the piece and slot size don't match 3-3 or 2-2
    """
    if len(slot) != len(piece):
        raise PieceSizeError
    new_layout = deepcopy(layout)
    piece = reversed(piece) if orientation == 'flipped' else piece
    for cell_coords, symbol in zip(slot, piece):
        row_index = cell_coords[0] - 1
        col_index = cell_coords[1] - 1
        cell_contents = new_layout[row_index][col_index]
        # This error should never happen, and we don't catch it. It's not part
        # of the recursion error handling like the first part. When given a slot,
        # it should be valid already.
        if isinstance(cell_contents, str):
            raise CellFullError
        new_layout[row_index][col_index] = str(cell_contents) + symbol
    return new_layout


def try_piece(layout, remaining_slots, remaining_pieces):
    """The recursive target. Walks down the placement of each piece,
    checking validity and appending to a global array for acceptable
    solutions.

    We don't need any anchoring behavior here, we effectively have
    9 lists to match with 9 lists.

    We don't deduplicate on rotational equivalents here.

    There is a fail-fast mechanism that checks the grid for validity
    after every piece placement. This keeps the deep recursive stack
    from getting out of hand. It is much faster than finding every
    permutation and the validating in post-process (and my laptop
    cannot do the latter). There is a second fail-fast mechanism when
    a 3x1 piece tries to go in a size 2 slot, and vice versa.

    There's no intentional try/except error handling flow for LOCATION
    here, because the slots are already determined as valid from part 1.

    Here is the entire state space, and order, of that recursion:
    -> slot: 1, 2, 3, 4, 5, 6, 7, 8, 9
      -> piece: 1, 2, 3, 4, 5, 6, 7, 8, 9
        -> orientation: normal, flipped

    Args:
        layout (list of lists): current board - a placed symbol has a string
            for its cell because its an alphanumeric, whereas a cell without a
            symbol is still an int for the shape ident
            e.g. [['1e', '1c', '1d', 2, 2], [...], [...], [...], [...]]
        remaining_slots (list of lists of tuples): ordered list of
            coordinates for the cells of piece layouts.
        remaining_pieces (list of tuples): symbol-containing definitions
            for the unplaced pieces.
    """
    global filled_grids
    for piece in remaining_pieces:
        for orientation in ['normal', 'flipped']:
            try:
                new_layout = place_piece(layout,
                                         remaining_slots[0],
                                         piece,
                                         orientation)
                if not check_grid(new_layout):
                    continue  # fail fast on invalidity
                new_remaining_slots = deepcopy(remaining_slots)
                new_remaining_slots.pop(0)
                new_remaining_pieces = deepcopy(remaining_pieces)
                new_remaining_pieces.remove(piece)
                if len(new_remaining_pieces) == 0:
                    filled_grids.append(new_layout)
                else:
                    try_piece(new_layout,
                              new_remaining_slots,
                              new_remaining_pieces)
            except PieceSizeError:
                continue  # fail fast on wrong piece size


def main():
    """Globals are used to store recursive permutations because we're not
    filtering down to a single return like a reduce() function, we're
    walking every path and storing them all.
    """
    # Part 1, find the shape slots
    global grids; grids = []
    initial_conditions = {
        'grid': [[0 for x in range(5)] for y in range(5)],
        'ident': 1,
        'remaining_shapes': {3: 7, 2: 2},
    }
    try_shape(**initial_conditions)
    # We now have a `grids` var of len 164.

    # Part 2, place the symbol pieces
    #     s = six pointed star
    #     f = five pointed star
    #     w = whirlwind
    #     t = triangle
    #     c = circle
    global filled_grids; filled_grids = []
    pieces = [
        ('s', 'f', 'w'),
        ('s', 'w', 'c'),
        ('s', 'c', 't'),
        ('f', 's', 'w'),
        ('f', 't', 'w'),
        ('w', 'f', 'c'),
        ('t', 'f', 'c'),
        ('s', 't'),
        ('t', 'c'),
    ]
    for layout in grids:
        slots = find_slots_from_layout(layout)
        initial_conditions = {
            'layout': layout,
            'remaining_slots': slots,
            'remaining_pieces': pieces,
        }
        try_piece(**initial_conditions)
    # We now have a `filled_grids` var of len 32.

    # You could deduplicate the rotations/mirrors programmatically,
    # but 32 is small enough to do by hand.
    for index, solution in enumerate(filled_grids):
        print(index + 1)
        pprint(solution)


if __name__ == '__main__':
        main()
