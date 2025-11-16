document.addEventListener('DOMContentLoaded', function() {
    const letterLinks = document.querySelectorAll('.letter-bar p');
    
    letterLinks.forEach(link => {
        link.addEventListener('click', function() {
            const letter = this.textContent.trim();
            const section = document.getElementById('letter-' + letter);
            
            if (section) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});