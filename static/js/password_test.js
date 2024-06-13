let passwordAnimationInterval;

function checkPassword() {
    const password = document.getElementById('password').value;

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

    // Aggiornamento barra di progresso e stima del tempo
    updateProgressBarAndTimeEstimate(password);

    // Gestione animazione visualizzazione password
    if (password.length > 0 && !passwordAnimationInterval) {
        startPasswordAnimation();
    } else if (password.length === 0 && passwordAnimationInterval) {
        stopPasswordAnimation();
    }
}

function updateProgressBarAndTimeEstimate(password) {
    const progressBarFill = document.getElementById('progress-bar-fill');
    const timeEstimate = document.getElementById('time-estimate');

    const score = calculatePasswordStrength(password);
    const timeToCrack = estimateTimeToCrack(password);

    progressBarFill.style.width = `${score}%`;

    timeEstimate.textContent = `Tempo stimato per scoprire la password: ${timeToCrack}`;
}

function calculatePasswordStrength(password) {
    let score = 0;

    if (password.length >= 9) score += 25;
    if (/[A-Z]/.test(password)) score += 25;
    if (/\d/.test(password)) score += 25;
    if (/[!£$%&/()?^[\]@#]/.test(password)) score += 25;

    return score;
}

function estimateTimeToCrack(password) {
    // Stima semplificata del tempo di scoperta
    const baseTime = 1000; // Tempo base in secondi
    let multiplier = 1;

    if (password.length >= 9) multiplier *= 10;
    if (/[A-Z]/.test(password)) multiplier *= 10;
    if (/\d/.test(password)) multiplier *= 10;
    if (/[!£$%&/()?^[\]@#]/.test(password)) multiplier *= 10;

    const timeInSeconds = (baseTime * multiplier) * password.length;

    if (timeInSeconds < 60) {
        return `${Math.round(timeInSeconds)} secondi`;
    } else if (timeInSeconds < 3600) {
        return `${Math.round(timeInSeconds / 60)} minuti`;
    } else if (timeInSeconds < 86400) {
        return `${Math.round(timeInSeconds / 3600)} ore`;
    } else {
        return `${Math.round(timeInSeconds / 86400)} giorni`;
    }
}

function startPasswordAnimation() {
    const passwordDisplay = document.getElementById('password-display');

    passwordAnimationInterval = setInterval(function() {
        const password = generatePassword();
        passwordDisplay.textContent = password;
    }, 500);
}

function stopPasswordAnimation() {
    clearInterval(passwordAnimationInterval);
    passwordAnimationInterval = null;
    const passwordDisplay = document.getElementById('password-display');
    passwordDisplay.textContent = "";
}

function generatePassword() {
    const length = 20;
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!£$%&/()?^[]@#";
    let password = "";
    for (let i = 0; i < length; ++i) {
        password += charset.charAt(Math.floor(Math.random() * charset.length));
    }
    return password;
}