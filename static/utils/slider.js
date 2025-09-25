// Initialize all sliders on the page
document.addEventListener('DOMContentLoaded', function() {
    // Handle regular sliders
    const sliders = document.querySelectorAll('.slider');
    sliders.forEach((slider) => {
        initSlider(slider, '.slide', '.dot', '.prev', '.next');
    });

    // Handle security sliders
    const securitySliders = document.querySelectorAll('.security-slider');
    securitySliders.forEach((slider) => {
        initSlider(slider, '.security-slide', '.security-dot', '.security-prev', '.security-next');
    });
});

function initSlider(slider, slideSelector, dotSelector, prevSelector, nextSelector) {
    let slideIndex = 1;
    const slides = slider.querySelectorAll(slideSelector);
    const dots = slider.querySelectorAll(dotSelector);
    const prevBtn = slider.querySelector(prevSelector);
    const nextBtn = slider.querySelector(nextSelector);

    function showSlides(n) {
        if (n > slides.length) {slideIndex = 1}
        if (n < 1) {slideIndex = slides.length}
        slides.forEach(slide => slide.style.display = "none");
        dots.forEach(dot => dot.className = dot.className.replace(" active", ""));
        slides[slideIndex-1].style.display = "block";
        dots[slideIndex-1].className += " active";
    }

    function plusSlides(n) {
        showSlides(slideIndex += n);
    }

    function currentSlide(n) {
        showSlides(slideIndex = n);
    }

    // Attach event listeners for this slider
    if (prevBtn) prevBtn.addEventListener('click', () => plusSlides(-1));
    if (nextBtn) nextBtn.addEventListener('click', () => plusSlides(1));
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => currentSlide(index + 1));
    });

    // Auto slide for this slider
    function autoShowSlides() {
        slideIndex++;
        if (slideIndex > slides.length) {slideIndex = 1}
        showSlides(slideIndex);
        setTimeout(autoShowSlides, 4000);
    }

    // Start auto slide
    showSlides(slideIndex);
    setTimeout(autoShowSlides, 4000);
}
