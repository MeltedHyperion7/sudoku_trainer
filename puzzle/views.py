from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from engine.engine import Puzzle
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser


@parser_classes([JSONParser])
class SudokuEngineView(APIView):
    def post(self, request, *args, **kwargs):
        """ get the filled cells, solve the puzzle, return the steps """
        filled_cells = request.data
        grid = []
        for cell in filled_cells:
            grid.append((int(cell['x']), cell['y'], cell['v']))
        puzzle = Puzzle(grid)
        puzzle.solve()
        result = puzzle.steps
        return Response(result, status=status.HTTP_200_OK)


def solver(request):
    return render(request, 'puzzle/puzzle_page.html', {'filled_cells': []})
