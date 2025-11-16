document.addEventListener('DOMContentLoaded', function() {
    const letterLinks = document.querySelectorAll('.letter-bar p');
    
    letterLinks.forEach(letter => {
        letter.addEventListener('click', function(e) {
            e.preventDefault();
            const letterText = this.textContent.trim();
            const targetSection = document.querySelector(`#letter\\=${letterText}`);
            
            if (targetSection) {
                targetSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
        
        letter.style.cursor = 'pointer';
    });
    
    letterLinks.forEach(letter => {
        letter.addEventListener('mouseenter', function() {
            this.style.opacity = '0.7';
        });
        
        letter.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
    });
});