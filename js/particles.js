/* ========================================================
   CANVAS DE PARTÍCULAS E CONEXÕES EM REDE (CETAM THEME)
   ======================================================== */
(function() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width, height;
    let particles = [];

    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.7;
            this.vy = (Math.random() - 0.5) * 0.7;
            this.radius = Math.random() * 2 + 1;
            
            // Cores oficiais CETAM (Verde Amazônia, Azul Céu, Ouro)
            const colors = [
                'rgba(0, 179, 84, ',   // CETAM Green
                'rgba(56, 189, 248, ',  // Cyan/Blue
                'rgba(255, 184, 28, '   // Gold
            ];
            this.baseColor = colors[Math.floor(Math.random() * colors.length)];
            this.alpha = Math.random() * 0.5 + 0.2;
            this.pulseSpeed = Math.random() * 0.02 + 0.008;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            this.alpha += Math.sin(Date.now() * this.pulseSpeed) * 0.01;
            if (this.alpha < 0.1) this.alpha = 0.1;
            if (this.alpha > 0.7) this.alpha = 0.7;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.baseColor + this.alpha + ')';
            ctx.shadowBlur = 10;
            ctx.shadowColor = this.baseColor + '0.8)';
            ctx.fill();
        }
    }

    // Densidade balanceada de partículas
    const count = Math.min(Math.floor((window.innerWidth * window.innerHeight) / 15000), 70);
    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Traçar linhas de conexão entre nós próximos
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 125) {
                    const lineAlpha = (1 - dist / 125) * 0.16;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 179, 84, ${lineAlpha})`;
                    ctx.lineWidth = 0.7;
                    ctx.stroke();
                }
            }
        }

        particles.forEach(p => {
            p.update();
            p.draw();
        });

        requestAnimationFrame(animate);
    }

    animate();
})();
