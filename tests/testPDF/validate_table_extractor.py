import logging

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pdfparser.table_edges_extractor as extractor


def add_rect(x0, y0, x1, y1, color, fill=False):
    rec.add_patch(
        patches.Rectangle(
            (x0, y0),
            x1-x0,
            y1-y0,
            fill=fill,
            edgecolor=color
        )
    )


def load_cells(definition_file):
    _cells = list()
    rec_def = open(definition_file, 'r')
    _min_x = -1.0
    _min_y = -1.0
    _max_x = -1.0
    _max_y = -1.0
    for line in rec_def:
        x0, y0, x1, y1 = line.strip().split(',')
        _min_x, _min_y, _max_x, _max_y = store_cell(_cells, x0, y0, x1, y1, _min_x, _min_y, _max_x, _max_y)
    return _min_x, _max_x, _min_y, _max_y, _cells


def load_test_cells():
    _cells = list()
    _cells.append(extractor.Cell(1.0, 1.0, 10.5, 10.0))
    _cells.append(extractor.Cell(10.0, 1.0, 20.0, 10.0))
    _cells.append(extractor.Cell(19.9, 1.0, 30.5, 10.0))
    _cells.append(extractor.Cell(30.0, 1.0, 40.0, 20.0))
    _cells.append(extractor.Cell(1.0, 9.5, 15.0, 20.0))
    _cells.append(extractor.Cell(15.0, 9.5, 30.0, 20.0))

    return 1.0, 40.0, 1.0, 20.0, _cells


def load_text(definition_file):
    _cells = []
    text_def = open(definition_file, 'r')
    _min_x = -1.0
    _min_y = -1.0
    _max_x = -1.0
    _max_y = -1.0

    for line in text_def:
        x0, y0, x1, y1, s = line.strip().split('|')
        _min_x, _min_y, _max_x, _max_y = store_cell(_cells, x0, y0, x1, y1, _min_x, _min_y, _max_x, _max_y)
    return _min_x, _max_x, _min_y, _max_y, _cells


def store_cell(_cells, x0, y0, x1, y1, _min_x, _min_y, _max_x, _max_y):
    if float(x0) < float(x1):
        cell_x0 = float(x0)
        cell_x1 = float(x1)
    else:
        cell_x0 = float(x1)
        cell_x1 = float(x0)
    if float(y0) < float(y1):
        cell_y0 = float(y0)
        cell_y1 = float(y1)
    else:
        cell_y0 = float(y1)
        cell_y1 = float(y0)
    _cells.append(extractor.Cell(cell_x0, cell_y0, cell_x1, cell_y1))
    if _min_x == -1 or cell_x0 < _min_x:
        _min_x = cell_x0
    if _max_x == -1 or cell_x1 > _max_x:
        _max_x = cell_x1
    if _min_y == -1 or cell_y0 < _min_y:
        _min_y = cell_y0
    if _max_y == -1 or cell_y1 > _max_y:
        _max_y = cell_y1
    return _min_x, _min_y, _max_x, _max_y


def plot_cells(rec_list, color, fill=False):
    """

    :param rec_list: list of rectangles to add to the plot
    :param fill:
    :param color:
    :type rec_list: list
    """
    for _rec in rec_list:
        add_rect(x0=_rec.x0, y0=_rec.y0, x1=_rec.x1, y1=_rec.y1, color=color, fill=fill)


def logging_setup():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    _logger = logging.getLogger('table_extractor')
    # create file handler which logs even debug messages
    fh = logging.FileHandler('table_extractor.log', mode='w')
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
    # rec_def_file = 'rec_def-JT03365818-1.log'
    # text_def_file = 'text_def-JT03365818-1.log'
    rec_def_file = 'rec_def.log'
    text_def_file = 'text_def.log'
    fig = plt.figure()
    rec = fig.add_subplot(111, aspect='equal')

    # min_x, max_x, min_y, max_y, cells = load_test_cells()
    min_x, max_x, min_y, max_y, cells = load_cells(rec_def_file)
    plot_cells(cells, 'blue')

    min_x, max_x, min_y, max_y, text_blocks = load_text(text_def_file)
    plot_cells(text_blocks, 'black')

    plt.xlim(min_x - 10.0, max_x + 10.0)
    plt.ylim(min_y - 10.0, max_y + 10.0)

    # Coalesce cells within the same table to keep only the outer edges
    outer_edges = extractor.find_outer_edges(cells)
    for cell in outer_edges:
        print 'Collapsed cell built from {nrows} inner rows and {ncolumns} inner columns'.format(nrows=cell.rows,
                                                                                                 ncolumns=cell.columns)
    plot_cells(outer_edges, 'red')

    plt.show()

