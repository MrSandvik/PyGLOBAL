$(document).ready(function () {
    var cursorPositionX = 0;
    var cursorPositionY = 0;
    var cursor = $('#cursor');

    function moveCursor(x, y) {
        cursorPositionX += x;
        cursorPositionY += y;

        // Make sure the cursor doesn't go out of the grid.
        cursorPositionX = Math.max(0, Math.min(cursorPositionX, 39));
        cursorPositionY = Math.max(0, Math.min(cursorPositionY, 39));

        cursor.css('grid-column-start', cursorPositionX + 1);
        cursor.css('grid-row-start', cursorPositionY + 1);
    }

    $(document).keydown(function (e) {
        switch (e.which) {
            case 37: // left
                moveCursor(-1, 0);
                break;

            case 38: // up
                moveCursor(0, -1);
                break;

            case 39: // right
                moveCursor(1, 0);
                break;

            case 40: // down
                moveCursor(0, 1);
                break;

            default: return; // exit this handler for other keys
        }
        e.preventDefault(); // prevent the default action (scroll / move caret)
    });
});
