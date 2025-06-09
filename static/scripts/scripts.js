document.addEventListener("DOMContentLoaded", function () {
  // === Navbar for main pages ===
  const mobileMenu = document.getElementById('mobile-menu');
  const navMenu = document.querySelector('.nav-menu');

  if (mobileMenu && navMenu) {
    mobileMenu.addEventListener('click', function () {
      navMenu.classList.toggle('active');
    });
  }

  // === Navbar for dashboards ===
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-hidden');
    });
  }

  // === Counter Animation ===
  function animateCounters() {
    const doctorsCounter = document.getElementById('doctorsCounter');
    const patientsCounter = document.getElementById('patientsCounter');
    const satisfactionCounter = document.getElementById('satisfactionCounter');

    if (!doctorsCounter || !patientsCounter || !satisfactionCounter) return;

    const doctorsTarget = 400;
    const patientsTarget = 50000;
    const satisfactionTarget = 98;

    let doctorsCurrent = 0;
    let patientsCurrent = 0;
    let satisfactionCurrent = 0;

    const doctorsIncrement = doctorsTarget / 50;
    const patientsIncrement = patientsTarget / 50;
    const satisfactionIncrement = satisfactionTarget / 50;

    const interval = setInterval(() => {
      doctorsCurrent = Math.min(doctorsCurrent + doctorsIncrement, doctorsTarget);
      patientsCurrent = Math.min(patientsCurrent + patientsIncrement, patientsTarget);
      satisfactionCurrent = Math.min(satisfactionCurrent + satisfactionIncrement, satisfactionTarget);

      doctorsCounter.innerText = Math.round(doctorsCurrent) + '+';
      patientsCounter.innerText = Math.round(patientsCurrent) + '+';
      satisfactionCounter.innerText = Math.round(satisfactionCurrent) + '%';

      if (
        doctorsCurrent >= doctorsTarget &&
        patientsCurrent >= patientsTarget &&
        satisfactionCurrent >= satisfactionTarget
      ) {
        clearInterval(interval);
      }
    }, 50);
  }

  // === Observer to trigger counter animation ===
  const heroStats = document.querySelector('.hero-stats');
  if (heroStats) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounters();
          observer.disconnect();
        }
      });
    }, { threshold: 0.1 });

    observer.observe(heroStats);
  }

  // === AI Assistant Logic ===
  const askBtn = document.getElementById("askBtn");
  const promptInput = document.getElementById("userPrompt");
  const responseBox = document.getElementById("aiResponse");

  if (askBtn && promptInput && responseBox) {
    askBtn.addEventListener("click", async function () {
      const prompt = promptInput.value.trim();
      if (!prompt) {
        responseBox.textContent = "Please enter a question.";
        return;
      }

      responseBox.textContent = "Thinking...";

      try {
        const res = await fetch("/api/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ prompt: prompt })
        });

        const data = await res.json();
        console.log(data);
        responseBox.innerHTML = formatResponse(data.response || "Sorry, no response received.");
      } catch (err) {
        console.error("Error:", err);
        responseBox.textContent = "There was an error connecting to the AI.";
      }
    });
  }

  function formatResponse(text) {
  if (!text) return "";

  // Convert numbered list
  const numbered = text.match(/^(\d+\.\s)/gm);
  if (numbered && numbered.length > 1) {
    const lines = text.split('\n').filter(Boolean);
    return '<ol>' + lines.map(line => `<li>${line.replace(/^\d+\.\s/, '')}</li>`).join('') + '</ol>';
  }

  // Convert bullets (if you use * or - or • in future answers)
  if (text.includes("•") || text.includes("- ")) {
    const bullets = text.split('\n').map(line => line.trim()).filter(Boolean);
    return '<ul>' + bullets.map(line => `<li>${line.replace(/^[-•*]\s*/, '')}</li>`).join('') + '</ul>';
  }

  // Otherwise, just return with line breaks
  return text.replace(/\n/g, '<br>');
}

});

// === Appointment Booking Modal ===
function toggleModal() {
  const modal = document.getElementById('appointmentModal');
  const bookBtn = document.getElementById('bookAppointmentBtn');
    modal.classList.toggle('show');  
    document.body.classList.toggle('modal-open');
      if (bookBtn) {
        bookBtn.addEventListener('click', () => toggleModal(true));
}
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    toggleModal(false);
  }
});