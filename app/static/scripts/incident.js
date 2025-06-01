let uploadedFiles = [];

// Handle file upload
function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    
    files.forEach(file => {
        if (file.size > 10 * 1024 * 1024) {
            alert(`File ${file.name} is too large. Maximum size is 10MB.`);
            return;
        }
        
        uploadedFiles.push(file);
        displayUploadedFile(file);
    });
}

// Display uploaded file
function displayUploadedFile(file) {
    const container = document.getElementById('uploadedImages');
    const fileDiv = document.createElement('div');
    fileDiv.className = 'uploaded-image';
    
    if (file.type.startsWith('image/')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        fileDiv.appendChild(img);
    } else {
        const fileIcon = document.createElement('div');
        fileIcon.style.cssText = `
            width: 100%;
            height: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #f3f4f6;
            color: #6b7280;
            font-size: 0.8rem;
            text-align: center;
            padding: 10px;
        `;
        fileIcon.innerHTML = `
            <div style="font-size: 1.5rem; margin-bottom: 5px;">📄</div>
            <div>${file.name}</div>
        `;
        fileDiv.appendChild(fileIcon);
    }
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-image';
    removeBtn.innerHTML = '×';
    removeBtn.onclick = () => removeFile(file, fileDiv);
    
    fileDiv.appendChild(removeBtn);
    container.appendChild(fileDiv);
}

// Remove uploaded file
function removeFile(file, element) {
    uploadedFiles = uploadedFiles.filter(f => f !== file);
    element.remove();
}

// Drag and drop functionality
const uploadArea = document.querySelector('.image-upload-area');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    files.forEach(file => {
        if (file.size <= 10 * 1024 * 1024) {
            uploadedFiles.push(file);
            displayUploadedFile(file);
        } else {
            alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        }
    });
});


document.querySelector('.btn-primary').addEventListener('click', function() {
    localStorage.removeItem('incidentDraft');
});
// Save draft functionality
document.querySelector('.btn-secondary').addEventListener('click', function() {
    // Get form data
    const formData = new FormData();
    formData.append('incidentType', document.getElementById('incidentType').value);
    formData.append('description', document.getElementById('description').value);
    formData.append('location', document.getElementById('location').value);
    formData.append('dateIncident', document.getElementById('dateIncident').value);
    formData.append('contactName', document.getElementById('contactName').value);
    formData.append('contactEmail', document.getElementById('contactEmail').value);
    formData.append('contactPhone', document.getElementById('contactPhone').value);
    
    // In a real application, this would save to a server or localStorage
    localStorage.setItem('incidentDraft', JSON.stringify(formData));
    alert('Draft saved in browser!');
});
window.addEventListener('DOMContentLoaded', () => {
    const savedData = JSON.parse(localStorage.getItem('incidentDraft'));
    if (savedData) {
        document.getElementById('incidentType').value = savedData.incidentType || "";
        document.getElementById('description').value = savedData.description || "";
        document.getElementById('location').value = savedData.location || "";
        document.getElementById('dateIncident').value = savedData.incidentDate || "";
        document.getElementById('contactName').value = savedData.fullName || "";
        document.getElementById('contactEmail').value = savedData.email || "";
        document.getElementById('contactPhone').value = savedData.contactPhone || "";
    }
});

// Handling the image file upload input
function displayUploadedFile(file) {
    const container = document.getElementById('uploadedImages');
    const fileDiv = document.createElement('div');
    fileDiv.className = 'uploaded-image';
    
    if (file.type.startsWith('image/')) {
        // Handle image files
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.onload = () => URL.revokeObjectURL(img.src); // Clean up
        fileDiv.appendChild(img);
    } else {
        // Handle other file types (PDF, DOC, etc)
        const preview = document.createElement('div');
        preview.className = 'file-preview';
        
        // Determine icon based on file type
        let icon = '📄';
        if (file.type.includes('pdf')) icon = '📕';
        if (file.type.includes('word')) icon = '📝';
        
        preview.innerHTML = `
            <div class="file-preview-icon">${icon}</div>
            <div class="file-preview-name">${file.name}</div>
        `;
        fileDiv.appendChild(preview);
    }
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-image';
    removeBtn.innerHTML = '×';
    removeBtn.onclick = () => removeFile(file, fileDiv);
    
    fileDiv.appendChild(removeBtn);
    container.appendChild(fileDiv);
}

// Add visual feedback for drag and drop
function addDragAndDropStyles() {
    const uploadArea = document.querySelector('.image-upload-area');
    
    uploadArea.addEventListener('dragenter', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#1e3a8a';
        uploadArea.style.backgroundColor = '#f0f4ff';
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#1e3a8a';
        uploadArea.style.backgroundColor = '#f0f4ff';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#d1d5db';
        uploadArea.style.backgroundColor = '#f9fafb';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#d1d5db';
        uploadArea.style.backgroundColor = '#f9fafb';
        
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => {
            if (file.size <= 10 * 1024 * 1024) {
                uploadedFiles.push(file);
                displayUploadedFile(file);
            } else {
                alert(`File ${file.name} is too large. Maximum size is 10MB.`);
            }
        });
    });
}

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', addDragAndDropStyles);