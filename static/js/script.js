// ======================================================
//  Estudio Bello - Funcionalidad principal
//  Autor: José Julián Tapia Bello
//  Archivo: script.js
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
    // ===========================
    // 🖼️ MODAL DE IMÁGENES
    // ===========================
    const modal = document.getElementById('modal');
    const modalImg = document.getElementById('modal-img');
    const closeModal = document.getElementById('close-modal');

    // Abre el modal al hacer clic en cualquier imagen de la galería
    document.querySelectorAll('.gallery img').forEach(img => {
        img.addEventListener("click", () => {
            modal.classList.add('show');
            modalImg.src = img.src;
        });
    });

    // Cierra el modal con la “X”
    closeModal.addEventListener("click", () => {
        modal.classList.remove('show');
    });

    // Cierra el modal haciendo clic fuera de la imagen
    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.classList.remove('show');
        }
    });

    // ===========================
    // 📱 SECCIONES FULLSCREEN (Portafolio y Paquetes)
    // ===========================
    const portafolioLink = document.querySelector('a[href="#portafolio"]');
    const paquetesLink = document.querySelector('a[href="#paquetes"]');
    const portafolioSection = document.getElementById("portafolio");
    const paquetesSection = document.getElementById("paquetes");

    // Abre una sección fullscreen
    function openSection(section) {
        document.body.classList.add('fullscreen-mode');

        // Oculta todas las secciones fullscreen antes de mostrar la elegida
        document.querySelectorAll('.fullscreen-section').forEach(sec => {
            sec.classList.remove('show');
        });

        // Muestra la sección seleccionada
        section.classList.add('show');

        // Bloquea el scroll del body (solo scroll interno)
        document.body.style.overflow = 'hidden';

        // Ajusta el tamaño visual
        const headerHeight = document.querySelector('header').offsetHeight;
        section.style.top = `${headerHeight}px`;
        section.style.height = `calc(100vh - ${headerHeight}px)`;
    }

    // Cierra todas las secciones fullscreen
    function closeAllSections() {
        document.body.classList.remove('fullscreen-mode');
        document.querySelectorAll('.fullscreen-section').forEach(section => {
            section.classList.remove('show');
        });
        document.body.style.overflow = 'auto';

        // Restaura el inicio
        const inicio = document.getElementById('inicio');
        inicio.style.display = 'flex';
        inicio.style.height = 'calc(100vh - 80px)';
        inicio.style.minHeight = 'calc(100vh - 80px)';
        inicio.style.marginTop = '0';
        inicio.style.paddingTop = '80px';

        // Asegura que la posición del scroll esté al inicio
        window.scrollTo(0, 0);
    }

    // Eventos de los enlaces del menú
    portafolioLink.addEventListener('click', (e) => {
        e.preventDefault();
        openSection(portafolioSection);
    });

    paquetesLink.addEventListener('click', (e) => {
        e.preventDefault();
        openSection(paquetesSection);
    });

    // Cierra fullscreen al hacer clic en otra sección del menú
    document.querySelectorAll('nav a:not([href="#portafolio"]):not([href="#paquetes"])').forEach(link => {
        link.addEventListener('click', () => closeAllSections());
    });

    // Ajusta dinámicamente la altura al cambiar tamaño de ventana
    window.addEventListener('resize', () => {
        const headerHeight = document.querySelector('header').offsetHeight;
        document.querySelectorAll('.fullscreen-section').forEach(section => {
            section.style.top = `${headerHeight}px`;
            section.style.height = `calc(100vh - ${headerHeight}px)`;
        });
    });

    // ===========================
    // 🎛️ BOTONES DESPLEGABLES DE PAQUETES
    // ===========================
    document.querySelectorAll(".toggle-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const content = btn.nextElementSibling;
            content.style.display = (content.style.display === "block") ? "none" : "block";
        });
    });
});