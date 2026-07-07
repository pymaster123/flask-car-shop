document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll('.gallery-image-wrap');

    cards.forEach(function (card) {
        var overlay = card.querySelector('.gallery-description');
        if (!overlay) {
            return;
        }

        var description = card.getAttribute('data-description') || '';
        overlay.textContent = description;

        // trigger the different events to show/hide the overlay
        card.addEventListener('mouseenter', function () {
            overlay.classList.add('is-visible');
        });

        card.addEventListener('mouseleave', function () {
            overlay.classList.remove('is-visible');
        });

        card.addEventListener('focusin', function () {
            overlay.classList.add('is-visible');
        });

        card.addEventListener('focusout', function () {
            overlay.classList.remove('is-visible');
        });
    });
});