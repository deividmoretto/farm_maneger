/* scripts.js */

document.addEventListener("DOMContentLoaded", () => {
    // Função para navegação suave
    function smoothScroll(event) {
        event.preventDefault();
        const targetId = event.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        } else {
            window.location.href = event.target.getAttribute('href');
        }
    }

    // Função para feedback visual de botões
    function buttonFeedback(event) {
        const button = event.target;
        button.classList.add('clicked');
        setTimeout(() => {
            button.classList.remove('clicked');
        }, 200);
    }

    // Função para exibir mensagens de erro com fade out
    function fadeOutErrorMessages() {
        errorMessages.forEach(error => {
            setTimeout(() => {
                error.style.transition = 'opacity 1s';
                error.style.opacity = '0';
            }, 3000);
            setTimeout(() => {
                error.remove();
            }, 4000);
        });
    }

    // Navegação suave para links de navegação
    const navLinks = document.querySelectorAll('nav ul li a');
    if (navLinks.length > 0) {
        navLinks.forEach(link => {
            link.addEventListener('click', smoothScroll);
        });
    }

    // Feedback visual para botões
    const buttons = document.querySelectorAll('button');
    if (buttons.length > 0) {
        buttons.forEach(button => {
            button.addEventListener('click', buttonFeedback);
        });
    }

    // Exibir mensagens de erro com fade out
    const errorMessages = document.querySelectorAll('.error');
    if (errorMessages.length > 0) {
        fadeOutErrorMessages();
    }
});
