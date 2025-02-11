document.addEventListener('DOMContentLoaded', () => {
    // Clean up after animations
    setTimeout(() => {
        const subTitle = document.querySelector('.sub-title');
        if (subTitle) {
            subTitle.style.borderRight = 'none';
            subTitle.style.whiteSpace = 'normal';
        }
    }, 4000); // Total animation time (1000ms delay + 3500ms typing)
});