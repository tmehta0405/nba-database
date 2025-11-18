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
});