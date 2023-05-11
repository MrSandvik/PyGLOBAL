

// Click-and-drag values between cells in Value column
/*
$(document).ready(function () {
    const table = $("#example").DataTable();
  
    $(".value-cell").draggable({
      helper: "clone",
      revert: "invalid",
    });
  
    $(".value-cell").droppable({
      accept: ".value-cell",
      drop: function (event, ui) {
        const draggedValue = ui.draggable.data("value");
        const targetValue = $(this).data("value");
  
        // Swap the values between the dragged and target cells
        ui.draggable.text(targetValue).data("value", targetValue);
        $(this).text(draggedValue).data("value", draggedValue);
  
        // Update the DataTables data to maintain consistency
        const draggedCell = table.cell(ui.draggable);
        const targetCell = table.cell(this);
        draggedCell.data(targetValue);
        targetCell.data(draggedValue);
      },
    });
  });
  
*/
  // click-and-drag rows
/*
$(document).ready(function() {
    // Create the DataTable instance
    var table = $('#example').DataTable();
  
    // Make the rows draggable
    $('#example tbody').sortable({
      helper: 'clone',
      start: function(event, ui) {
        ui.item.addClass('selected');
      },
      stop: function(event, ui) {
        ui.item.removeClass('selected');
      }
    }).disableSelection();
  
    // Make the rows droppable
    $('#example tbody').on('drop', 'tr', function(event, ui) {
      var dragged = ui.draggable;
      var dropped = $(this);
      var temp = dragged.clone();
      dragged.remove();
      if (dropped.index() == 0) {
        temp.prependTo('#example tbody');
      } else {
        temp.insertAfter($('#example tbody tr:nth-child(' + (dropped.index()) + ')'));
      }
    });
  });
  */