$(document).ready(function() {
    // Toggle para la barra lateral
    $('#sidebarToggle').click(function() {
        $('.sidebar').toggleClass('active');
    });

    // Función para mostrar/ocultar el menú de configuración
    $('#configMenuButton').click(function(event) {
        $('#configMenu').toggle();
        event.stopPropagation();
    });

    // Cerrar el menú de configuración si se hace clic fuera de él
    $(document).click(function(event) {
        if (!$(event.target).closest('#configMenuButton').length) {
            $('#configMenu').hide();
        }
    });
});
