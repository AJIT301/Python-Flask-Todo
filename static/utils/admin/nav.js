//nav bar effect script.
document.addEventListener('DOMContentLoaded', function () {
    const navWrapper = document.querySelector('.dashboard-nav-wrapper');
    let lastScrollY = window.scrollY;
    let scrollTimer = null;

    if (navWrapper) {
        function handleScroll() {
            const currentScrollY = window.scrollY;
            const scrollDelta = currentScrollY - lastScrollY;

            // More sensitive detection
            if (Math.abs(scrollDelta) > 1) { // Reduced from 2 to 1
                // Immediate sharp displacement
                navWrapper.style.transition = 'none';

                //Sharper displacement calculation
                const displacement = Math.min(Math.abs(scrollDelta) * 5.0, 50); // Increased multiplier and max

                if (scrollDelta > 0) {
                    // Scrolling down - sharper push up
                    navWrapper.style.transform = `translateY(${-displacement}px)`;
                } else {
                    // Scrolling up - sharper push down
                    navWrapper.style.transform = `translateY(${displacement}px)`;
                }

                // Faster bounce back
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(() => {
                    navWrapper.style.transition = 'transform 0.3s cubic-bezier(0.3, -0.8, 0.3, 1.8)'; // Sharper easing
                    navWrapper.style.transform = 'translateY(0)';
                }, 100); // Reduced delay from 30 to 10ms
            }

            lastScrollY = currentScrollY;
        }

        window.addEventListener('scroll', handleScroll, { passive: true });
    }
});
