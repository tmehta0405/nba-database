document.addEventListener('DOMContentLoaded', function() {
    const text = "DATABALL";
    const typewriterElement = document.getElementById('typewriter-text');
    let index = 0;

    function typeWriter() {
        if (index < text.length) {
            typewriterElement.innerHTML += text.charAt(index);
            typewriterElement.classList.add('typewriter');
            index++;
            setTimeout(typeWriter, 150);
        } 
    }

    setTimeout(typeWriter, 500);
});