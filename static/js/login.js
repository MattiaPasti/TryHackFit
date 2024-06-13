document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript is loaded and running!');
    console.log('SONO QUI');
    // Aggiungi il tuo codice JavaScript qui

    // Generazione e visualizzazione password
    const passwordDisplay = document.getElementById('password-display');

    setInterval(function() {
        const password = generatePassword();
        passwordDisplay.textContent = password;
    }, 500);

    function generatePassword() {
        const length = 20;
        const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!£$%&/()?^[]@#";
        let password = "";
        for (let i = 0; i < length; ++i) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        return password;
    }
});