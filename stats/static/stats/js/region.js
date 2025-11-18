document.addEventListener('DOMContentLoaded', function() {
    const typewriterElement = document.getElementById('typewriter-search');
    const text = typewriterElement.textContent.trim(); 
    typewriterElement.textContent = ''; 
    let index = 0;

    function typeWriter() {
        if (index < text.length) {
            typewriterElement.innerHTML += text.charAt(index);
            typewriterElement.classList.add('typewriter-search');
            index++;
            setTimeout(typeWriter, 100);
        }
    }

    setTimeout(typeWriter, 300);
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