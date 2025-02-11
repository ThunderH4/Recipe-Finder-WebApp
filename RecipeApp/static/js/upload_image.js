// upload_image.js
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dragDropArea = document.getElementById('dragDropArea');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const imagePreview = document.getElementById('imagePreview');
    const clearImageBtn = document.getElementById('clearImageBtn');
    const processImageBtn = document.getElementById('processImageBtn');
    const continueBtn = document.getElementById('continueBtn');
    const tagsContainer = document.getElementById('tagsContainer');
    
    let detectedIngredients = [];
    let currentFile = null;

    // ======================
    // Event Listeners
    // ======================

    // Drag & Drop Handling
    dragDropArea.addEventListener('dragover', handleDragOver);
    dragDropArea.addEventListener('dragleave', handleDragLeave);
    dragDropArea.addEventListener('drop', handleDrop);

    // File Input Change
    fileInput.addEventListener('change', handleFileSelect);

    // Clear Image
    clearImageBtn.addEventListener('click', clearImage);

    // Process Image
    processImageBtn.addEventListener('click', processImage);

    // Continue to Manual Input
    continueBtn.addEventListener('click', handleContinue);

    // ======================
    // Core Functions
    // ======================

    function handleDragOver(e) {
        e.preventDefault();
        dragDropArea.classList.add('dragover');
    }

    function handleDragLeave() {
        dragDropArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        dragDropArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (validateImage(file)) {
            handleImage(file);
            fileInput.files = e.dataTransfer.files; // Sync with file input
        }
    }

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (validateImage(file)) {
            handleImage(file);
        }
    }

    function clearImage() {
        fileInput.value = '';
        previewImage.src = '';
        imagePreview.style.display = 'none';
        tagsContainer.innerHTML = '';
        detectedIngredients = [];
        continueBtn.disabled = true;
        currentFile = null;
    }

    async function processImage() {
        if (!currentFile) {
            alert('Please upload an image first.');
            return;
        }

        try {
            // Show processing state
            processImageBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            processImageBtn.disabled = true;

            // Send to Imagga API
            const formData = new FormData();
            formData.append('image', currentFile);

            const response = await fetch('/api/detect-ingredients', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Ingredient detection failed');
            }

            const data = await response.json();
            detectedIngredients = data.ingredients;
            
            if (detectedIngredients.length === 0) {
                throw new Error('No ingredients found in the image');
            }

            displayIngredients();
            continueBtn.disabled = false;

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            processImageBtn.innerHTML = '<i class="fas fa-magic"></i> Detect Ingredients';
            processImageBtn.disabled = false;
        }
    }

    function handleContinue() {
        if (detectedIngredients.length === 0) {
            alert('Please detect ingredients first');
            return;
        }
        
        // Store ingredients in sessionStorage
        sessionStorage.setItem('ingredients', JSON.stringify(detectedIngredients));
        
        // Redirect to manual input page
        window.location.href = document.getElementById('manualInputUrl').dataset.url;
    }

    // ======================
    // Helper Functions
    // ======================

    function validateImage(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!file) {
            alert('Please select an image file');
            return false;
        }

        if (!validTypes.includes(file.type)) {
            alert('Only JPG, PNG, and WEBP files are allowed');
            return false;
        }

        if (file.size > maxSize) {
            alert('File size must be less than 5MB');
            return false;
        }

        return true;
    }

    function handleImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            imagePreview.style.display = 'block';
            currentFile = file;
        };
        reader.readAsDataURL(file);
    }

    function displayIngredients() {
        tagsContainer.innerHTML = detectedIngredients.map(ingredient => `
            <div class="tag">
                ${ingredient}
                <span class="tag-remove" onclick="removeTag('${ingredient}')">&times;</span>
            </div>
        `).join('');
    }

    // Global function for tag removal
    window.removeTag = (ingredient) => {
        detectedIngredients = detectedIngredients.filter(item => item !== ingredient);
        displayIngredients();
        sessionStorage.setItem('ingredients', JSON.stringify(detectedIngredients));
    };
});