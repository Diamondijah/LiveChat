let currentSlide = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.carousel-item');
    const slideWidth = slides[0].clientWidth; // Largeur de la première image (supposée fixe)
    const totalSlides = slides.length;

    if (index >= totalSlides) {
        currentSlide = 0;
    }
    if (index < 0) {
        currentSlide = totalSlides - 1;
    }

    slides.forEach((slide, i) => {
        slide.style.transform = `translateX(-${currentSlide * slideWidth}px)`;
    });
}

function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
    setInterval(nextSlide, 10000); // Change slide every 5 seconds
});
