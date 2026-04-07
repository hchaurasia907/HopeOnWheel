// Core JS App Logic
// Map initialization and dynamic AJAX handled mostly inside the template script tags for scoped variables
console.log("HopeOn Wheel Web App Loaded Successfully!");

// Fade out flash messages after 5 seconds
setTimeout(() => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        flash.style.opacity = '0';
        setTimeout(() => flash.remove(), 300);
    });
}, 5000);
