let filterRow;

function initColumnToggle(tableInstance) {
    // Show the modal on right-click and prevent the default context menu
    $('#example').on('contextmenu', function (e) {
        e.preventDefault();
        const columnToggleModal = new bootstrap.Modal(document.getElementById('columnToggleModal'));
        columnToggleModal.show();
    });

    // Generate the column checkboxes inside the modal
    tableInstance.columns().every(function (idx) {
        const columnHeader = $(this.header()).text();
        const checkboxId = 'toggleColumn' + idx;

        const formCheck = $('<div class="form-check"></div>');
        const input = $(`<input class="form-check-input" type="checkbox" value="${idx}" id="${checkboxId}" checked>`);
        const label = $(`<label class="form-check-label" for="${checkboxId}">${columnHeader}</label>`);

        input.appendTo(formCheck);
        label.appendTo(formCheck);
        formCheck.appendTo('#columnToggleForm');
    });

    // Apply the show/hide functionality when the "Apply" button is clicked
    $('#applyColumnToggle').on('click', function () {
        $('#columnToggleForm input[type="checkbox"]').each(function () {
            const columnIdx = $(this).val();
            const column = tableInstance.column(columnIdx);
            column.visible($(this).is(':checked'));

            // Show/hide the corresponding search input elements in the filter row
            filterRow.find(`th:eq(${columnIdx})`).toggle($(this).is(':checked'));
        });

        // Close the modal
        const columnToggleModal = bootstrap.Modal.getInstance(document.getElementById('columnToggleModal'));
        columnToggleModal.hide();
    });
}

$(document).ready(function () {
    let table = $('#example').DataTable({
        colReorder: false,
        responsive: true,
        orderCellsTop: true,
        dom: 'rt',
        search: true,
        colResizable: true,
        pageLength: -1,
        initComplete: function () {
            let tableInstance = this.api();
            tableInstance.columns().every(function () {
                const column = this;
                const input = $('<input type="text" class="my-search">')
                    .appendTo($(column.header()))
                    .on('change keyup', function () {
                        const val = $.fn.dataTable.util.escapeRegex($(this).val()).replace(/\\\*/g, '.*');
                        column.search(val ? '^'+val.replace(/\*/g, '.*') : '', true, false).draw();
                    });
            });

            // Add filtering row
            filterRow = $('<tr class="my-search"></tr>');
            tableInstance.columns().every(function () {
                const th = $('<th class="my-search"></th>');
                $(this.header()).children('input').clone(true).appendTo(th);
                th.appendTo(filterRow);
            });
            filterRow.appendTo(tableInstance.table().header());

            // Remove input elements from header row
            tableInstance.columns().every(function () {
                $(this.header()).children('input').remove();
            });

            // Call the initColumnToggle function after initializing the table
            initColumnToggle(tableInstance);


        },
        drawCallback: function () {
            // Apply alternating row colors
            $('tbody > tr:even', this.api().table().node()).css('background-color', 'white');
            $('tbody > tr:odd', this.api().table().node()).css('background-color', '#eeeeee');
        }
    });
});
