let debugging = true; // Set this to true to enable console logging

$(document).ready(function () {
    // Clear all search filters by hitting shift-esc
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && event.shiftKey) {
            event.preventDefault(); // Add this line to prevent the default action
            table.clearHeaderFilter();
            table.setData(table.getData()); // Refresh the table
        }
    });

    //    const tableData = [
    //        { plus: '+', hash: '', amp: '', eth: 'Ð', kontonr: '1950', kundenr: '0', levnr: '0', bilagsnr: '22503', buntnr: '1234', tekst: 'This is a text', belop: '1234.56' },
    //        { plus: '+', hash: '', amp: '', eth: 'Ð', kontonr: '1950', kundenr: '0', levnr: '0', bilagsnr: '22508', buntnr: '1234', tekst: 'This is a texty', belop: '-1234.56' },
    //        { plus: '+', hash: '', amp: '', eth: '', kontonr: '1950', kundenr: '12011', levnr: '0', bilagsnr: '22505', buntnr: '1243', tekst: 'This is another text', belop: '218.00' },
    //    ];

    fetch('get.php')
        .then(response => response.json())
        .then(data => {

            let locale = navigator.language;
            let formatting = {};

            if (locale === 'nb-NO') {
                formatting = {
                    decimal: ",",
                    thousand: " ",
                    symbol: "",
                };
            } else if (locale === 'de-DE') {
                formatting = {
                    decimal: ",",
                    thousand: ".",
                    symbol: "",
                };
            } else {
                formatting = {
                    decimal: ".",
                    thousand: "",
                    symbol: ""
                }
            }

            const tableData = data.map(row => {
                return {
                    plus: '+', // assuming this value is static
                    hash: '',  // assuming this value is static
                    amp: '',   // assuming this value is static
                    eth: row['GLAccRec']['value'],  // replace with the actual key for this column
                    kontonr: row['BatchNo']['value'],  // replace with the actual key for this column
                    kundenr: row['CustomerNo']['value'], // replace with the actual key for this column
                    levnr: '0',  // assuming this value is static
                    bilagsnr: row['VoucherNo']['value'],  // replace with the actual key for this column
                    buntnr: row['BatchNo']['value'],  // replace with the actual key for this column
                    tekst: row['Description']['value'],  // replace with the actual key for this column
                    belop: row['Amount']['value']  // replace with the actual key for this column
                };
            });

            const headerFilterPlaceholder = '...';

            const filterText = (headerValue, rowValue) => {
                const regex = new RegExp('^' + headerValue.replace(/\*/g, '.*') + '$', 'i');
                return regex.test(rowValue);
            };

            const table = new Tabulator("#table1", {
                data: tableData,
                layout: "fitColumns",
                columns: [
                    { title: "+", field: "plus", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "#", field: "hash", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "&", field: "amp", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Ð", field: "eth", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Kontonr", field: "kontonr", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Kundenr", field: "kundenr", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Levnr", field: "levnr", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Bilagsnr", field: "bilagsnr", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Buntnr", field: "buntnr", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Tekst", field: "tekst", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterText, headerFilterLiveFilter: false },
                    { title: "Beløp", formatter: "money", formatterParams: formatting, hozAlign: "right", field: "belop", headerFilter: "input", headerFilterPlaceholder: headerFilterPlaceholder, headerFilterFunc: filterNumber, headerFilterLiveFilter: false },
                ],
            });
        })
        .catch(error => console.error('Error:', error));


    console.log(navigator.language);

    // Apply custom styling to header filters
    $(".tabulator-header-filter").css({
        "background-color": "rgba(99, 179, 237, 0.1)", // Faint blue background
        "border": "none",
        "width": "100%",
    });
});
