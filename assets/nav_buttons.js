document.addEventListener('DOMContentLoaded', (event) => {
    document.body.addEventListener('click', function(e) {
        let clickedElement = e.target;
        if (!clickedElement.classList.contains('nav-link')) {
            let navButtons = document.querySelectorAll('.nav-link.selected');
            navButtons.forEach(btn => btn.classList.remove('selected'));
        }
    });
});
