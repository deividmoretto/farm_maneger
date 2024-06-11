// Função para exibir uma mensagem de boas-vindas
function mostrarMensagem() {
    alert("Bem-vindo ao AgroVision!");
}

// Função para mudar a cor de fundo ao passar o mouse sobre a barra de menus
function mudarCorDeFundo() {
    var nav = document.querySelector("nav");
    nav.style.backgroundColor = "#4e944e"; // Verde mais claro
}

// Função para restaurar a cor de fundo ao remover o mouse da barra de menus
function restaurarCorDeFundo() {
    var nav = document.querySelector("nav");
    nav.style.backgroundColor = "#3f6f3f"; // Verde escuro
}
