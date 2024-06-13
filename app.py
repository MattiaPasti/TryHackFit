from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib
import re
import sys
import bcrypt
import os
import secrets
from functools import wraps
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

app = Flask(__name__)

app.secret_key = "cancro"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "sql-db-1"

mysql = MySQL(app)

PEPPER = b'3O=UfowScBy#TH~5[-{z'
P_ROLE = b"caaZ_UuXsw2DZTFhpOIP-6sWNQ5jiGl50bWKagqvUg4="

def generate_salt():
    return secrets.token_hex(16)

def hash_with_pepper(value, salt):
    peppered_value = value.encode('utf-8') + PEPPER
    hashed_value = hashlib.pbkdf2_hmac('sha256', peppered_value, salt.encode('utf-8'), 100000)
    return hashed_value.hex()

def encrypt_role(role):
    # Crea un oggetto Fernet con la chiave segreta
    cipher = Fernet(P_ROLE)

    # Cifra il ruolo
    encrypted_role = cipher.encrypt(role.encode())

    # Restituisce il ruolo cifrato
    return encrypted_role

def decrypt_role(encrypted_role):
    # Crea un oggetto Fernet con la chiave segreta
    cipher = Fernet(P_ROLE)

    # Decifra il ruolo
    decrypted_role = cipher.decrypt(encrypted_role).decode()

    # Restituisce il ruolo decifrato
    return decrypted_role

# Decoratore per controllare se l'utente è loggato
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decoratore per controllare il ruolo dell'utente
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Controlla se il ruolo dell'utente è quello richiesto
            if session.get('role') != role:
                # Reindirizza l'utente a una pagina non autorizzata
                return redirect(url_for('unauthorized'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Route per la pagina di accesso non autorizzata
@app.route('/unauthorized')
def unauthorized():
    return "Non sei autorizzato a visualizzare questa pagina."

@app.errorhandler(500)
def internal_error(error):
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))

@app.route("/logout")
@login_required
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST" and "email" in request.form and "password" in request.form:
        email = request.form["email"]
        password = request.form["password"]

        # Esegui la query per ottenere tutti i salt delle email nel database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT salt_email, salt_password FROM UserSalt")
        salts = cursor.fetchall()

        found = False

        # Itera su ciascun salt
        for salt_record in salts:
            salt_email = salt_record['salt_email']
            salt_password = salt_record['salt_password']
            hashed_email = hash_with_pepper(email, salt_email)
            hashed_password = hash_with_pepper(password, salt_password)
            
            # Esegui la query per cercare l'email criptata nel database
            cursor.execute("SELECT * FROM User WHERE email = %s AND password = %s", (hashed_email, hashed_password,))
            account = cursor.fetchone()
                
            # Se l'email corrisponde, imposta found a True e esci dal ciclo
            if account:
                found = True
                break

        if found != True:
            msg = "Utente non registrato"
            return render_template('login.html', msg=msg)
        else:

            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]

            cursor.execute("SELECT role FROM Role WHERE user_id = %s", (account["id"],))
            role_record = cursor.fetchone()
            role = decrypt_role(role_record["role"])
            
            if role == "1":
                session["role"] = "user"
                msg = "Accesso eseguito correttamente"
                passwords = get_decrypted_passwords()
                return render_template('index_user.html', msg = msg, passwords=passwords)
            elif role == "2":
                session["role"] = "admin"
                msg = "Accesso eseguito correttamente"
                profiles = get_profiles_with_decrypted_roles()
                return render_template('index_admin.html', msg = msg, profiles=profiles)
  
    return render_template("login.html", msg=msg)

