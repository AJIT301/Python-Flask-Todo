document.addEventListener('DOMContentLoaded', function () {
    // Initialize scroll effects for feature sections
    initFeatureAnimations();
    // Initialize smooth scrolling
    initSmoothScrolling();
});

function initFeatureAnimations() {
    // Create intersection observer for feature sections
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                console.log('Animating section:', entry.target.id);
                animateFeatureSection(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all feature detail sections
    const featureSections = document.querySelectorAll('.feature-detail');
    featureSections.forEach(section => {
        observer.observe(section);
    });
}

function animateFeatureSection(section) {
    const container = section.querySelector('.feature-detail-container');
    const featureText = container.querySelector('.feature-text');
    const featureImage = container.querySelector('.feature-image');

    // Determine which element comes first in DOM (visual position)
    const children = Array.from(container.children);
    const textIndex = children.indexOf(featureText);
    const imageIndex = children.indexOf(featureImage);

    // Add initial animation classes based on position
    if (textIndex < imageIndex) {
        // Text comes first (left side) - text from left, image from right
        featureText.classList.add('slide-from-left');
        featureImage.classList.add('slide-from-right');
    } else {
        // Image comes first (left side) - image from left, text from right
        featureText.classList.add('slide-from-right');
        featureImage.classList.add('slide-from-left');
    }

    // Start animation after a small delay
    setTimeout(() => {
        featureText.classList.add('animated');
        setTimeout(() => {
            featureImage.classList.add('animated');
        }, 200);
    }, 100);
}

function initSmoothScrolling() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}