/* do we need bold text in highlighted groups? */

var Colours = {
    LIGHT: 1,
    DARK: 2,
    THIRD: 3,
    NONE: 4
};
var steps = []; // holds the solved steps
var step_ptr = 0, max_steps = 0;

/*
---Selection Functions
*/
function selectRow(y) {
    /* returns a list of all cells in row y */
    return $('#row-' + y + ' td');
}

function selectCol(x) {
    /* returns a list of all cells in column x */
    var target = "";
    for(var y=0; y <= 8;y++) {
        target += '#cell-' + x + '-' + y + ',';
    }
    target = target.slice(0, target.length-1);  // remove last comma
    return $(target);
}

function selectSquare(x, y) {
    /* select the square of cell (x,y) */
    var target = '', cx = x - (x % 3), cy = y - (y % 3);
    for(var i=0; i < 3; i++) {
        for(var j=0; j < 3; j++) {
            target += '#cell-' + (cx + i) + '-' + (cy + j) + ',';
        }
    }
    target = target.slice(0, target.length-1);  // remove last comma
    return $(target);
}
/*---*/

function highlightCell(x, y, colour) {
    /** highlight cell (x, y) **/
    $('#cell-' + x + '-' + y).removeClass('highlight-light highlight-dark'); // remove any existing formatting
    if(colour === Colours.DARK) {
        $('#cell-' + x + '-' + y).addClass('highlight-dark');
    }
    else if (colour === Colours.LIGHT) {
        $('#cell-' + x + '-' + y).addClass('highlight-light');
    }
}

function highlightGroup(group_t, colour, coords) {
    /* highlight or unhighlight a group */
    // TODO: add Colours.THIRD
    switch(group_t) {
        case 'r':
            if(colour === Colours.LIGHT) {
                selectRow(coords.y).removeClass('highlight-dark').addClass('highlight-light');  // toggle highlight-dark and highlight-light
            }
            else if (colour === Colours.DARK) {
                selectRow(coords.y).removeClass('highlight-light').addClass('highlight-dark');
            }
            else if (colour === Colours.NONE) {  // remove highlighting
                selectRow(coords.y).removeClass('highlight-light highlight-dark');
            }
            break;
        case 'c':
            if(colour === Colours.LIGHT) {
                selectCol(coords.x).removeClass('highlight-dark').addClass('highlight-light');
            }
            else if (colour === Colours.DARK) {
                selectCol(coords.x).removeClass('highlight-light').addClass('highlight-dark');
            }
            else if (colour === Colours.NONE) {
                selectCol(coords.y).removeClass('highlight-light highlight-dark');
            }
            break;
        case 's':
            if(colour === Colours.LIGHT) {
                selectSquare(coords.x, coords.y).removeClass('highlight-dark').addClass('highlight-light');
            }
            else if (colour === Colours.DARK) {
                selectSquare(coords.x, coords.y).removeClass('highlight-light').addClass('highlight-dark');
            }
            else if (colour === Colours.NONE) {
                selectSquare(coords.y).removeClass('highlight-light highlight-dark');
            }
            break;
    }
}

function highlightFromTo(x1, y1, x2, y2, colour) {
    /*
    highlight all cells between (x1, y1) and (x2, y2) 
    works only if (x1, y1) and (x2, y2) are in line
    */
    var target = '';
    if (x1 === x2) {
        var i = 0;
        while (y1+i <= y2) {
            target += '#cell-' + x1 + '-' + (y1 + i) + ',';
        }
        target = target.slice(0, target.length-2);  // remove last comma
    }
    else if (y1 === y2) {
        var i = 0;
        while (x1+i <= x2) {
            target += '#cell-' + (x1 + i) + '-' + y1 + ',';
        }
        target = target.slice(0, target.length-2);  // remove last comma
    }
    $(target).removeClass('highlight-light highlight-dark highlight-third');
    switch(colour) {
        case Colours.DARK:
            $(target).addClass('highlight-dark');
            break;
        case Colours.LIGHT:
            $(target).addClass('highlight-light');
            break;
        case Colours.THIRD:
            $(target).addClass('highlight-third');
            break;
    }
}

function sendGrid() {
    /* sends the grid to the server for solving */
    var filled_cells = [];  //list of pre-filled cells
    var re = /^[1-9]$/;
    for(var x = 0;x <= 8; x++) {  //populate filled_cells
        for(var y=0;y <= 8; y++) {
            var cell_contents = $('#cell-' + x + '-' + y).text();
            if(re.test(cell_contents)) {
                filled_cells.push({"x": x, "y": y, "v": parseInt(cell_contents)});
            }
        }
    }
    $.ajax({ // TODO: complete this and remove the post request
        url: '/puzzle/engine/',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        method: 'POST',
        cache: false,
        data: JSON.stringify(filled_cells),
        success: function(data) {
            if(data.not_solved) {
                // if the problem couldn't be solved
                $('#step_text').text('Sorry, but we were unable to solve the puzzle.');
                return;
            }
            steps = data;
            steps.push({s_type: 'comp', s_text: 'And the solution is complete!'}); // final concluding step
            max_steps = steps.length;
            step_ptr = 0;
            showStep(0);
        },
        error: function(xhr, status, errthrow){
            alert(status);
        }
    });
}

