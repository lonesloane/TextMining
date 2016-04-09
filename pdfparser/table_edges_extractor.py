
X0, Y0, X1, Y1 = 0, 1, 2, 3
MAX_RECURSION = 100  # To avoid infinite recursion...should never require that many steps!!!
ADJ_DISTANCE = 1.0  # TODO: come up with better way to define a reasonable "adjacence" limit


def adjacent(pt1, pt2):
    if abs(pt1 - pt2) < ADJ_DISTANCE:
        return True
    return False


def same_cell(cell, neighbor_cell):
    if cell[X0] != neighbor_cell[X0]:
        return False
    if cell[X1] != neighbor_cell[X1]:
        return False
    if cell[Y0] != neighbor_cell[Y0]:
        return False
    if cell[Y1] != neighbor_cell[Y1]:
        return False
    return True


def find_outer_edges(cells, nth_recursion=0):
    nth_recursion += 1
    print '{n}th recursion step'.format(n=nth_recursion)
    if nth_recursion > MAX_RECURSION:
        return cells
    print 'Initial nb cells found: {ntables}'.format(ntables=len(cells))

    converged = True
    neighbor_cells = cells
    collapsed_cells = list()
    ignored_cells = list()

    for cell in cells:
        print 'Trying to collapse cell: {cell}'.format(cell=cell)
        collapsed = False
        if cell in ignored_cells:
            continue

        for neighbor_cell in neighbor_cells:
            if neighbor_cell in ignored_cells or same_cell(cell, neighbor_cell):
                continue

            print 'neighbor cell {neighbor_cell}'.format(neighbor_cell=neighbor_cell)

            # Collapse adjacent cell on West side
            if not collapsed and (adjacent(cell[X0], neighbor_cell[X1])) and \
                    (adjacent(neighbor_cell[Y0], cell[Y0]) or adjacent(neighbor_cell[Y1], cell[Y1])):
                print '[W] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                bottom = min(cell[Y0], neighbor_cell[Y0])
                top = max(cell[Y1], neighbor_cell[Y1])
                collapsed_cell = [neighbor_cell[X0], bottom, cell[X1], top]
                print '[W] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on East side
            if not collapsed and (adjacent(neighbor_cell[X0], cell[X1])) and \
                    (adjacent(neighbor_cell[Y0], cell[Y0]) or adjacent(neighbor_cell[Y1], cell[Y1])):
                print '[E] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                bottom = min(cell[Y0], neighbor_cell[Y0])
                top = max(cell[Y1], neighbor_cell[Y1])
                collapsed_cell = [cell[X0], bottom, neighbor_cell[X1], top]
                print '[E] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on South side
            if not collapsed and (adjacent(cell[Y0], neighbor_cell[Y1])) and \
                    (adjacent(neighbor_cell[X0], cell[X0]) or adjacent(neighbor_cell[X1], cell[X1])):
                print '[S] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                left = min(cell[X0], neighbor_cell[X0])
                right = max(cell[X1], neighbor_cell[X1])
                collapsed_cell = [left, neighbor_cell[Y0], right, cell[Y1]]
                print '[S] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse adjacent cell on North side
            if not collapsed and (adjacent(neighbor_cell[Y0], cell[Y1])) and \
                    (adjacent(neighbor_cell[X0], cell[X0]) or adjacent(neighbor_cell[X1], cell[X1])):
                print '[N] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                left = min(cell[X0], neighbor_cell[X0])
                right = max(cell[X1], neighbor_cell[X1])
                collapsed_cell = [left, cell[Y0], right, neighbor_cell[Y1]]
                print '[N] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse inner cell
            if not collapsed and (cell[X0] <= neighbor_cell[X0] <= neighbor_cell[X1] <= cell[X1]) and \
                    (cell[Y0] <= neighbor_cell[Y0] <= neighbor_cell[Y1] <= cell[Y1]):
                print '[INNER] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                   neighbor_cell=neighbor_cell)
                print '[INNER] resulting cell {cell}'.format(cell=cell)
                collapsed_cells.append(cell)
                collapsed = True

            # Collapse outer cell
            if not collapsed and (neighbor_cell[X0] <= cell[X0] <= cell[X1] <= neighbor_cell[X1]) and \
                    (neighbor_cell[Y0] <= cell[Y0] <= cell[Y1] <= neighbor_cell[Y1]):
                print '[OUTER] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell,
                                                                                   neighbor_cell=neighbor_cell)
                print '[OUTER] resulting cell {cell}'.format(cell=neighbor_cell)
                collapsed_cells.append(neighbor_cell)
                collapsed = True

            # Collapse overlapping cell on the right
            if not collapsed and (neighbor_cell[X0] <= cell[X1] and
                                  (cell[Y0] <= neighbor_cell[Y0] <= cell[Y1] or
                                   cell[Y0] <= neighbor_cell[Y1] <= cell[Y1])):
                print '[OE] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                left = min(cell[X0], neighbor_cell[X0])
                right = max(cell[X1], neighbor_cell[X1])
                top = max(cell[Y1], neighbor_cell[Y1])
                bottom = min(cell[Y0], neighbor_cell[Y0])
                collapsed_cell = [left, bottom, right, top]
                print '[OE] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            # Collapse overlapping cell on the left
            if not collapsed and (neighbor_cell[X1] >= cell[X0] and
                                  (cell[Y0] <= neighbor_cell[Y0] <= cell[Y1] or
                                   cell[Y0] <= neighbor_cell[Y1] <= cell[Y1])):
                print '[OW] collapsing cells {cell} and {neighbor_cell}'.format(cell=cell, neighbor_cell=neighbor_cell)
                left = min(cell[X0], neighbor_cell[X0])
                right = max(cell[X1], neighbor_cell[X1])
                top = max(cell[Y1], neighbor_cell[Y1])
                bottom = min(cell[Y0], neighbor_cell[Y0])
                collapsed_cell = [left, bottom, right, top]
                print '[OW] resulting cell {cell}'.format(cell=collapsed_cell)
                collapsed_cells.append(collapsed_cell)
                collapsed = True

            if collapsed:
                ignored_cells.append(cell)
                ignored_cells.append(neighbor_cell)
                converged = False
                break

        if not collapsed:
            print 'Failed to collapse cell: {cell}. Must be "alone"...'.format(cell=cell)
            collapsed_cells.append(cell)

    if converged:
        print 'Converged. All cells collapsed....'
        return collapsed_cells
    else:
        print 'Final nb cells found: {ntables}'.format(ntables=len(collapsed_cells))
        for cell in collapsed_cells:
            print cell
        # Not converged yet, make a recursive call to ourselves with cells collapsed so far.
        return find_outer_edges(collapsed_cells, nth_recursion=nth_recursion)


if __name__ == '__main__':
    pass
