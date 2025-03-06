// conversion-result.js
document.addEventListener('DOMContentLoaded', () => {
    const downloadCsvBtn = document.getElementById('downloadCsv');
    const downloadExcelBtn = document.getElementById('downloadExcel');
    const resultPreview = document.getElementById('resultPreview');
    const conversionDetails = document.getElementById('conversionDetails');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Get conversion result data from localStorage or session
    const conversionResult = JSON.parse(localStorage.getItem('conversionResult') || '{}');
    
    // Display conversion details
    if (conversionResult.original_file) {
        const { original_filename, file_size } = conversionResult.original_file;
        const { total_rows, total_columns } = conversionResult.conversion_result || {};
        
        const fileSizeKB = Math.round(file_size / 1024);
        
        conversionDetails.innerHTML = `
            Original file: <strong>${original_filename}</strong><br>
            File size: <strong>${fileSizeKB} KB</strong><br>
            Rows: <strong>${total_rows || 'N/A'}</strong><br>
            Columns: <strong>${total_columns || 'N/A'}</strong>
        `;
    }
    
    // Set up download buttons
    if (conversionResult.conversion_result) {
        const { csv_path, excel_path } = conversionResult.conversion_result;
        
        downloadCsvBtn.addEventListener('click', () => {
            const token = localStorage.getItem('token');
            
            // Make an authenticated fetch request
            fetch(`/api/converter/download?file=${encodeURIComponent(csv_path)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Download failed with status: ' + response.status);
                }
                return response.blob();
            })
            .then(blob => {
                // Create a temporary download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                // Extract filename from path
                const filename = csv_path.split('\\').pop().split('/').pop();
                a.download = filename;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Download error:', error);
                alert('Download failed. Please try again.');
            });
        });
        
        downloadExcelBtn.addEventListener('click', () => {
            const token = localStorage.getItem('token');
            
            // Make an authenticated fetch request
            fetch(`/api/converter/download?file=${encodeURIComponent(excel_path)}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Download failed with status: ' + response.status);
                }
                return response.blob();
            })
            .then(blob => {
                // Create a temporary download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                // Extract filename from path
                const filename = excel_path.split('\\').pop().split('/').pop();
                a.download = filename;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            })
            .catch(error => {
                console.error('Download error:', error);
                alert('Download failed. Please try again.');
            });
        });
    } else {
        // Disable buttons if no conversion result
        downloadCsvBtn.disabled = true;
        downloadCsvBtn.classList.add('bg-gray-400');
        downloadExcelBtn.disabled = true;
        downloadExcelBtn.classList.add('bg-gray-400');
    }
    
    // Load preview data
    if (conversionResult.preview_data) {
        renderPreview(conversionResult.preview_data);
    } else {
        resultPreview.innerHTML = '<p class="text-gray-500">No preview data available</p>';
    }
    
    function renderPreview(data) {
        if (data.length === 0) {
            resultPreview.innerHTML = '<p class="text-gray-500">No data to preview</p>';
            return;
        }

        // Create table
        const table = document.createElement('table');
        table.className = 'w-full border-collapse';

        // Table headers
        const headers = Object.keys(data[0]);
        const headerRow = document.createElement('tr');
        headerRow.className = 'bg-blue-100';
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            th.className = 'border p-2 text-left';
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        // Table data (limit to 10 rows for preview)
        const previewData = data.slice(0, 10);
        previewData.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] || 'N/A';
                td.className = 'border p-2';
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        resultPreview.innerHTML = '';
        resultPreview.appendChild(table);
    }
    
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('conversionResult');
        window.location.href = '/';
    });
});