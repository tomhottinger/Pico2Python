document.addEventListener('DOMContentLoaded', function() {
    const burgerMenu = document.querySelector('.burger-menu');
    const menuContainer = document.querySelector('.menu-container');

    burgerMenu.addEventListener('click', function() {
        burgerMenu.classList.toggle('active');
        menuContainer.classList.toggle('active');
        
        // Toggle aria-expanded
        const isExpanded = burgerMenu.classList.contains('active');
        burgerMenu.setAttribute('aria-expanded', isExpanded);
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = isExpanded ? 'hidden' : '';
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!burgerMenu.contains(event.target) && 
            !menuContainer.contains(event.target) && 
            menuContainer.classList.contains('active')) {
            burgerMenu.classList.remove('active');
            menuContainer.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});
