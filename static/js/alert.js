function showAlert() {
    // Verifica si la alerta ya ha sido mostrada
    if (sessionStorage.getItem('alert_shown') === 'true') {
        return;
    }

    // Muestra la alerta y marca como mostrada
    const blurOverlay = document.createElement('div');
    blurOverlay.className = 'blur-overlay';
    const alertContainer = document.createElement('div');
    alertContainer.className = 'alert-container';
    alertContainer.innerHTML = `
        <div class="alert-content">
            <div class="alert-header">
                <img src="/static/imagenes/crisis.png" alt="Advertencia" class="alert-icon"> 
                <h2>Advertencia</h2>
            </div>
            <p>Este NO es un bot conversacional y se encuentra en constante entrenamiento y mejora. 
            Si cuenta con alguna queja, problema, recomendación, crítica constructiva puede depositarlo en el apartado de Observaciones. 
            El asistente virtual solo responde si la pregunta es específica y concreta. 
            Ten en cuenta que si necesitas más información de la que te puede brindar el asistente virtual, se recomienda que se acerque a bienestar en los horarios de 7:00 a.m - 7:00 p.m 
            o mandar un correo a bienestar@unibarranquilla.edu.co</p>
            <button class="alert-close" onclick="closeAlert();">Cerrar</button>
        </div>
    `;
    document.body.appendChild(blurOverlay);
    document.body.appendChild(alertContainer);

    // Establece alert_shown a true en sessionStorage
    sessionStorage.setItem('alert_shown', 'true');
}

function closeAlert() {
    const alertContainer = document.querySelector('.alert-container');
    const blurOverlay = document.querySelector('.blur-overlay');
    if (alertContainer) {
        alertContainer.remove();
    }
    if (blurOverlay) {
        blurOverlay.remove();
    }
}