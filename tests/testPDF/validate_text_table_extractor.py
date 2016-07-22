import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

import pdfparser.text_table_extractor as extractor
#from pdfparser.text_table_extractor import compare_cells


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


def plot_cells(rec_list, color, fill=False):
    """

    :param rec_list: list of rectangles to add to the plot
    :param fill:
    :param color:
    :type rec_list: list
    """
    for _rec in rec_list:
        add_rect(x0=_rec.x0, y0=_rec.y0, x1=_rec.x1, y1=_rec.y1, color=color, fill=fill)


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


def load_cells(definition_file):
    _cells = list()
    with open(definition_file, 'r') as rec_def:
        _min_x = -1.0
        _min_y = -1.0
        _max_x = -1.0
        _max_y = -1.0
        for line in rec_def:
            x0, y0, x1, y1, s = line.strip().split('|')
            _min_x, _min_y, _max_x, _max_y = store_cell(_cells, x0, y0, x1, y1, _min_x, _min_y, _max_x, _max_y)
    return _min_x, _max_x, _min_y, _max_y, _cells


def main():
    print 'Extracting table from text layout'
    txt_cells = []

    rec_def_file = 'text_def.log'
    min_x, max_x, min_y, max_y, cells = load_cells(rec_def_file)
    cells.sort(key=extractor.compare_cells, reverse=True)
    # TODO: write back the cells after sort...
    fig = plt.figure()
    global rec
    rec = fig.add_subplot(111, aspect='equal')

    plot_cells(cells, 'black')
    plt.xlim(min_x - 10.0, max_x + 10.0)
    plt.ylim(min_y - 10.0, max_y + 10.0)

    candidate_cells = extractor.find_table_cells(cells=cells)
    plot_cells(candidate_cells, 'red')

    plt.show()

    return 0


if __name__ == '__main__':
    sys.exit(main())