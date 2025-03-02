document.addEventListener('DOMContentLoaded', function() {
    // Canvas setup
    const canvas = document.getElementById('vector-canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size to match window
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Vector particles
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 1.5 + 0.5;
            this.speed = Math.random() * 0.5 + 0.2;
            this.direction = Math.random() * Math.PI * 2;
            this.color = this.getRandomColor();
            this.life = Math.random() * 100 + 100;
            this.connections = [];
        }

        getRandomColor() {
            const colors = [
                'rgba(0, 191, 255, 0.8)', // Primary blue
                'rgba(0, 119, 204, 0.7)', // Secondary blue
                'rgba(119, 0, 255, 0.6)', // Accent purple
                'rgba(0, 255, 170, 0.5)'  // Success teal
            ];
            return colors[Math.floor(Math.random() * colors.length)];
        }

        update() {
            // Move particle
            this.x += Math.cos(this.direction) * this.speed;
            this.y += Math.sin(this.direction) * this.speed;

            // Slightly change direction
            this.direction += (Math.random() - 0.5) * 0.05;

            // Decrease life
            this.life -= 0.2;

            // Reset if out of bounds or dead
            if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life <= 0) {
                this.resetParticle();
            }
        }

        resetParticle() {
            // Reset position to a random edge of the screen
            const edge = Math.floor(Math.random() * 4);
            if (edge === 0) { // Top edge
                this.x = Math.random() * canvas.width;
                this.y = 0;
                this.direction = Math.random() * Math.PI + Math.PI/2; // Down direction
            } else if (edge === 1) { // Right edge
                this.x = canvas.width;
                this.y = Math.random() * canvas.height;
                this.direction = Math.random() * Math.PI + Math.PI; // Left direction
            } else if (edge === 2) { // Bottom edge
                this.x = Math.random() * canvas.width;
                this.y = canvas.height;
                this.direction = Math.random() * Math.PI + Math.PI*3/2; // Up direction
            } else { // Left edge
                this.x = 0;
                this.y = Math.random() * canvas.height;
                this.direction = Math.random() * Math.PI; // Right direction
            }

            this.size = Math.random() * 1.5 + 0.5;
            this.speed = Math.random() * 0.5 + 0.2;
            this.color = this.getRandomColor();
            this.life = Math.random() * 100 + 100;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    // Create particles
    const particleCount = Math.min(Math.floor(window.innerWidth * window.innerHeight / 15000), 100);
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // Calculate distance between two particles
    function getDistance(p1, p2) {
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Animation loop
    function animate() {
        // Clear canvas with slight fade for trail effect
        ctx.fillStyle = 'rgba(10, 10, 20, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Update and draw particles
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            // Find connections
            particles[i].connections = [];
            for (let j = i + 1; j < particles.length; j++) {
                const distance = getDistance(particles[i], particles[j]);
                const maxDistance = 150; // Maximum distance for connection

                if (distance < maxDistance) {
                    particles[i].connections.push({
                        particle: particles[j],
                        opacity: 1 - (distance / maxDistance)
                    });
                }
            }

            // Draw connections
            for (const conn of particles[i].connections) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(conn.particle.x, conn.particle.y);

                // Get color components from the particle's color
                const color = particles[i].color;
                const rgbaMatch = color.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);

                if (rgbaMatch) {
                    const r = rgbaMatch[1];
                    const g = rgbaMatch[2];
                    const b = rgbaMatch[3];
                    const opacity = conn.opacity * 0.4; // Reduce opacity for lines

                    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${opacity})`;
                    ctx.lineWidth = conn.opacity * 0.8;
                    ctx.stroke();
                }
            }
        }

        // Pulse effect for glow
        const time = Date.now() * 0.001;
        const pulse = Math.sin(time) * 0.5 + 0.5;

        // Add some random glow spots
        const glowCount = 3;
        for (let i = 0; i < glowCount; i++) {
            const size = Math.random() * 100 + 50;
            const x = Math.sin(time * (i + 1) * 0.3) * canvas.width * 0.4 + canvas.width * 0.5;
            const y = Math.cos(time * (i + 1) * 0.2) * canvas.height * 0.4 + canvas.height * 0.5;

            // Create radial gradient for glow
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, size);
            gradient.addColorStop(0, `rgba(0, 191, 255, ${0.1 * pulse})`);
            gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }

        requestAnimationFrame(animate);
    }

    animate();

    // Handle visibility change to improve performance
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden, clear canvas to save resources
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    });
});