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

    const canvas = document.getElementById('dots-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const spacing = 40;
    const dotRadius = 2;
    const dots = [];

    class Dot {
        constructor(x, y) {
            this.baseX = x;
            this.baseY = y;
            this.x = x;
            this.y = y;
            this.vx = 0;
            this.vy = 0;
        }

        update() {
            this.vx += (this.baseX - this.x) * 0.05;
            this.vy += (this.baseY - this.y) * 0.05;
            this.vx *= 0.85;
            this.vy *= 0.85;

            this.x += this.vx;
            this.y += this.vy;
        }

        draw() {
            const dx = this.x - this.baseX;
            const dy = this.y - this.baseY;
            const displacement = Math.sqrt(dx * dx + dy * dy);
            const intensity = Math.max(0, 1 - displacement / 100);
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, dotRadius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(86, 176, 102, ${0.3 + intensity * 0.4})`;
            ctx.fill();
        }
    }

    function initDots() {
        dots.length = 0;
        
        const cols = Math.floor(canvas.width / spacing);
        const rows = Math.floor(canvas.height / spacing);
        
        const offsetX = (canvas.width - (cols - 1) * spacing) / 2;
        const offsetY = (canvas.height - (rows - 1) * spacing) / 2;
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = offsetX + col * spacing;
                const y = offsetY + row * spacing;
                dots.push(new Dot(x, y));
            }
        }
    }

    initDots();

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        dots.forEach(dot => {
            dot.update();
            dot.draw();
        });

        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initDots();
    });

    animate();
});