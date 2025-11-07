document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.navbar-dropdown');

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
            const container = this.parentElement;

            document.querySelectorAll('.dropdown-container').forEach(other => {
                if (other !== container) {
                    other.classList.remove('active');
                }
            });

            container.classList.toggle('active')
        });
    });

    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-container').forEach(container => {
            container.classList.remove('active')
        })
    })
});