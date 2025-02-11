document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('preferencesForm');

    // ===== Initialize Saved Preference Card Hover =====
    function initSavedPrefHover() {
        const savedPrefCards = document.querySelectorAll('.saved-preferences-grid .pref-card');

        savedPrefCards.forEach(card => {
            // Desktop hover
            card.addEventListener('mouseenter', () => {
                savedPrefCards.forEach(c => c.classList.remove('hovered')); // Clear others
                card.classList.add('hovered');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hovered');
            });

            // Mobile touch support
            card.addEventListener('touchstart', (e) => {
                e.preventDefault();
                savedPrefCards.forEach(c => c.classList.remove('hovered')); // Clear others
                card.classList.toggle('hovered');
            });
        });
    }

    // ===== Initialize Delete Buttons =====
    function initDeleteButtons() {
        document.querySelectorAll('.pref-card .remove-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation(); // Prevent card click
                const card = btn.closest('.pref-card');
                if (confirm('Are you sure you want to delete this preference?')) {
                    try {
                        const response = await fetch(`/api/delete-preference/${card.dataset.prefId}`, {
                            method: 'DELETE'
                        });
                        if (response.ok) card.remove();
                    } catch (error) {
                        console.error('Delete error:', error);
                    }
                }
            });
        });
    }

    // Handle "Use This" button clicks
    document.querySelectorAll('.use-pref-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const prefId = this.dataset.prefId;
            const useButton = this;
            
            // Add loading state
            useButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            useButton.disabled = true;

            try {
                const response = await fetch(`/api/load-preference/${prefId}`);
                
                if (response.ok) {
                    // Redirect to recommendations after successful load
                    window.location.href = "/recommendations";
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.error || 'Failed to load preference'}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while loading the preference');
            } finally {
                // Reset button state
                useButton.innerHTML = '<i class="fas fa-arrow-right"></i> Use This';
                useButton.disabled = false;
            }
        });
    });

    // ===== Form Submission Handler =====
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Collect form data
        const formData = {
            save_preference: document.getElementById('savePreference').checked,
            preference_name: document.getElementById('preferenceName').value.trim(),
            difficulty: document.querySelector('.difficulty-card.selected')?.dataset.difficulty || '',
            max_time: document.querySelector('.time-option.selected')?.dataset.time || '',
            diet: document.querySelector('[name="diet"]:checked')?.value || '',
            allergies: Array.from(document.querySelectorAll('.allergy-pill.selected'))
                        .map(pill => pill.dataset.allergy)
        };

        // Validation
        if (formData.save_preference && !formData.preference_name) {
            document.getElementById('validationModal').style.display = 'flex';
            return;
        }

        // Send to backend
        try {
            const response = await fetch('/save-preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                window.location.href = '/recommendations';
            } else {
                console.error('Failed to save preferences');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // ===== Initialize All Functionality =====
    initSavedPrefHover(); // Hover effects for saved preference cards
    initDeleteButtons();  // Delete button functionality

    // Difficulty cards
    document.querySelectorAll('.difficulty-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
        });
    });

    // Time picker
    document.querySelectorAll('.time-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.time-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
        });
    });

    // Allergy pills
    document.querySelectorAll('.allergy-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            pill.classList.toggle('selected');
        });
    });
});

// ===== Modal Handling =====
window.closeModal = () => {
    document.getElementById('validationModal').style.display = 'none';
}

