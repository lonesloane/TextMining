import logging

MAX_RECURSION = 100  # To avoid infinite recursion...should never require that many steps!!!
ADJ_DISTANCE = 1.0  # TODO: come up with better way to define a reasonable "adjacence" limit


class Cell:

    def __init__(self, x0, y0, x1, y1, rows=1, columns=1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.rows = rows
        self.columns = columns

    def __repr__(self):
        return '[' + 'x0: ' + str(self.x0) + ', y0: ' + str(self.y0) \
               + ', x1: ' + str(self.x1) + ', y1: ' + str(self.y1) + ']'


def adjacent(pt1, pt2):
    if abs(pt1 - pt2) < ADJ_DISTANCE:
        return True
    return False


def same_cell(cell, neighbor_cell):
    if cell.x0 != neighbor_cell.x0:
        return False
    if cell.x1 != neighbor_cell.x1:
        return False
    if cell.y0 != neighbor_cell.y0:
        return False
    if cell.y1 != neighbor_cell.y1:
        return False
    return True


def find_outer_edges(cells, nth_recursion=0):
    # logger = logging.getLogger('summarizer')
    logger = logging.getLogger(__name__)
    nth_recursion += 1
    logger.debug('{n}th recursion step'.format(n=nth_recursion))
    if nth_recursion > MAX_RECURSION:
        return cells
    logger.debug('Initial nb cells found: {ntables}'.format(ntables=len(cells)))

    converged = True
    neighbor_cells = cells[:]  # deep copy to ensure no side effects (really useful?)
    collapsed_cells = list()
    ignored_cells = list()

    for cell in cells:
        logger.debug('Trying to collapse cell: {cell}'.format(cell=cell))
        collapsed = False
        if cell in ignored_cells:
            continue

        for neighbor_cell in neighbor_cells:
            if neighbor_cell in ignored_cells or same_cell(cell, neighbor_cell):
                continue

            logger.debug('neighbor cell {neighbor_cell}'.format(neighbor_cell=neighbor_cell))

            # Collapse adjacent cell on West side
            if not collapsed and (adjacent(cell.x0, neighbor_cell.x1)) and \
                    (adjacent(neighbor_cell.y0, cell.y0) or adjacent(neighbor_cell.y1, cell.y1)):
                logger.debug('[W] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                      neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_west(cell, neighbor_cell)
                logger.debug('[W] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on East side
            if not collapsed and (adjacent(neighbor_cell.x0, cell.x1)) and \
                    (adjacent(neighbor_cell.y0, cell.y0) or adjacent(neighbor_cell.y1, cell.y1)):
                logger.debug('[E] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                      neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_east(cell, neighbor_cell)
                logger.debug('[E] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on South side
            if not collapsed and (adjacent(cell.y0, neighbor_cell.y1)) and \
                    (adjacent(neighbor_cell.x0, cell.x0) or adjacent(neighbor_cell.x1, cell.x1)):
                logger.debug('[S] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                      neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_south(cell, neighbor_cell)
                logger.debug('[S] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on North side
            if not collapsed and (adjacent(neighbor_cell.y0, cell.y1)) and \
                    (adjacent(neighbor_cell.x0, cell.x0) or adjacent(neighbor_cell.x1, cell.x1)):
                logger.debug('[N] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                      neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_north(cell, neighbor_cell)
                logger.debug('[N] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse inner cell
            if not collapsed and (cell.x0 <= neighbor_cell.x0 <= neighbor_cell.x1 <= cell.x1) and \
                    (cell.y0 <= neighbor_cell.y0 <= neighbor_cell.y1 <= cell.y1):
                logger.debug('[INNER] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                          neighbor_cell=neighbor_cell))
                logger.debug('[INNER] resulting cell {cell}'.format(cell=cell))
                cell.columns += neighbor_cell.columns
                cell.rows += neighbor_cell.rows
                collapsed_cells.append(cell)
                collapsed = True

            # Collapse outer cell
            if not collapsed and (neighbor_cell.x0 <= cell.x0 <= cell.x1 <= neighbor_cell.x1) and \
                    (neighbor_cell.y0 <= cell.y0 <= cell.y1 <= neighbor_cell.y1):
                logger.debug('[OUTER] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                          neighbor_cell=neighbor_cell))
                logger.debug('[OUTER] resulting cell {cell}'.format(cell=neighbor_cell))
                neighbor_cell.columns += cell.columns
                neighbor_cell.rows += cell.rows
                collapsed_cells.append(neighbor_cell)
                collapsed = True

            # Collapse overlapping cell on the right
            if not collapsed and (neighbor_cell.x0 <= cell.x1 and
                                  (cell.y0 <= neighbor_cell.y0 <= cell.y1 or
                                   cell.y0 <= neighbor_cell.y1 <= cell.y1)):
                logger.debug('[OE] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                       neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_overlapping(cell, neighbor_cell)
                logger.debug('[OE] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse overlapping cell on the left
            if not collapsed and (neighbor_cell.x1 >= cell.x0 and
                                  (cell.y0 <= neighbor_cell.y0 <= cell.y1 or
                                   cell.y0 <= neighbor_cell.y1 <= cell.y1)):
                logger.debug('[OW] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                       neighbor_cell=neighbor_cell))
                collapsed_cell = collapse_overlapping(cell, neighbor_cell)
                logger.debug('[OW] resulting cell {cell}'.format(cell=collapsed_cell))
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            if collapsed:
                ignored_cells.append(cell)
                ignored_cells.append(neighbor_cell)
                converged = False
                break

        if not collapsed:
            logger.debug('Failed to collapse cell: {cell}. Must be "alone"...'.format(cell=cell))
            collapsed_cells.append(cell)

    if converged:
        logger.debug('Converged. All cells collapsed....')
        return collapsed_cells
    else:
        logger.debug('Final nb cells found: {ntables}'.format(ntables=len(collapsed_cells)))
        for cell in collapsed_cells:
            logger.debug(cell)
        # Not converged yet, make a recursive call to ourselves with cells collapsed so far.
        return find_outer_edges(collapsed_cells, nth_recursion=nth_recursion)


def collapse_overlapping(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    top = max(cell.y1, neighbor_cell.y1)
    bottom = min(cell.y0, neighbor_cell.y0)
    rows = cell.rows + neighbor_cell.rows
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(left, bottom, right, top, rows=rows, columns=columns)
    return collapsed_cell


def collapse_north(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    rows = cell.rows + neighbor_cell.rows
    columns = max(cell.columns, neighbor_cell.columns)
    collapsed_cell = Cell(left, cell.y0, right, neighbor_cell.y1, rows=rows, columns=columns)
    return collapsed_cell


def collapse_south(cell, neighbor_cell):
    left = min(cell.x0, neighbor_cell.x0)
    right = max(cell.x1, neighbor_cell.x1)
    rows = cell.rows + neighbor_cell.rows
    columns = max(cell.columns, neighbor_cell.columns)
    collapsed_cell = Cell(left, neighbor_cell.y0, right, cell.y1, rows=rows, columns=columns)
    return collapsed_cell


def collapse_east(cell, neighbor_cell):
    bottom = min(cell.y0, neighbor_cell.y0)
    top = max(cell.y1, neighbor_cell.y1)
    rows = max(cell.rows, neighbor_cell.rows)
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(cell.x0, bottom, neighbor_cell.x1, top, rows=rows, columns=columns)
    return collapsed_cell


def collapse_west(cell, neighbor_cell):
    bottom = min(cell.y0, neighbor_cell.y0)
    top = max(cell.y1, neighbor_cell.y1)
    rows = max(cell.rows, neighbor_cell.rows)
    columns = cell.columns + neighbor_cell.columns
    collapsed_cell = Cell(neighbor_cell.x0, bottom, cell.x1, top, rows=rows, columns=columns)
    return collapsed_cell


def logging_setup():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    _logger = logging.getLogger('summarizer')
    # create file handler which logs even debug messages
    fh = logging.FileHandler('summarizer.log', mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)

    return _logger


if __name__ == '__main__':
    logger = logging_setup()
