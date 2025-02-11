document.addEventListener('DOMContentLoaded', () => {
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach(notification => {
        // Remove CSS initial animation
        notification.style.animation = 'slideIn 0.5s ease-out';
        
        // Set up removal after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s ease forwards';
            
            // Remove element after animation completes
            setTimeout(() => {
                notification.remove();
            }, 500); // Matches animation duration
        }, 3000); // 3 seconds total visibility
    });
});