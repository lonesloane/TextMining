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


def load_cells(rec_def_file):
    _cells = []
    rec_def = open(rec_def_file, 'r')
    min_x = -1.0
    min_y = -1.0
    max_x = -1.0
    max_y = -1.0
    for line in rec_def:
        x0, y0, x1, y1 = line.strip().split(',')
        min_x, min_y, max_x, max_y  = store_cell(_cells, x0, y0, x1, y1, min_x, min_y, max_x, max_y)
    return min_x, max_x, min_y, max_y, _cells


def load_test_cells():
    _cells = list()
    _cells.append([1.0, 1.0, 10.5, 10.0])
    _cells.append([10.0, 1.0, 20.0, 10.0])
    _cells.append([19.9, 1.0, 30.5, 10.0])
    _cells.append([30.0, 1.0, 40.0, 20.0])
    _cells.append([1.0, 9.5, 15.0, 20.0])
    _cells.append([15.0, 9.5, 30.0, 20.0])

    return 1.0, 40.0, 1.0, 20.0, _cells


def load_text(text_def_file):
    _cells = []
    text_def = open(text_def_file, 'r')
    min_x = -1.0
    min_y = -1.0
    max_x = -1.0
    max_y = -1.0

    for line in text_def:
        x0, y0, x1, y1, s = line.strip().split('|')
        min_x, min_y, max_x, max_y  = store_cell(_cells, x0, y0, x1, y1, min_x, min_y, max_x, max_y)
    return min_x, max_x, min_y, max_y, _cells


def store_cell(_cells, x0, y0, x1, y1, min_x, min_y, max_x, max_y):
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
    _cells.append([cell_x0, cell_y0, cell_x1, cell_y1])
    if min_x == -1 or cell_x0 < min_x:
        min_x = cell_x0
    if max_x == -1 or cell_x1 > max_x:
        max_x = cell_x1
    if min_y == -1 or cell_y0 < min_y:
        min_y = cell_y0
    if max_y == -1 or cell_y1 > max_y:
        max_y = cell_y1
    return min_x, min_y, max_x, max_y


def plot_cells(cells, color, fill=False):
    for x0, y0, x1, y1 in cells:
        add_rect(x0=x0, y0=y0, x1=x1, y1=y1, color=color, fill=fill)


if __name__ == '__main__':
    rec_def_file = 'rec_def-JT03365818-1.log'
    text_def_file = 'text_def-JT03365818-1.log'
    fig = plt.figure()
    rec = fig.add_subplot(111, aspect='equal')

    min_x, max_x, min_y, max_y, cells = load_test_cells()
    min_x, max_x, min_y, max_y, cells = load_cells(rec_def_file)
    plot_cells(cells, 'blue')

    min_x, max_x, min_y, max_y, text_blocks = load_text(text_def_file)
    plot_cells(text_blocks, 'black')

    plt.xlim(min_x - 10.0, max_x + 10.0)
    plt.ylim(min_y - 10.0, max_y + 10.0)

    # Coalesce cells within the same table to keep only the outer edges
    outer_edges = extractor.find_outer_edges(cells)
    plot_cells(outer_edges, 'red')

    plt.show()
