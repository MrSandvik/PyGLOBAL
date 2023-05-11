function filterNumber(headerValue, rowValue, rowData, filterParams) {
    const number = parseFloat(rowValue.replace(",", "."));

    const searchStrings = headerValue.split(";");

    const operations = [];

    for (const searchString of searchStrings) {
        const operation = {
            abs: searchString.startsWith("!"),
            searchString: searchString.startsWith("!") ? searchString.substring(1) : searchString,
        };

        const hasSingleDigitWildcard = /[xX]/.test(operation.searchString);
        const hasDecimalWildcard = /#/.test(operation.searchString);

        // TODO: (math interval searching currently not possible)
        if (operation.searchString.match(/^\(.*::.*\)$/)) {
            operation.type = "interval";
            operation.value = operation.searchString;
        } else if (operation.searchString.match(/^\(.*\)$/)) {
            operation.type = "math_operations";
            operation.value = operation.searchString;
        } else if (operation.searchString.match(/^(>=|<=|>|<|!=)(-?\d+(\.\d+)?)$/) && !operation.abs) {
            operation.type = "operator";
            operation.value = operation.searchString;
        } else if (hasSingleDigitWildcard || hasDecimalWildcard) {
            operation.type = "wildcard";
            operation.value = operation.searchString;
        } else if (operation.searchString.match(/:[:]?/)) {
            operation.type = "interval";
            operation.value = operation.searchString;
        } else {
            operation.type = "exact";
            operation.value = operation.searchString;
        }

        operations.push(operation);
    }

    if (debugging) {
        console.log("Parsed operations:", operations);
    }

    return processOperations(operations, number);
}


function processOperations(operations, rowValue) {
    for (const operation of operations) {
        if (operation.abs) {
            rowValue = Math.abs(rowValue);
        }

        let isMatch = false;

        switch (operation.type) {
            case "exact":
                isMatch = matchExact(rowValue, operation.value);
                break;
            case "math_operations":
                isMatch = matchMathOperations(rowValue, operation.value);
                break;
            case "interval":
                isMatch = matchInterval(rowValue, operation.value);
                break;
            case "operator":
                isMatch = matchOperator(rowValue, operation.value);
                break;
            case "wildcard":
                isMatch = matchWildcard(rowValue, operation.value);
                break;
            default:
                console.error("Unknown operation type:", operation.type);
                break;
        }

        if (isMatch) {
            return true;
        }
    }

    return false;
}


function matchMathOperations(rowValue, searchString) {
    // Remove the parentheses from the searchString
alert(searchString);
    const cleanedSearchString = searchString.replace(/^\(|\)$/g, "");
console.log(">>>>>>>>>", cleanedSearchString);
    // Check if the searchString has an interval
    if (cleanedSearchString.includes("::")) {
        const [lowerBoundExpression, upperBoundExpression] = cleanedSearchString.split("::");

        // Evaluate the expressions
        const lowerBound = safeEval(lowerBoundExpression);
        const upperBound = safeEval(upperBoundExpression);
console.log(">>>>>>>",lowerBound, upperBound);
        // Check if the rowValue is within the interval, inclusive
        return rowValue >= lowerBound && rowValue <= upperBound;
    } else {
        // Evaluate the expression
        const value = safeEval(cleanedSearchString);

        // Check if the rowValue matches the value
        return rowValue === value;
    }
}

function safeEval(expression) {
    const validCharacters = /^[\d\s+\-*/.()]+$/;
    if (validCharacters.test(expression)) {
        const result = eval(expression);
        return parseFloat(result.toFixed(6)); // Round the result to 2 decimal places
    } else {
        throw new Error(`Invalid characters found in expression: "${expression}"`);
    }
}


function matchInterval(rowValue, searchString) {
    // Remove the parenthesis if there are any
    const cleanedSearchString = searchString.replace(/^\(|\)$/g, "");

    // Split the interval by ': or ::'
    const [lowerBound, upperBound] = cleanedSearchString.split(/:[:]?/).map(str => parseFloat(str));

    // Check if the rowValue is within the interval, inclusive
    return rowValue >= lowerBound && rowValue <= upperBound;
}

function matchOperator(rowValue, searchString) {
    const [, operator, value] = searchString.match(/^(>=|<=|>|<|!=)(-?\d+(\.\d+)?)$/);
    const parsedValue = parseFloat(value);
    console.log(operator);
    switch (operator) {
        case ">=":
            return rowValue >= parsedValue;
        case "<=":
            return rowValue <= parsedValue;
        case ">":
            return rowValue > parsedValue;
        case "<":
            return rowValue < parsedValue;
        case "!=":
            return rowValue !== parsedValue;
        default:
            console.error("Unknown operator:", operator);
            return false;
    }
}


function matchWildcard(rowValue, searchString) {
    // Check if there is a '#' before the decimal point
    if (/^[^.]*#/.test(searchString)) {
        console.error("'#' wildcard is only allowed after the decimal point:", searchString);
        return false;
    }

    // Convert rowValue to string, and split into integer and decimal parts
    let [integerPart, decimalPart = '00'] = rowValue.toString().split('.');

    // Split searchString into integer and decimal parts
    let [integerSearch, decimalSearch = ''] = searchString.split('.');

    // If the search string doesn't include a decimal point,
    // match it against the integer part of the row value and ignore the decimal part
    if (searchString.indexOf('.') === -1) {
        decimalPart = '';
        decimalSearch = '';
    }

    // Ignore anything after the first '#'
    if (decimalSearch.includes('#')) {
        decimalSearch = decimalSearch.slice(0, decimalSearch.indexOf('#') + 1);
    }

    // Replace the decimal wildcard '#' with a regex pattern for decimals
    const decimalWildcardPattern = decimalSearch.replace(/#/, ".*");

    // Replace the single-digit wildcard 'x' or 'X' in both integer and decimal parts
    const integerPattern = integerSearch.replace(/[xX]/g, "\\d");
    const decimalPattern = decimalWildcardPattern.replace(/[xX]/g, "\\d");

    // Create new RegExp objects with the combined patterns
    const integerRegex = new RegExp(`^${integerPattern}$`);
    const decimalRegex = new RegExp(`^${decimalPattern}$`);

    // Test the integer and decimal parts against the respective regex patterns
    return integerRegex.test(integerPart) && decimalRegex.test(decimalPart);
}


function matchExact(rowValue, searchString) {
    const parsedSearchValue = parseFloat(searchString);
    return rowValue === parsedSearchValue;
}
