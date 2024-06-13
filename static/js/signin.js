document.getElementById('email').addEventListener('input', validateForm);
document.getElementById('password').addEventListener('input', validateForm);
document.getElementById('confirm-password').addEventListener('input', validateForm);

function validateForm() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Controllo validità email
    checkEmail();

    // Controllo password coincidono
    const passwordStatus = document.getElementById('password-status');
    if (password === confirmPassword && password.trim() !== '') {
        passwordStatus.textContent = "Le password coincidono";
        passwordStatus.className = "password-match";

        // Controllo forza della password
        checkPassword();

        // Abilita il pulsante "Registrati" solo se le password coincidono e sono entrambe non vuote
        const submitButton = document.getElementById('register-btn');
        submitButton.disabled = false;
    } else {
        passwordStatus.textContent = "Le password non coincidono";
        passwordStatus.className = "password-not-match";

        // Disabilita il pulsante "Registrati" se le password non coincidono o sono vuote
        const submitButton = document.getElementById('register-btn');
        submitButton.disabled = true;
    }

    return true; // Permette l'invio del form se tutti i controlli sono passati
}

function checkEmail() {
    const email = document.getElementById('email').value;
    const emailStatus = document.getElementById('email-status');
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        emailStatus.textContent = "Email non valida";
        emailStatus.className = "email-not-valid";
    } else {
        emailStatus.textContent = "Email valida";
        emailStatus.className = "email-valid";
    }
}

function isEmailValid(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function checkPassword() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const passwordStatus = document.getElementById('password-status');
    const confirmPasswordStatus = document.getElementById('confirm-password-status');

    // Aggiorna lo stato delle password
    if (password === confirmPassword && password.trim() !== '') {
        passwordStatus.textContent = "Le password coincidono";
        passwordStatus.className = "password-match";
        confirmPasswordStatus.textContent = "Le password coincidono";
        confirmPasswordStatus.className = "password-match";
    } else {
        passwordStatus.textContent = "Le password non coincidono";
        passwordStatus.className = "password-not-match";
        confirmPasswordStatus.textContent = "Le password non coincidono";
        confirmPasswordStatus.className = "password-not-match";
    }

    // Controllo forza della password
    const passwordLength = document.getElementById('password-length');
    const passwordUppercase = document.getElementById('password-uppercase');
    const passwordNumber = document.getElementById('password-number');
    const passwordSpecial = document.getElementById('password-special');

    passwordLength.textContent = password.length >= 9 ? "Lunghezza OK" : "Deve essere di almeno 9 caratteri";
    passwordLength.className = password.length >= 9 ? "password-strength-strong" : "password-strength-weak";

    passwordUppercase.textContent = /[A-Z]/.test(password) ? "Maiuscola OK" : "Deve contenere almeno una maiuscola";
    passwordUppercase.className = /[A-Z]/.test(password) ? "password-strength-strong" : "password-strength-weak";

    passwordNumber.textContent = /\d/.test(password) ? "Numero OK" : "Deve contenere almeno un numero";
    passwordNumber.className = /\d/.test(password) ? "password-strength-strong" : "password-strength-weak";

    passwordSpecial.textContent = /[!£$%&/()?^[\]@#]/.test(password) ? "Speciale OK" : "Deve contenere almeno un carattere speciale";
    passwordSpecial.className = /[!£$%&/()?^[\]@#]/.test(password) ? "password-strength-strong" : "password-strength-weak";
}