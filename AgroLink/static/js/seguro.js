document.addEventListener("DOMContentLoaded", function() {
    const coverageSelect = document.getElementById('coverage-select');
    const coverages = document.querySelectorAll('.coverage');

    coverageSelect.addEventListener('change', function() {
        coverages.forEach(function(coverage) {
            coverage.classList.add('hidden');
        });

        const selectedCoverage = document.getElementById(coverageSelect.value);
        if (selectedCoverage) {
            selectedCoverage.classList.remove('hidden');
        }
    });
});
