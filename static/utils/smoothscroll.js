document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
        const href = link.getAttribute('href');

        // Only handle internal anchor links, not external URLs
        if (href.startsWith('#')) {
            e.preventDefault();

            const targetId = href.slice(1);
            const targetElement = document.getElementById(targetId);

            if (!targetElement) {
                console.error('Target element not found:', targetId);
                return;
            }

            const navbarHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = targetElement.offsetTop - navbarHeight;

            // Enhanced smooth scrolling with fallback
            if ('scrollBehavior' in document.documentElement.style) {
                // Modern browsers - use scrollTo with smooth behavior
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            } else {
                // Fallback for older browsers - animated scroll
                smoothScrollTo(targetPosition, 800);
            }
        }
    });
});

// Fallback smooth scroll function for older browsers
function smoothScrollTo(targetY, duration) {
    const startY = window.pageYOffset;
    const difference = targetY - startY;
    const startTime = performance.now();

    function step() {
        const progress = (performance.now() - startTime) / duration;
        const amount = easeInOutCubic(progress);
        window.scrollTo(0, startY + (difference * amount));

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

// Easing function for smooth animation
function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}
