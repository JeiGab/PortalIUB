document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    
    form.addEventListener("submit", function (event) {
        const oldPassword = document.getElementById("oldPassword").value;
        const newPassword = document.getElementById("newPassword").value;
        const confirmPassword = document.getElementById("confirmPassword").value;
        
        // Validar que las contraseñas coincidan
        if (newPassword !== confirmPassword) {
            event.preventDefault();
            alert("Las nuevas contraseñas no coinciden.");
        }
        
        // Validar longitud de la nueva contraseña
        if (newPassword.length < 6 || newPassword.length > 12) {
            event.preventDefault();
            alert("La nueva contraseña debe tener entre 6 y 12 caracteres.");
        }
    });
});