function viewSolution() {
    /* view the complete solution */
        for (var step of steps) {
            if(step.s_type === 'fill_unique' || step.s_type === 'fill_single') // of the step fills a cell
                $('#cell-' + step.x + '-' + step.y).text(step.v);
        }
    showStep(max_steps-1); // show final step
}

function removeStepFormatting() {
    /*
    removes all current formatting
    */
    $('.grid td').removeClass('highlight-dark highlight-light highlight-third');
}

function showStep(n) {
    /* presents step n */
    //TODO: more security steps i.e. check data type, integer check
    if (n > max_steps || n < 0)  // cancel if n is greater than max no of steps
        return;
    removeStepFormatting(); // remove existing formatting
    step_ptr = n; // set step pointer to n
    var step = steps[step_ptr]; // get the step
    switch(step.s_type) { // find the type of step it is
        case 'fill_unique':
            $('#step_text').text(step.s_text);
            highlightGroup(step.h, Colours.LIGHT, {'x': step.x, 'y': step.y});
            highlightCell(step.x, step.y, Colours.DARK);
            $('#cell-' + step.x + '-' + step.y).text(step.v); // fill the cell
            break;
        case 'fill_single':
            $('#step_text').text(step.s_text);
            highlightCell(step.x, step.y, Colours.DARK);
            $('#cell-' + step.x + '-' + step.y).text(step.v); // fill the cell
            break;
        case 'locked':
            $('#step_text').text(step.s_text);
            highlightGroup(step.h1, Colours.LIGHT, {'x': step.x1, 'y': step.y1});
            highlightGroup(step.h2, Colours.THIRD, {'x': step.x1, 'y': step.y1});
            highlightFromTo(step.x1, step.y1, step.x2, step.y2, Colours.DARK);
            break;
        case 'naked':
            $('#step_text').text(step.s_text);
            highlightGroup(step.h, Colours.LIGHT, {'x': step.x1, 'y': step.y1});
            highlightCell(step.x1, step.y1, Colours.DARK);
            highlightCell(step.x2, step.y2, Colours.DARK);
            break;
        case 'comp':
            $('#step_text').text(step.s_text);
    }
}

function getXY(id) {
    /* gets the x and y coordinates of a cell from its id */
    var re = /cell-(\d)-(\d)/g;
    var res = re.exec(id);
    if(res) {
        return [parseInt(res[1]), parseInt(res[2])];
    }
}

/*
when document load
contains all event bindings
*/
$(document).ready(function(){
    // these functions control step navigation and solving buttons
    $('#solve').click(sendGrid);
    $('#steps_prev').click(function(){
        //TODO: remove the work of the current step
        showStep(step_ptr-1);
    });
    $('#steps_next').click(function(){
        showStep(step_ptr+1);
    });
    $('#show_comp').click(viewSolution);
    
    //controls grid navigation
    $('.grid .cell').keydown(function(e) {
        if(e.which >= 49 && e.which <= 57) {  //edit cell number
            $(this).text(e.which - 48);
            return;
        }
        else if(e.which === 8) {
            $(this).text("");
            e.stopPropagation();
        }
        switch(e.which) {  // grid navigation
            case 37: //left
                var active = getXY($(this).attr('id'));
                if(active[0] == 0) {
                    return;
                } else {
                    var target = "#cell-" + (active[0] - 1) + "-" + active[1];
                    $(target).focus();
                }
                break;
            case 38: //up
                var active = getXY($(this).attr('id'));
                if(active[1] == 0) {
                    return;
                } else {
                    var target = "#cell-" + active[0] + "-" + (active[1] - 1);
                    $(target).focus();
                }
                break;
            case 39: //right
                var active = getXY($(this).attr('id'));
                if(active[0] == 8) {
                    return;
                } else {
                    var target = "#cell-" + (active[0] + 1) + "-" + active[1];
                    $(target).focus();
                }
                break;
            case 40: //down
                var active = getXY($(this).attr('id'));
                if(active[1] == 8) {
                    return;
                } else {
                    var target = "#cell-" + active[0] + "-" + (active[1] + 1);
                    $(target).focus();
                }
                break;
        }
    }); 
});