document.addEventListener('DOMContentLoaded', function() {
    const promptForm = document.getElementById('prompt-form');
    const sqlQuery = document.getElementById('sql-query');
    const executeBtn = document.getElementById('execute-btn');
    const copyBtn = document.getElementById('copy-btn');
    const resultsTable = document.getElementById('results-table');
    const tableHead = document.getElementById('table-head');
    const tableBody = document.getElementById('table-body');
    const messageBox = document.getElementById('message-box');
    const loadingIndicator = document.getElementById('loading');

    let currentQuery = '';

    // Handle form submission to generate SQL query
    promptForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(promptForm);
        const userPrompt = formData.get('prompt');

        if (!userPrompt) return;

        // Reset UI
        resetResults();
        showMessage('', '');
        sqlQuery.textContent = 'Generating query...';
        executeBtn.disabled = true;
        copyBtn.disabled = true;

        // Send request to generate SQL query
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentQuery = data.query;
                sqlQuery.textContent = data.query;
                executeBtn.disabled = false;
                copyBtn.disabled = false;
            } else {
                showMessage('Error generating query: ' + data.message, 'error');
                sqlQuery.textContent = '-- Failed to generate query';
            }
        })
        .catch(error => {
            showMessage('Network error: ' + error.message, 'error');
            sqlQuery.textContent = '-- Failed to generate query';
        });
    });

    // Handle execute button click
    executeBtn.addEventListener('click', function() {
        if (!currentQuery) return;

        // Reset results and show loading
        resetResults();
        loadingIndicator.classList.remove('hidden');

        // Create form data with the query
        const formData = new FormData();
        formData.append('query', currentQuery);

        // Send request to execute SQL query
        fetch('/execute', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');

            if (data.status === 'success') {
                if (data.results && data.results.length > 0) {
                    // If we have results, display them in the table
                    displayResults(data.results);
                } else {
                    // Show success message for non-SELECT queries
                    showMessage('Query executed successfully with no results to display.', 'success');
                }
            } else {
                showMessage(data.message, 'error');
            }
        })
        .catch(error => {
            loadingIndicator.classList.add('hidden');
            showMessage('Network error: ' + error.message, 'error');
        });
    });

    // Handle copy button click
    copyBtn.addEventListener('click', function() {
        if (!currentQuery) return;

        navigator.clipboard.writeText(currentQuery)
            .then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                showMessage('Failed to copy: ' + err.message, 'error');
            });
    });

    // Function to display results in the table
    function displayResults(results) {
        if (!results || results.length === 0) return;

        // Check if the first result has a message property (non-SELECT query result)
        if (results[0].message) {
            showMessage(results[0].message, 'success');
            return;
        }

        // Get column names from the first result
        const columns = Object.keys(results[0]);

        // Create table header
        let headerRow = document.createElement('tr');
        columns.forEach(column => {
            let th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        tableHead.appendChild(headerRow);

        // Create table rows for each result
        results.forEach(result => {
            let row = document.createElement('tr');
            columns.forEach(column => {
                let td = document.createElement('td');
                td.textContent = result[column] !== null ? result[column] : 'NULL';
                row.appendChild(td);
            });
            tableBody.appendChild(row);
        });

        // Show the table
        resultsTable.classList.remove('hidden');
    }

    // Function to show a message
    function showMessage(message, type) {
        if (!message) {
            messageBox.innerHTML = '';
            messageBox.className = '';
            return;
        }

        messageBox.textContent = message;
        messageBox.className = type === 'error' ? 'error-message' : 'success-message';
    }

    // Function to reset the results area
    function resetResults() {
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';
        resultsTable.classList.add('hidden');
        messageBox.innerHTML = '';
        messageBox.className = '';
    }
});