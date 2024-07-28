document.addEventListener('DOMContentLoaded', function () {
    const navbarToggle = document.getElementById('navbarToggle');
    const customNavMenu = document.getElementById('customNavMenu');

    navbarToggle.addEventListener('click', function (event) {
        event.preventDefault();
        customNavMenu.style.display = customNavMenu.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', function (event) {
        if (!customNavMenu.contains(event.target) && event.target !== navbarToggle) {
            customNavMenu.style.display = 'none';
        }
    });
});
