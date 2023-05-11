<?php
// Database connection parameters
$servername = "orion";
$username = "root";
$password = "(Volvo90V)";
$dbname = "marlogasglobaldata";

try {
    // Create a new PDO instance
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);

    // Set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // SQL query
    $sql = "SELECT AgreementCode, BatchNo, CreatedBy, Created, GLAccRec, CustomerNo, ExchangeRate, VoucherNo, BatchNo, Description, Amount FROM DebLTransaction ORDER BY UniqueNo LIMIT 50";

    // Prepare statement
    $stmt = $conn->prepare($sql);

    // Execute the query
    $stmt->execute();

    // Fetch all rows into an associative array
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Initialize an empty array to hold the results with data types
    $resultsWithTypes = [];

    // Loop over the results
    foreach ($results as $row) {
        // Initialize an array to hold the current row with data types
        $rowWithTypes = [];

        // Loop over each value in the row
        foreach ($row as $key => $value) {
            // Add the value and its data type to the row array
            $rowWithTypes[$key] = [
                'value' => $value,
                'type' => gettype($value),
            ];
        }

        // Add the row to the results array
        $resultsWithTypes[] = $rowWithTypes;
    }

    // Convert the results to JSON
    $json = json_encode($resultsWithTypes);

    echo $json;

    $conn = null;

} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}


?>
