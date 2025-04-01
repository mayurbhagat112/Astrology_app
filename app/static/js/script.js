// Wait for the DOM to load
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chart-form');
    const loadingIndicator = document.getElementById('loading');
    const chartImage = document.getElementById('chart-image');
    const summaryElement = document.getElementById('summary');
    const positionsElement = document.getElementById('positions');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent form submission
        const dateTime = document.getElementById('date-time').value;

        // Show loading spinner
        loadingIndicator.style.display = 'block';

        try {
            // Send a POST request to the server
            const response = await fetch('/get_chart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date_time: dateTime }),
            });

            const result = await response.json();
            loadingIndicator.style.display = 'none'; // Hide loading spinner

            // Update chart image if successful
            if (result.chart) {
                chartImage.src = 'data:image/png;base64,' + result.chart;
                chartImage.style.display = 'block';
            } else {
                chartImage.style.display = 'none';
            }

            // Update summary text
            if (result.summary) {
                summaryElement.innerText = result.summary;
            } else {
                summaryElement.innerText = 'No summary available.';
            }

            // Update planetary positions
            if (result.positions) {
                positionsElement.innerText = JSON.stringify(result.positions, null, 2);
            } else {
                positionsElement.innerText = 'No planetary positions available.';
            }

            // Handle errors
            if (result.error) {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            loadingIndicator.style.display = 'none'; // Hide loading spinner
            alert('An error occurred while generating the chart. Please try again.');
            console.error('Error:', error);
        }
    });
});
