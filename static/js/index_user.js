function updateLength() {
    var lengthInput = document.getElementById("length");
    var lengthInfo = document.getElementById("length-info");
    lengthInfo.textContent = "Lunghezza attuale: " + lengthInput.value;
}

function generatePassword() {
    var length = document.getElementById("length").value;
    var charset = "abcdefghijklmnopqrstuvwxyz"; // Caratteri minuscoli
    var uppercaseCharset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"; // Caratteri maiuscoli
    var numericCharset = "0123456789"; // Numeri
    var specialCharset = "!@#$%^&*()_+{}[]|;:,.<>?"; // Caratteri speciali

    var password = "";
    var allCharset = charset;

    // Aggiungi maiuscole se richiesto
    if (document.getElementById("uppercase").checked) {
        allCharset += uppercaseCharset;
    }

    // Aggiungi numeri se richiesto
    if (document.getElementById("numeric").checked) {
        allCharset += numericCharset;
    }

    // Aggiungi caratteri speciali se richiesto
    if (document.getElementById("special").checked) {
        allCharset += specialCharset;
    }

    for (var i = 0; i < length; i++) {
        password += allCharset.charAt(Math.floor(Math.random() * allCharset.length));
    }

    document.getElementById("password").value = password;
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = this.closest('.user').querySelector('.saved-password');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = 'Nascondi';
            } else {
                passwordInput.type = 'password';
                this.textContent = 'Mostra';
            }
        });
    });

    document.querySelectorAll('.copy-password').forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = this.closest('.user').querySelector('.saved-password');
            passwordInput.select();
            document.execCommand('copy');
            // alert('Password copiata negli appunti!');
        });
    });
});

