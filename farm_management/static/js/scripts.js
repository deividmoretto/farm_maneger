/* scripts.js */

document.addEventListener("DOMContentLoaded", function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            } else {
                window.location.href = this.getAttribute('href');
            }
        });
    });

    // Feedback visual para botões
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            button.classList.add('clicked');
            setTimeout(() => {
                button.classList.remove('clicked');
            }, 200);
        });
    });

    // Exibir mensagens de erro com fade out
    const errorMessages = document.querySelectorAll('.error');
    errorMessages.forEach(error => {
        setTimeout(() => {
            error.style.transition = 'opacity 1s';
            error.style.opacity = '0';
        }, 3000);
        setTimeout(() => {
            error.remove();
        }, 4000);
    });
});
