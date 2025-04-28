//res navbar
const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('show'); 
});

document.getElementById('appointmentForm').addEventListener('submit', function(event) {
    var termsCheckbox = document.getElementById('terms');
    
    if (!termsCheckbox.checked) {
        event.preventDefault(); // stop form from submitting
        alert("Please accept the Terms & Conditions to continue!");
    }
});