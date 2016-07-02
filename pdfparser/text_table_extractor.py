from pdfparser import logger, _log_level, _config


class Cell:

    def __init__(self, x0, y0, x1, y1, rows=1, columns=1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        height = abs(self.y0 - self.y1)
        self.rows = rows
        width = abs(self.x0 - self.x1)
        self.columns = columns

    def __repr__(self):
        return '[' + 'x0: ' + str(self.x0) + ', y0: ' + str(self.y0) \
               + ', x1: ' + str(self.x1) + ', y1: ' + str(self.y1) \
               + ', rows: ' + str(self.rows) + ', columns: ' + str(self.columns) + ']'


class Row:

    def __init__(self):
        self.max_y = None
        self.min_y = None
        self.cells = list()

    def add_cell(self, cell):
        self.cells.append(cell)
        self.update_boundaries(cell)

    def update_boundaries(self, cell):
        if not self.min_y or cell.y0 < self.min_y:
            self.min_y = cell.y0
        if not self.max_y or cell.y1 > self.max_y:
            self.max_y = cell.y1

    def included(self, cell):
        if cell.y0 >= self.min_y and cell.y1 <= self.max_y:
            return True
        return False

    def aligned(self, cell):
        if self.min_y > cell.y0 and self.min_y > cell.y1:
            return False
        if self.max_y <= cell.y0 and self.max_y <= cell.y1:
            return False
        return True


class Table:

    def __init__(self):
        self.max_y = None
        self.min_y = None
        self.cells = list()

    def add_cells(self, row):
        for cell in row:
            self.cells.append(cell)
            self.update_boundaries(cell)

    def update_boundaries(self, cell):
        if not self.min_y or cell.y0 < self.min_y:
            self.min_y = cell.y0
        if not self.max_y or cell.y1 > self.max_y:
            self.max_y = cell.y1

    def included(self, cell):
        if cell.y0 >= self.min_y and cell.y1 <= self.max_y:
            return True
        return False


def find_table_cells(cells):

    candidate_cells = list()
    table = Table()
    candidate_row = Row()
    for cell in cells:
        if len(candidate_row.cells) == 0:
            candidate_row.add_cell(cell)
        else:
            if candidate_row.aligned(cell) or candidate_row.included(cell) or table.included(cell):  # append to candidate row
                candidate_row.add_cell(cell)
            else:
                if len(candidate_row.cells) > 2:    # save previous row
                    candidate_cells.extend(candidate_row.cells)
                    table.add_cells(candidate_row.cells)

                candidate_row = Row()
                candidate_row.add_cell(cell)

    if len(candidate_row.cells) > 2:
        candidate_cells.extend(candidate_row.cells)

    return candidate_cells


def compare_cells(cell):
    return cell.y0, cell.y1, cell.x0, cell.x1


def log(log_text):
    if _log_level > 2:
        logger.debug(log_text)

if __name__ == '__main__':
    pass