@app.route("/save", methods=["POST"])
@login_required
@role_required('user')
def save():
    msg = ""
    if request.method == "POST":
        if "name" in request.form and "password" in request.form:
            name = request.form["name"]
            password = request.form["password"]     
            if len(password) < 9:
                msg = "Perfavore inserisci una password più sicura"
                passwords = get_decrypted_passwords()
                return render_template('index_user.html', msg = msg, passwords=passwords)
            else:
                try:
                    # Genera i salt per la password e l'email
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                    # Cifra la password
                    encrypted_password = encrypt_role(password)

                    # Inserisci l'utente nella tabella 'User'
                    cursor.execute(
                        "INSERT INTO Password (nome, password, user_id) VALUES (%s, %s, %s)",
                        (name, encrypted_password, session["id"])
                    )

                    # Conferma le modifiche al database
                    mysql.connection.commit()
                            
                    # Messaggio di successo
                    msg = "Registrazione completata con successo!"
                    passwords = get_decrypted_passwords()
                    return render_template('index_user.html', msg = msg, passwords=passwords)
                except Exception as e:
                    # In caso di errore, esegui il rollback delle modifiche
                    mysql.connection.rollback()
                    msg = f"Errore durante l'inserimento dei dati nel database: {str(e)}"
                finally:
                    # Chiudi il cursore
                    cursor.close()            
    else:
        msg = "Perfavore completa tutti i campi!"
    passwords = get_decrypted_passwords()
    return render_template('index_user.html', msg = msg, passwords=passwords)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    msg = ""
    if request.method == "POST":
        if "username" in request.form and "password" in request.form and "email" in request.form and "confirm-password" in request.form:
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm-password"]
            role = "2"

            # Esegui la query per ottenere tutti i salt delle email nel database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT salt_email FROM UserSalt")
            salts = cursor.fetchall()
            
            found = False
            
            # Itera su ciascun salt
            for salt_record in salts:
                salt_email = salt_record['salt_email']
                hashed_email = hash_with_pepper(email, salt_email)
            
                # Esegui la query per cercare l'email criptata nel database
                cursor.execute("SELECT * FROM User WHERE email = %s", (hashed_email,))
                account = cursor.fetchone()
                
                # Se l'email corrisponde, imposta found a True e esci dal ciclo
                if account:
                    found = True
                    break

            if found == True:
                msg = "Utente già registrato, assicurati di usare una mail diversa"
                return render_template('signin.html', msg = msg)
            elif not username or not password or not email or not confirm_password:
                msg = "Assicurati di aver compilato tutti i campi"
                return render_template('signin.html', msg = msg)
            elif len(password) < 9:
                msg = "La password deve essere lunga almeno 9 caratteri"
                return render_template('signin.html', msg = msg)
            elif not any(char.isdigit() for char in password):
                msg = "La password deve contenere almeno un numero"
                return render_template('signin.html', msg = msg)
            elif not any(char.isupper() for char in password):
                msg = "La password deve contenere almeno una lettera maiuscola"
                return render_template('signin.html', msg = msg)
            elif not any(char in '!@#$%^&*()_-+=<>,.?/:;{}[]|' for char in password):
                msg = "La password deve contenere almeno un carattere speciale"
                return render_template('signin.html', msg = msg)
            elif password != confirm_password:
                msg = "Le password non coincidono"
                return render_template('signin.html', msg = msg)
            else:
                # Esegui la query per verificare se l'email esiste già nel database
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
                account = cursor.fetchone()

                if account:
                    msg = "E' già stato registrato un utente con quella mail"
                else:
                    try:
                        # Genera i salt per la password e l'email
                        password_salt = generate_salt()
                        email_salt = generate_salt()

                        # Ottieni l'hash della password e dell'email con i rispettivi salt
                        hashed_password = hash_with_pepper(password, password_salt)
                        hashed_email = hash_with_pepper(email, email_salt)

                        # Cifra il ruolo
                        encrypted_role = encrypt_role(role)

                        # Inserisci l'utente nella tabella 'User'
                        cursor.execute(
                            "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)",
                            (username, hashed_email, hashed_password)
                        )

                        # Recupera l'ID dell'utente appena inserito
                        user_id = cursor.lastrowid

                        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
                        cursor.execute(
                            "INSERT INTO UserSalt (salt_email, salt_password, user_id) VALUES (%s, %s, %s)",
                            (email_salt, password_salt, user_id)
                        )

                        # Inserisci il ruolo cifrato nella tabella 'Role'
                        cursor.execute(
                            "INSERT INTO Role (role, user_id) VALUES (%s, %s)",
                            (encrypted_role, user_id)
                        )

                        # Conferma le modifiche al database
                        mysql.connection.commit()
                        
                        # Messaggio di successo
                        msg = "Registrazione completata con successo!"
                        return render_template('login.html', msg=msg)
                    except Exception as e:
                        # In caso di errore, esegui il rollback delle modifiche
                        mysql.connection.rollback()
                        msg = f"Errore durante l'inserimento dei dati nel database: {str(e)}"
                    finally:
                        # Chiudi il cursore
                        cursor.close()
        else:
            msg = "Perfavore completa tutti i campi!"

    return render_template("signin.html", msg=msg)

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/test")
def test():
    return render_template('password_test.html')

