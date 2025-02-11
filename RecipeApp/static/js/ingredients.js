// ingredients.js
document.addEventListener('DOMContentLoaded', () => {
    const ingredientInput = document.getElementById('ingredientInput');
    const tagsContainer = document.getElementById('tagsContainer');
    const suggestionsDiv = document.getElementById('suggestions');
    const hiddenInput = document.getElementById('hiddenIngredients');
    let ingredients = JSON.parse(sessionStorage.getItem('ingredients') || '[]');

    // Initialize detected ingredients
    updateIngredientsDisplay();
    syncHiddenInput();

    // Fetch suggestions from Spoonacular API
    async function fetchSuggestions(query) {
        const API_KEY = '0ceb03c406e94244a2f5576a172c773d'; // 🔑 Replace with your key
        const url = `https://api.spoonacular.com/food/ingredients/autocomplete?query=${query}&number=5&apiKey=${API_KEY}`;

        try {
            const response = await fetch(url);
            const data = await response.json();
            return data.map(ing => ing.name.toLowerCase());
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            return [];
        }
    }

    // Handle input for suggestions
    ingredientInput.addEventListener('input', async (e) => {
        const value = e.target.value.trim().toLowerCase();
        suggestionsDiv.innerHTML = '';
        
        if (value.length > 1) {
            const filtered = await fetchSuggestions(value);
            showSuggestions(filtered.filter(ing => !ingredients.includes(ing)));
        } else {
            suggestionsDiv.classList.remove('visible');
        }
    });

    // Show suggestions
    function showSuggestions(items) {
        if (items.length > 0) {
            suggestionsDiv.classList.add('visible');
            suggestionsDiv.innerHTML = items.map(item => `
                <div class="suggestion-item">${item}</div>
            `).join('');
            
            document.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    addTag(item.textContent);
                    ingredientInput.value = '';
                    suggestionsDiv.classList.remove('visible');
                });
            });
        } else {
            suggestionsDiv.classList.remove('visible');
        }
    }

    // Add a new tag
    function addTag(ingredient) {
        if (!ingredients.includes(ingredient)) {
            ingredients.push(ingredient);
            updateIngredientsDisplay();
            syncHiddenInput();
        }
    }

    // Remove a tag
    window.removeTag = (ingredient) => {
        ingredients = ingredients.filter(ing => ing !== ingredient);
        updateIngredientsDisplay();
        syncHiddenInput();
    };

    // Update the visual display of ingredients
    function updateIngredientsDisplay() {
        tagsContainer.innerHTML = ingredients.map(ingredient => `
            <div class="tag">
                ${ingredient}
                <span class="tag-remove" onclick="removeTag('${ingredient}')">&times;</span>
            </div>
        `).join('');
    }

    // Sync ingredients with hidden input
    function syncHiddenInput() {
        if (hiddenInput) {
            hiddenInput.value = JSON.stringify(ingredients);
        }
    }

    // Handle form submission
    document.getElementById('submitIngredients').addEventListener('click', (e) => {
        e.preventDefault();
        
        if (ingredients.length === 0) {
            alert('Please add at least one ingredient');
            return;
        }

        // Create hidden input to send ingredients
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'ingredients';
        input.value = JSON.stringify(ingredients);
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.input-wrapper')) {
            suggestionsDiv.classList.remove('visible');
        }
    });
});