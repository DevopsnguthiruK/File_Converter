document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const browseFiles = document.getElementById('browseFiles');
    const filePreview = document.getElementById('filePreview');
    const previewTable = document.getElementById('previewTable');
    const convertBtn = document.getElementById('convertBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // Add event listener for the browse files button
    browseFiles.addEventListener('click', () => {
        fileInput.click();
    });

    // Add event listener for the file input change event
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Drag and Drop Functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropzone.classList.add('border-blue-400', 'bg-blue-50');
    }

    function unhighlight() {
        dropzone.classList.remove('border-blue-400', 'bg-blue-50');
    }

    dropzone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        // Assign the dropped file to the file input element
        if (files.length > 0) {
            // Create a DataTransfer object and add the file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            
            // Set the file input's files property
            fileInput.files = dataTransfer.files;
        }
        
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (['application/json', 'text/xml', 'application/xml'].includes(file.type)) {
                previewFile(file);
            } else {
                alert('Please upload a JSON or XML file');
            }
        }
    }

    function previewFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            try {
                let data;
                if (file.type.includes('json')) {
                    data = JSON.parse(content);
                } else {
                    const parser = new DOMParser();
                    const xmlDoc = parser.parseFromString(content, "text/xml");
                    data = xmlToJson(xmlDoc);
                }

                // Limit to 10 records
                const limitedData = Array.isArray(data) ? data.slice(0, 3) : [data];
                renderPreview(limitedData);
            } catch (error) {
                console.error('Preview error:', error);
                alert('Error parsing file');
            }
        };
        reader.readAsText(file);
    }

    function xmlToJson(xml) {
        // Get the root element name
        const rootName = xml.documentElement.nodeName;
        
        // Find repeated elements that form a collection
        const childElements = Array.from(xml.documentElement.children);
        
        // Check if we have repeating elements (like CTR elements in your file)
        if (childElements.length > 0) {
            const firstChildName = childElements[0].nodeName;
            
            // If we have multiple elements with the same name, treat as collection
            if (childElements.filter(el => el.nodeName === firstChildName).length > 1) {
                return childElements.map(item => {
                    const obj = {};
                    // Extract all child elements of the item
                    Array.from(item.children).forEach(child => {
                        obj[child.nodeName] = child.textContent;
                        
                        // Handle attributes if they exist
                        if (child.attributes.length > 0) {
                            for (let i = 0; i < child.attributes.length; i++) {
                                const attr = child.attributes[i];
                                obj[`${child.nodeName}_${attr.name}`] = attr.value;
                            }
                        }
                    });
                    return obj;
                });
            }
        }
        
        // Fallback for simpler structures
        const obj = {};
        for (let child of xml.documentElement.children) {
            obj[child.nodeName] = Object.fromEntries(
                Array.from(child.children).map(el => [el.nodeName, el.textContent])
            );
        }
        return [obj];
    }

    function renderPreview(data) {
        filePreview.classList.remove('hidden');
        
        if (data.length === 0) {
            previewTable.innerHTML = '<p class="text-gray-500">No data to preview</p>';
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

        // Table data
        data.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] || 'N/A';
                td.className = 'border p-2';
                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        previewTable.innerHTML = '';
        previewTable.appendChild(table);
    }

    convertBtn.addEventListener('click', () => {
        const fileToUpload = fileInput.files[0];
        if (!fileToUpload) {
            alert('Please select a file to convert');
            return;
        }
        
        // Show loading state
        convertBtn.disabled = true;
        convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Converting...';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', fileToUpload);
        
        // Send to server for conversion
        fetch('/api/converter/convert', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Conversion failed');
            }
            return response.json();
        })
        .then(data => {
            // Save conversion result and preview data to localStorage
            localStorage.setItem('conversionResult', JSON.stringify(data.result));
            
            // Get preview data from the previewTable
            const previewData = extractPreviewData();
            if (previewData.length > 0) {
                const resultWithPreview = JSON.parse(localStorage.getItem('conversionResult'));
                resultWithPreview.preview_data = previewData;
                localStorage.setItem('conversionResult', JSON.stringify(resultWithPreview));
            }
            
            // Navigate to conversion result page
            window.location.href = '/conversion-result';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Conversion failed: ' + error.message);
            // Reset button
            convertBtn.disabled = false;
            convertBtn.innerHTML = 'Convert File';
        });
        
        // Function to extract preview data from the table
        function extractPreviewData() {
            const table = previewTable.querySelector('table');
            if (!table) return [];
            
            const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent);
            const rows = Array.from(table.querySelectorAll('tr')).slice(1); // Skip header row
            
            return rows.map(row => {
                const cells = Array.from(row.querySelectorAll('td'));
                return Object.fromEntries(
                    headers.map((header, index) => [header, cells[index]?.textContent || ''])
                );
            });
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = '/';
    });
});