def get_profiles_with_decrypted_roles():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT User.id, User.username, Role.role FROM User LEFT JOIN Role ON User.id = Role.user_id")
    profiles_with_decrypted_roles = []
    for profile_record in cursor.fetchall():
        user_id = profile_record["id"]
        username = profile_record["username"]
        role = decrypt_role(profile_record["role"])
        if role == "1":
            role = "Utente"
        else:
            role = "Admin"
        profiles_with_decrypted_roles.append((user_id, username, role))
    cursor.close()
    return profiles_with_decrypted_roles

def get_decrypted_passwords():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Password.id, Password.nome, Password.password FROM Password WHERE %s = Password.user_id", (session["id"],))
    passwords_list = []
    for passwords_saved in cursor.fetchall():
        id = passwords_saved["id"]
        nome = passwords_saved["nome"]
        password = decrypt_role(passwords_saved["password"])
        passwords_list.append((id, nome, password))
    cursor.close()
    return passwords_list

# Route protetta che richiede un ruolo specifico
@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    profiles = get_profiles_with_decrypted_roles()
    return render_template("index_admin.html", profiles=profiles)

# Route protetta che richiede un ruolo specifico
@app.route('/user')
@login_required
@role_required('user')
def user_panel():
    passwords = get_decrypted_passwords()
    return render_template("index_user.html", passwords=passwords)

@app.route('/delete_password/<int:id>')
@login_required
@role_required('user')
def delete_password(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Password WHERE id=%s;", (str(id)))
    msg = 'Password eliminata con successo'
    mysql.connection.commit()
    passwords = get_decrypted_passwords()
    return render_template('index_user.html', msg = msg, passwords=passwords)

@app.route('/delete_user/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM User WHERE id=%s;", (str(user_id)))
    msg = 'Utente eliminato con successo'
    mysql.connection.commit()
    return redirect (url_for('admin_panel', msg=msg))

@app.route('/manage_user/<int:user_id>')
@login_required
@role_required('admin')
def manage_user(user_id):
    # Recupero e decripto il ruolo dell'utente
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT role FROM Role WHERE user_id = %s", (str(user_id)))
    role_record = cursor.fetchone()
    encrypted_role_hex = role_record["role"]
    role = decrypt_role(encrypted_role_hex)
    # Assegno all'utente un nuovo ruolo
    if role == "1":
        new_role = "2"
        encrypted_role = encrypt_role(new_role)
        cursor.execute("UPDATE Role SET role = %s WHERE user_id = %s;", (encrypted_role, str(user_id)))        
        msg = 'Utente aggiornato con successo'
        mysql.connection.commit()
        profiles = get_profiles_with_decrypted_roles()
        return render_template('index_admin.html', msg=msg, profiles=profiles)
    else:
        new_role = "1"
        encrypted_role = encrypt_role(new_role)
        cursor.execute("UPDATE Role SET role = %s WHERE user_id = %s;", (encrypted_role, str(user_id)))        
        msg = 'Utente aggiornato con successo'
        mysql.connection.commit()
        profiles = get_profiles_with_decrypted_roles()
        return render_template('index_admin.html', msg=msg, profiles=profiles)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)