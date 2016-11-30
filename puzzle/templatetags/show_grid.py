from django import template


register = template.Library()


@register.filter
def row_num(y):
    """ increments y """
    return y + 1


@register.inclusion_tag('puzzle/grid.html', takes_context=True, name='show_grid')
def show_grid(context):
    """ display the grid in template """
    filled_cells = context['filled_cells']  # get the cells that will be pre-filled
    cells = []  # stores cell co-ordinates
    values = []  # stores cell values
    for cell_to_fill in filled_cells:  # fill the lists
        cells.append([cell_to_fill[0], cell_to_fill[1]])
        values.append(cell_to_fill[2])

    return {
        'numbers': [0, 1, 2, 3, 4, 5, 6, 7, 8],  # list of numbers(for template)
        'cells': cells,
        'values': values
    }


@register.simple_tag(takes_context=True, name='show_cell')
def show_cell(context, *args):
    """ display a single cell """
    """ takes x and y as input """
    x = args[0]
    y = args[1]  # get x and y
    try:
        index = context['cells'].index((x, y))
        return '<td class="cell" id="cell-%d-%d" sudoku_filled="true" tabindex="-1">%d</td>' % (x, y, context['values'][index])
    except ValueError:
        """ if the cell is not filled """
        return '<td class="cell" id="cell-%d-%d" tabindex="-1"></td>' % (x, y)
