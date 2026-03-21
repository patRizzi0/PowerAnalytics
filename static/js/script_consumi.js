const steps = document.querySelectorAll(".step");
const nextBtns = document.querySelectorAll(".next-btn");
const prevBtns = document.querySelectorAll(".prev-btn");

let currentStep = 0;

function showStep(index) {
    steps.forEach((step, i) => {
        step.classList.toggle("active", i === index);
    });
}

function validateStep(stepIndex) {
    const currentInputs = steps[stepIndex].querySelectorAll("input, select");
    
    for (let input of currentInputs) {
        if (input.type === "button" || input.type === "submit") continue;

        if (input.type === "radio") {
            const groupName = input.name;
            const checked = steps[stepIndex].querySelector(`input[name="${groupName}"]:checked`);
            if (!checked) {
                alert("Seleziona un'opzione prima di continuare.");
                return false;
            }
            return true;
        }

        if (!input.value.trim()) {
            alert("Compila il campo prima di continuare.");
            input.focus();
            return false;
        }
    }

    return true;
}

nextBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        if (!validateStep(currentStep)) return;
        currentStep++;
        showStep(currentStep);
    });
});

prevBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        currentStep--;
        showStep(currentStep);
    });
});

showStep(currentStep);