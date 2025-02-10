setTimeout(() => {
    document.querySelectorAll(".alert").forEach(alert => {
        alert.style.animation = "fadeOut 0.5s ease forwards";
        setTimeout(() => alert.remove(), 500);
    });
}, 4000); // Auto-remove after 4 seconds