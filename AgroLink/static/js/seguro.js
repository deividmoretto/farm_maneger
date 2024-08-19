document.addEventListener("DOMContentLoaded", function() {
    const coverageSelect = document.getElementById('coverage-select');
    const coverages = document.querySelectorAll('.coverage');
    const additionalInfo = document.getElementById('additional-info');
    const extraDetails = document.getElementById('extra-details');

    const coverageDetails = {
        fire: "Este seguro é ideal para proteger áreas de reflorestamento contra incêndios devastadores. Também inclui assistência técnica especializada.",
        theft: "Com este seguro, você está protegido contra os danos que o granizo pode causar em suas plantações.",
        thirdParty: "Ideal para quem busca proteção abrangente, cobrindo riscos diversos que afetam a produção agrícola.",
        naturalDisasters: "Uma solução simplificada para proteção básica contra eventos naturais comuns.",
        liability: "Protege bens rurais empenhados como garantia em financiamentos.",
        harvestGuarantee: "Uma segurança extra para garantir que sua colheita esteja protegida contra eventos climáticos.",
        cafezal: "Cobertura completa para a produção de café, essencial para manter a estabilidade do cultivo."
    };

    coverageSelect.addEventListener('change', function() {
        coverages.forEach(function(coverage) {
            coverage.classList.add('hidden');
        });

        const selectedCoverage = document.getElementById(coverageSelect.value);
        if (selectedCoverage) {
            selectedCoverage.classList.remove('hidden');
            additionalInfo.classList.remove('hidden');
            extraDetails.textContent = coverageDetails[coverageSelect.value] || "Detalhes não disponíveis.";
        } else {
            additionalInfo.classList.add('hidden');
        }
    });
});
