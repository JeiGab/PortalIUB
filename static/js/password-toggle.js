$(document).ready(function() {
    // Toggle para mostrar/ocultar la contraseña
    document.getElementById('togglePassword').addEventListener('click', function (e) {
        const password = document.getElementById('password');
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('bi-eye');
        this.classList.toggle('bi-eye-slash');
    });
});
