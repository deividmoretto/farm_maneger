// Alternar tema claro/escuro
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            if (html.getAttribute('data-theme') === 'dark') {
                html.setAttribute('data-theme', 'light');
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            } else {
                html.setAttribute('data-theme', 'dark');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
            
            // Salvar a preferência do usuário
            localStorage.setItem('theme', html.getAttribute('data-theme'));
        });
        
        // Carregar tema salvo
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            html.setAttribute('data-theme', savedTheme);
            if (savedTheme === 'dark') {
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
        }
    }
    
    // Toggle de sidebar para dispositivos móveis
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }
    
    // Auto-fechar alerts após 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

// Controlador de loading para submissões de formulários
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form:not(.no-loading)');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    if (loadingSpinner) {
        forms.forEach(function(form) {
            form.addEventListener('submit', function() {
                // Validar formulário antes de mostrar spinner
                if (form.checkValidity()) {
                    loadingSpinner.classList.remove('d-none');
                }
            });
        });
    }
});

// Confirmação para exclusões
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete, [data-confirm]');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = button.getAttribute('data-confirm') || 'Tem certeza que deseja excluir este item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}); 