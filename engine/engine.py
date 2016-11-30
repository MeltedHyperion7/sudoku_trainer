__author__ = 'MeltedHyperion7'

from .extras import generate_grid, num_set, Methods


class Puzzle:
    steps = []
    grid = generate_grid()
    pgrid = generate_grid()

    def __init__(self, cells):
        """ filled cells are assigned values """
        for cell in cells:
            self.grid[cell[0]][cell[1]] = cell[2]

        for i in range(9):
            for j in range(9):
                if self.grid[i][j] is None:
                    self.pgrid[i][j] = num_set - (set(self._col_values(i)) | set(self._row_values(j)) | set(self._square_values(i, j)))

    def _cell_string_repr(self, *args):
        if len(args) == 1:
            return '(%s, %d)' % (chr(args[0][0] + 65), args[0][1] + 1)
        elif len(args) == 2:
            return '(%s, %d)' % (chr(args[0] + 65), args[1] + 1)

    def _possibility_string_repr(self, pos):
        res = ''
        for p in list(pos):
            res += '%d,' % p
        return res

    def _grid_unsolved(self):
        """ tells if the grid is still unsolved """
        for c in self.grid:
            if None in c:
                return True

        return False

    def print_grid(self):
        for i in range(9):
            for j in range(9):
                if self.grid[j][i] is None:
                    print('N', end=' ')
                else:
                    print(str(self.grid[j][i]), end=' ')
            print()

    def _get_col(self, x):
        """ returns all indexes in column x """
        return list(((x, y) for y in range(9)))

    def _col_values(self, x):
        """ returns all the values present in column x """
        return self.grid[x]

    def _col_possibilities(self, x):
        """ returns all possible values in a column """
        res = set()
        for cell in self.pgrid[x]:
            if not cell is None:
                res = res.union(cell)
        return res

    def _get_row(self, y):
        """ returns all the cell indexes in row y """
        res = []
        for x in range(9):
            res.append((x, y))
        return res

    def _row_values(self, y):
        """ returns all the values present in row y """
        res = []
        for x in range(9):
            res.append(self.grid[x][y])
        return res

    def _row_possibilities(self, y):
        """ returns all possible values of a row """
        res = set()
        for i in range(9):
            if not self.pgrid[i][y] is None:
                res = res.union(self.pgrid[i][y])

        return res

    def _square_corner_cell(self, x, y):
        """ returns the left-upper corner cell index of the square of cell (x,y) """
        return (x-(x%3),y-(y%3))

    def _get_square(self, x, y):
        """ returns all cell indexes of the square of cell (x,y) """
        cx, cy = self._square_corner_cell(x, y)
        res = []
        for gx in range(3):
            for gy in range(3):
                res.append((cx + gx,cy + gy))

        return res

    def _square_values(self, x, y):
        """ returns all values present in the square of cell (X,y) """
        cx, cy = self._square_corner_cell(x, y)
        res = []
        for gx in range(3):
            for gy in range(3):
                res.append(self.grid[cx + gx][cy + gy])

        return res

    def _square_possibilities(self, x, y):
        cx, cy = self._square_corner_cell(x, y)
        res = set()
        for i in range(3):
            for j in range(3):
                if not self.pgrid[cx+i][cy+j] is None:
                    res = res.union(self.pgrid[cx+i][cy+j])

        return res

    def _get_group_in_square(self, t, cx, cy, i):
        res = []
        cx, cy = self._square_corner_cell(cx,cy)
        if t == 'r':
            for j in range(3):
                res.append((cx + j, cy + i))
        elif t == 'c':
            for j in range(3):
                res.append((cx + i, cy + j))

        return res

    def _possibilities_of_other_cells_in_group(self, group, x, y):
        """ returns the possibilities of all cells in a group except cell (x,y) """
        res = set()
        for cell in group:
            if (cell[0] == x and cell[1] == y) or self.pgrid[cell[0]][cell[1]] is None:
                continue
            res = res.union(self.pgrid[cell[0]][cell[1]])

        return res

    def _find_naked_pairs_in_group(self, group, group_t):
        """ find naked/hidden pairs in the grid and alter possibilities """
        pair_possib = []
        fetchback_coords = []
        confirmed_pairs = []
        for cell in group:
            if not self.pgrid[cell[0]][cell[1]] is None and len(self.pgrid[cell[0]][cell[1]]) == 2:
                possibilities = self.pgrid[cell[0]][cell[1]]
                try:
                    index = pair_possib.index(possibilities)
                    confirmed_pairs.append({'cells': [(fetchback_coords[index][0], fetchback_coords[index][1]), (cell[0], cell[1])], 'p': possibilities})
                except ValueError:
                    pair_possib.append(possibilities)
                    fetchback_coords.append((cell[0], cell[1]))
                    pass

        for pair in confirmed_pairs:
            # get the step string
            step_string = ""
            c1 = self._cell_string_repr(pair['cells'][0])
            c2 = self._cell_string_repr(pair['cells'][1])
            ps = self._possibility_string_repr(pair['p'])

            if group_t == 'c':
                step_string = '%s and %s form a naked pair in their column. We can eliminate %s as possibilities from all other cells of the column.' % (c1, c2, ps)
            elif group_t == 'r':
                step_string = '%s and %s form a naked pair in their row. We can eliminate %s as possibilities from all other cells of the row.' % (c1, c2, ps)
            elif group_t == 's':
                step_string = '%s and %s form a naked pair in their square. We can eliminate %s as possibilities from all other cells of the square.' % (c1, c2, ps)

            self.steps.append({'s_type': 'naked',
                               's_text': step_string,
                               'x1': pair['cells'][0][0],
                               'y1': pair['cells'][0][1],
                               'x2': pair['cells'][1][0],
                               'y2': pair['cells'][1][1],
                               'h': group_t
                               })

            for cell in group:
                if cell not in pair['cells'] and not self.pgrid[cell[0]][cell[1]] is None:
                    self.pgrid[cell[0]][cell[1]] -= pair['p']

    def _find_naked_pairs(self):
        for i in range(9):
            self._find_naked_pairs_in_group(self._get_row(i), 'r')
            self._find_naked_pairs_in_group(self._get_col(i), 'c')
            if i in range(3):
                for j in range(3):
                    self._find_naked_pairs_in_group(self._get_square(i*3, j*3), 's')

    def _find_locked_possibilities_in_square_group(self, square, group, t):
        other_cells_possibilities = set()
        group_possibilities = set()
        for cell in square:
            if cell in group:
                if not self.pgrid[cell[0]][cell[1]] is None:
                    group_possibilities = group_possibilities.union(self.pgrid[cell[0]][cell[1]])
                continue
            if not self.pgrid[cell[0]][cell[1]] is None:
                other_cells_possibilities = other_cells_possibilities.union(self.pgrid[cell[0]][cell[1]])

        punique = group_possibilities - other_cells_possibilities
        if len(punique) >= 1:
            if len(punique) is 1:
                sing_plural = 'possibility'  # ensure correct grammar
                is_are = 'is'
            else:
                sing_plural = 'possibilities'
                is_are = 'are'

            square_cell_string = self._cell_string_repr(group[0][0], group[0][1])
            p = self._possibility_string_repr(punique)
            if t == 'r':
                row_or_column = 'row'
                n = group[0][1] % 3
                if n == 0:
                    square_group_string = 'top row'
                elif n == 1:
                    square_group_string = 'middle row'
                else:
                    square_group_string = 'bottom row'

                for cell in self._get_row(group[0][1]):
                    if cell in group:
                        continue
                    if not self.pgrid[cell[0]][cell[1]] is None:
                        self.pgrid[cell[0]][cell[1]] -= punique
            elif t == 'c':
                row_or_column = 'column'
                n = group[0][0] % 3
                if n == 0:
                    square_group_string = 'left column'
                elif n == 1:
                    square_group_string = 'middle column'
                else:
                    square_group_string = 'right column'

                for cell in self._get_col(group[0][0]):
                    if cell in group:
                        continue
                    if not self.pgrid[cell[0]][cell[1]] is None:
                        self.pgrid[cell[0]][cell[1]] -= punique

            step_string = 'Look at the square of cell %s. The %s of %s %s limited to the %s. We have a locked possibility and can remove %s as a possibility from the rest of the %s.' % (
            square_cell_string, sing_plural, p, is_are, square_group_string, p, row_or_column)
            self.steps.append({
                's_type': 'locked',
                's_text': step_string,
                'x1': group[0][0],
                'y1': group[0][1],
                'x2': group[2][0],
                'y2': group[2][1],
                'h1': 's',
                'h2': t
            })

    def _find_locked_possibilities_in_line_group(self, line, group, t):
        pgroup = set()
        pother = set()
        for cell in line:
            if cell in group:
                if not self.pgrid[cell[0]][cell[1]] is None:
                    pgroup = pgroup.union(self.pgrid[cell[0]][cell[1]])
                continue
            if not self.pgrid[cell[0]][cell[1]] is None:
                pother = pother.union(self.pgrid[cell[0]][cell[1]])

        punique = pgroup - pother
        if len(punique) >= 1:
            p = self._possibility_string_repr(punique)
            if len(punique) is 1:
                sing_plural = 'possibility'  # ensure correct grammar
                is_are = 'is'
            else:
                sing_plural = 'possibilities'
                is_are = 'are'

            if t == 'r':
                row_or_column = 'row'
                num = line[0][1]
                n = group[0][0] % 3
                if n == 0:
                    line_group_string = 'left square'
                elif n == 1:
                    line_group_string = 'middle square'
                else:
                    line_group_string = 'right square'
            elif t == 'c':
                row_or_column = 'column'
                num = line[0][0]
                n = group[0][1] % 3
                if n == 0:
                    line_group_string = 'top square'
                elif n == 1:
                    line_group_string = 'middle square'
                else:
                    line_group_string = 'bottom square'

            step_string = 'Look at %s %d. The %s of %s %s restricted to the %s. We have a locked possibility and can remove %s from all other cells of this square.' % (row_or_column, num, sing_plural, p, is_are, line_group_string, p)
            self.steps.append({
                's_type': 'locked',
                's_text': step_string,
                'x1': group[0][0],
                'y1': group[0][1],
                'x2': group[2][0],
                'y2': group[2][1],
                'h1': t,
                'h2': 's'
            })

            square = self._get_square(group[0][0], group[0][1])
            for cell in square:
                if cell in group:
                    continue
                if not self.pgrid[cell[0]][cell[1]] is None:
                    self.pgrid[cell[0]][cell[1]] -= punique

    def _find_locked_possibilities_in_line(self, t, n):
        if t == 'r':
            cells = self._get_row(n)
        elif t == 'c':
            cells = self._get_col(n)
        for i in range(3):
            self._find_locked_possibilities_in_line_group(cells, cells[i*3:3], t)

    def _find_locked_possibilities_in_square(self, cx, cy):
        cells = self._get_square(cx, cy)
        for i in range(3):
            self._find_locked_possibilities_in_square_group(cells, self._get_group_in_square('r', cx, cy, i), 'r')
            self._find_locked_possibilities_in_square_group(cells, self._get_group_in_square('c', cx, cy, i), 'c')

    def _find_locked_possibilities(self):
        for i in range(9):
            self._find_locked_possibilities_in_line('r', i)
            self._find_locked_possibilities_in_line('c', i)
            if i in range(3):
                for j in range(3):
                    self._find_locked_possibilities_in_square(i*3, j*3)

    def _fill_cell(self, x, y, value, method, group_t=None):
        self.grid[x][y] = value
        self.pgrid[x][y] = None
        affected_cells = self._get_col(x) + self._get_row(y) + self._get_square(x, y)

        # get the entire step
        step_string = ""
        cell_string = self._cell_string_repr(x, y)
        if method == Methods.SINGLE_POS:
            step_string = 'Since %d is the only possibility in cell %s, we fill it.' % (value, cell_string)
            self.steps.append({'s_type': 'fill_single', 's_text': step_string, 'x': x, 'y': y, 'v': value})
        elif method == Methods.UNIQUE_POS:
            if group_t == 'c':
                step_string = '%s can be safely filled with %d because it is the only cell in its column in which %d can be placed.' % (cell_string, value, value)
            elif group_t == 'r':
                step_string = '%s can be safely filled with %d because it is the only cell in its row in which %d can be placed.' % (cell_string, value, value)
            elif group_t == 's':
                step_string = '%s can be safely filled with %d because it is the only cell in its square in which %d can be placed.' % (cell_string, value, value)

            self.steps.append({'s_type': 'fill_unique', 's_text': step_string, 'x': x, 'y': y, 'v': value, 'h': group_t})

        for cell in affected_cells:
            if not self.pgrid[cell[0]][cell[1]] is None:
                    self.pgrid[cell[0]][cell[1]].discard(value)

    def _solve_group(self, t, x=None, y=None, sp=False):
        # sp -> use single possibility technique if true
        success = False
        if t == 'c':
            cells = self._get_col(x)
        elif t == 'r':
            cells = self._get_row(y)
        elif t == 's':
            cells = self._get_square(x, y)

        for cell in cells:
            if not self.pgrid[cell[0]][cell[1]] is None:
                cell_possibilities = self.pgrid[cell[0]][cell[1]]
                possibilities_of_others = self._possibilities_of_other_cells_in_group(cells, cell[0], cell[1])
                if len(cell_possibilities - possibilities_of_others) == 1:  # unique possibility
                    self._fill_cell(cell[0], cell[1], list(cell_possibilities - possibilities_of_others)[0], Methods.UNIQUE_POS, group_t=t)
                    success = True

                elif sp is True and len(cell_possibilities) == 1:  # single possibility
                    self._fill_cell(cell[0], cell[1], list(cell_possibilities)[0], Methods.SINGLE_POS)
                    success = True

        return success

    def solve(self):
        """ solve the grid """
        use_single_possibility = False  # use single possibility check or not
        while self._grid_unsolved():
            solved_this_run = False  # if any cells were solved in this run
            for i in range(9):
                while self._solve_group('c', x=i, sp=use_single_possibility):
                    solved_this_run = True
                    use_single_possibility = False
                while self._solve_group('r', y=i, sp=use_single_possibility):
                    solved_this_run = True
                    use_single_possibility = False
                if i in range(3):
                    for j in range(3):
                        while self._solve_group('s', x=i*3, y=j*3, sp=use_single_possibility):
                            solved_this_run = True
                            use_single_possibility = False
            if not solved_this_run:
                if not use_single_possibility:
                    use_single_possibility = True
                else:
                    self._find_naked_pairs()
                    self._find_locked_possibilities()
