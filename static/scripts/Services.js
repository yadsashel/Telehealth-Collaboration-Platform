//responsive navbar
const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('show'); 
});

// Function that starts the counting animation
function startCounting() {
    // CountUp.js options (custom settings)
    const options = {
        duration: 2.5,  // How long the count animation should take (in seconds)
        separator: ","  // Adds commas to large numbers (e.g., 1,000 instead of 1000)
    };

    // Creating CountUp objects for each number
    const counter1 = new countUp.CountUp("counter1", 400, options); // Counts up to 400
    const counter2 = new countUp.CountUp("counter2", 500, options); // Counts up to 500
    const counter3 = new countUp.CountUp("counter3", 97, options);  // Counts up to 97

    // Checking if there are any errors before starting
    if (!counter1.error) {
        counter1.start(); // Start counting for the first number
        counter2.start(); // Start counting for the second number
        counter3.start(); // Start counting for the third number
    } else {
        console.error(counter1.error); // Log errors if something goes wrong
    }
}

// IntersectionObserver: Detects when the numbers are visible on the screen
const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) { // If the numbers are visible
            startCounting(); // Start the counting animation
            observer.disconnect(); // Stop observing after the animation runs
        }
    });
}, { threshold: 0.5 }); // The numbers should be at least 50% visible before starting

// Observing the first counter to trigger the animation
observer.observe(document.getElementById("counter1"));
