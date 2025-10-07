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
from datetime import datetime

app = Flask(__name__)

app.secret_key = "9a060b48d913a71b051da72bae5b2fdb83dec885a64f4e62d551e01da07caee9"

# Configurazione del primo database usando variabili d'ambiente
app.config["MYSQL_HOST"] = os.getenv("DB1_HOST", "localhost")
app.config["MYSQL_USER"] = os.getenv("DB1_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("DB1_PASSWORD", "root")
app.config["MYSQL_DB"] = os.getenv("DB1_NAME", "sql-db-1")

mysql = MySQL()
mysql.init_app(app)

# Configurazione del secondo database usando variabili d'ambiente
app.config["MYSQL1_HOST"] = os.getenv("DB2_HOST", "localhost")
app.config["MYSQL1_USER"] = os.getenv("DB2_USER", "root")
app.config["MYSQL1_PASSWORD"] = os.getenv("DB2_PASSWORD", "root")
app.config["MYSQL1_DB"] = os.getenv("DB2_NAME", "sql-db-2")

mysql1 = MySQL()
mysql1.init_app(app)

# Funzione di connessione per il primo database
def get_db_connection():
    return MySQLdb.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        db=app.config["MYSQL_DB"],
        cursorclass=MySQLdb.cursors.DictCursor
    )

# Funzione di connessione per il secondo database
def get_db1_connection():
    return MySQLdb.connect(
        host=app.config["MYSQL1_HOST"],
        user=app.config["MYSQL1_USER"],
        password=app.config["MYSQL1_PASSWORD"],
        db=app.config["MYSQL1_DB"],
        cursorclass=MySQLdb.cursors.DictCursor
    )

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
    encrypted_role = cipher.encrypt(role.encode('utf-8'))

    # Restituisce il ruolo cifrato
    return encrypted_role

def decrypt_role(encrypted_role):
    # Crea un oggetto Fernet con la chiave segreta
    cipher = Fernet(P_ROLE)

    # Decifra il ruolo
    decrypted_role = cipher.decrypt(encrypted_role.encode('utf-8')).decode('utf-8')

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
    
    # Get the current datetime
    now = datetime.now()

    # Format it as a string in MySQL-friendly format
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        
        conn = get_db1_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (session["id"], session["username"], formatted_date, 0)
        )
        conn.commit()  # Commit the transaction
        
        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            ("Successful logout", "A user has logged out", log_id)
        )

    except Exception as e:
        # In caso di errore, esegui il rollback delle modifiche
        conn.rollback()

        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (0, "GENERIC LOGOUT ERROR", formatted_date, 1)
        )
        conn.commit()  # Commit the transaction
        
        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Warnings (action, description, log_id) VALUES (%s, %s, %s)",
            ("LOGOUT ERROR", "Probably a user is trying to log out without being logged in, be careful", log_id)
        )
        
        msg = f"Errore durante l'inserimento dei dati nel database: {str(e)}"
    finally:
        # Chiudi la connessione e il cursore
        cursor.close()
        conn.close()
    
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT salt_email, salt_password FROM UserSalt")
        salts = cursor.fetchall()
        conn.close()

        found = False

        # Itera su ciascun salt
        for salt_record in salts:
            salt_email = salt_record['salt_email']
            salt_password = salt_record['salt_password']
            hashed_email = hash_with_pepper(email, salt_email)
            hashed_password = hash_with_pepper(password, salt_password)
            
            # Esegui la query per cercare l'email criptata nel database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE email = %s AND password = %s", (hashed_email, hashed_password,))
            account = cursor.fetchone()
            conn.close()
                
            # Se l'email corrisponde, imposta found a True e esci dal ciclo
            if account:
                found = True
                break

        if not found:
            msg = "Utente non registrato"
            
            # Get the current datetime
            now = datetime.now()

            # Format it as a string in MySQL-friendly format
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            
            conn = get_db1_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
                (0, "GENERIC LOGIN ERROR", formatted_date, 1)
            )
            conn.commit()  # Commit the transaction
            
            # Recupera l'ID dell'utente appena inserito
            log_id = cursor.lastrowid

            # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
            cursor.execute(
                "INSERT INTO Warnings (action, description, log_id) VALUES (%s, %s, %s)",
                ("FAILED LOGIN", "A user tried to log in with a non-existent account", log_id)
            )
            
            conn.commit()            
            conn.close()

            return render_template('login.html', msg=msg)
            
        else:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]

            conn1 = get_db_connection()
            cursor = conn1.cursor()
            cursor.execute("SELECT role FROM Role WHERE user_id = %s", (account["id"],))
            role_record = cursor.fetchone()
            conn1.close()
            role = decrypt_role(role_record["role"])
            
            if role == "1":
                session["role"] = "user"
                msg = "Accesso eseguito correttamente"
                passwords = get_decrypted_passwords()
                
                # Get the current datetime
                now = datetime.now()

                # Format it as a string in MySQL-friendly format
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                
                conn = get_db1_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
                    (session["id"], session["username"], formatted_date, 0)
                )
                conn.commit()  # Commit the transaction
                
                # Recupera l'ID dell'utente appena inserito
                log_id = cursor.lastrowid

                # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
                cursor.execute(
                    "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
                    ("Successful login", "A user has logged in with user privileges", log_id)
                )
                
                conn.commit()            
                conn.close()
                
                return render_template('index_user.html', msg=msg, passwords=passwords)
            
            elif role == "2":
                session["role"] = "admin"
                msg = "Accesso eseguito correttamente"
                profiles = get_profiles_with_decrypted_roles()
                
                # Get the current datetime
                now = datetime.now()

                # Format it as a string in MySQL-friendly format
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                
                conn = get_db1_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
                    (session["id"], session["username"], formatted_date, 0)
                )
                conn.commit()  # Commit the transaction
                
                # Recupera l'ID dell'utente appena inserito
                log_id = cursor.lastrowid

                # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
                cursor.execute(
                    "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
                    ("Successful login", "A user has logged in with ADMIN privileges", log_id)
                )
                
                conn.commit()            
                conn.close()
                
                return render_template('index_admin.html', msg=msg, profiles=profiles)
  
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
                
                # Log dell'azione di password non salvata
                log_action_warning(session["id"], session["username"], "User password not saved!", "The user is trying to save a password less than 9 characters long.")
                
                return render_template('index_user.html', msg=msg, passwords=passwords)
            else:
                try:
                    # Genera il salt per la password
                    encrypted_password = encrypt_role(password)

                    # Inserisci la password nella tabella 'Password'
                    conn = get_db_connection()
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "INSERT INTO Password (nome, password, user_id) VALUES (%s, %s, %s)",
                            (name, encrypted_password, session["id"])
                        )

                    conn.commit()

                    # Log dell'azione di password salvata correttamente
                    log_action_success(session["id"], session["username"], "User password saved", "The user's password has been saved correctly.")
                    
                    msg = "Registrazione completata con successo!"
                    passwords = get_decrypted_passwords()

                except Exception as e:
                    # In caso di errore, esegui il rollback delle modifiche
                    if 'conn' in locals():
                        conn.rollback()
                    
                    # Log dell'errore di password non salvata
                    log_action_error(session["id"], session["username"], "USER PASSWORD NOT SAVED!", f"Error saving user password: {str(e)}")
                    
                    msg = f"Errore durante l'inserimento dei dati nel database: {str(e)}"
                    passwords = get_decrypted_passwords()

                finally:
                    # Chiudi la connessione
                    conn.close()

        else:
            msg = "Perfavore completa tutti i campi!"

    passwords = get_decrypted_passwords()
    return render_template('index_user.html', msg=msg, passwords=passwords)


def log_action_warning(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert warning log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 1)
        )
        conn.commit()
        log_id = cursor.lastrowid

        # Insert warning details
        cursor.execute(
            "INSERT INTO Warnings (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )
        conn.commit()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action warning: {action} - {str(e)}")

    finally:
        # Close connection
        conn.close()


def log_action_success(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert success log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 0)
        )
        conn.commit()
        log_id = cursor.lastrowid

        # Insert success details
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )
        conn.commit()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action success: {action} - {str(e)}")

    finally:
        # Close connection
        conn.close()


def log_action_error(user_id, username, action, error_description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert error log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 2)
        )
        conn.commit()
        log_id = cursor.lastrowid

        # Insert error details
        cursor.execute(
            "INSERT INTO Errors (action, description, log_id) VALUES (%s, %s, %s)",
            (action, error_description, log_id)
        )
        conn.commit()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action error: {action} - {str(e)}")

    finally:
        # Close connection
        conn.close()

@app.route("/signin", methods=["GET", "POST"])
def signin():
    msg = ""
    if request.method == "POST":
        # Verifica che tutti i campi siano stati forniti nel form
        if all(field in request.form for field in ["username", "password", "email", "confirm-password"]):
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm-password"]
            role = "1"

            try:
                
                conn = get_db_connection()
                cursor = conn.cursor()
                        
                # Verifica se l'email è già registrata nel database
                cursor.execute("SELECT salt_email FROM UserSalt")
                salts = cursor.fetchall()
                
                found = False
                
                for salt_record in salts:
                    salt_email = salt_record['salt_email']
                    hashed_email = hash_with_pepper(email, salt_email)
                    
                    cursor.execute("SELECT * FROM User WHERE email = %s", (hashed_email,))
                    account = cursor.fetchone()
                    
                    if account:
                        found = True
                        break
                
                if found:
                    msg = "Utente già registrato. Utilizza un'email diversa."
                elif not username or not password or not email or not confirm_password:
                    msg = "Assicurati di compilare tutti i campi."
                elif len(password) < 9:
                    msg = "La password deve essere lunga almeno 9 caratteri."
                elif not any(char.isdigit() for char in password):
                    msg = "La password deve contenere almeno un numero."
                elif not any(char.isupper() for char in password):
                    msg = "La password deve contenere almeno una lettera maiuscola."
                elif not any(char in '!@#$%^&*()_-+=<>,.?/:;{}[]|' for char in password):
                    msg = "La password deve contenere almeno un carattere speciale."
                elif password != confirm_password:
                    msg = "Le password non coincidono."
                else:
                    # Genera i salt per password ed email
                    password_salt = generate_salt()
                    email_salt = generate_salt()

                    # Ottieni hash della password ed email con i rispettivi salt
                    hashed_password = hash_with_pepper(password, password_salt)
                    hashed_email = hash_with_pepper(email, email_salt)

                    # Cifra il ruolo
                    encrypted_role = encrypt_role(role)

                    # Inserisci l'utente nella tabella 'User'
                    cursor.execute(
                        "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)",
                        (username, hashed_email, hashed_password)
                    )
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
                    conn.commit()
                            
                    # Chiudi la connessione al database delle password
                    conn.close()

                    # Operazione di logging di successo
                    log_action_success4(0, "GENERIC USER REGISTERED", "User successfully registered", "A user has successfully registered")

                    msg = "Registrazione completata con successo!"

            except Exception as e:
                
                # In caso di errore, esegui il rollback delle modifiche e registra l'errore
                conn.rollback()
                conn.close()

                # Operazione di logging di errore
                log_action_error4(0, "GENERIC SIGNIN ERROR", "The user was not created correctly within the database! Take action now!",str(e))
                
                msg = f"Errore durante l'inserimento dei dati nel database: {str(e)}"

    return render_template("signin.html", msg=msg)

def log_action_success4(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert success log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 0)
        )

        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action: {action} - {str(e)}")


def log_action_error4(user_id, username, action, error_description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert error log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 2)
        )

        # Insert error details
        log_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Errors (action, description, log_id) VALUES (%s, %s, %s)",
            (action, error_description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action error: {action} - {str(e)}")

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/test")
def test():
    return render_template('password_test.html')

def get_profiles_with_decrypted_roles():
    conn = get_db_connection()
    cursor = conn.cursor()
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
    conn = get_db_connection()
    cursor = conn.cursor()
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Esegui la query per eliminare la password
        cursor.execute("DELETE FROM Password WHERE id=%s;", (id,))
        conn.commit()

        # Chiudi la connessione al database delle password
        conn.close()

        # Operazione di logging di successo
        log_action_success3(session["id"], session["username"], "Password successfully deleted", "A Registered User successfully deleted a password from his management system")

        # Recupera le password dopo l'eliminazione
        passwords = get_decrypted_passwords()

        # Messaggio di successo
        msg = 'Password eliminata con successo'

    except Exception as e:
        # In caso di errore, esegui il rollback delle modifiche e registra l'errore
        conn.rollback()
        conn.close()

        # Operazione di logging di errore
        log_action_error3(session["id"], session["username"], "Error deleting password", str(e))

        msg = f"Errore durante l'eliminazione della password: {str(e)}"
        passwords = get_decrypted_passwords()  # Recupera le password nonostante l'errore

    return render_template('index_user.html', msg=msg, passwords=passwords)


def log_action_success3(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert success log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 0)
        )

        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action: {action} - {str(e)}")


def log_action_error3(user_id, username, action, error_description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert error log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 2)
        )

        # Insert error details
        log_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Errors (action, description, log_id) VALUES (%s, %s, %s)",
            (action, error_description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action error: {action} - {str(e)}")

@app.route('/delete_user/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    try:
        
        if user_id == 1:
            msg = f"Impossibile eliminare un utente così bello."
            return redirect(url_for('admin_panel', msg=msg))
        
        # Elimina l'utente dal database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE id=%s", (user_id,))
        conn.commit()
        msg = 'Utente eliminato con successo'
        
        # Chiudi la connessione al database
        conn.close()
        
        # Registra l'operazione di eliminazione negli eventi di logging
        log_action_success2(session["id"], session["username"], "User successfully deleted", "A registered user has been successfully deleted")
        
    except Exception as e:
        # In caso di errore, esegui il rollback delle modifiche
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        msg = f"Errore durante l'eliminazione dell'utente: {str(e)}"
        
        # Registra l'errore negli eventi di logging
        log_action_error2(session["id"], session["username"], "Error deleting user", str(e))
    
    return redirect(url_for('admin_panel', msg=msg))


def log_action_success2(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert success log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 0)
        )
        
        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action: {action} - {str(e)}")


def log_action_error2(user_id, username, action, error_description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert error log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 2)
        )

        # Insert error details
        log_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Errors (action, description, log_id) VALUES (%s, %s, %s)",
            (action, error_description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action error: {action} - {str(e)}")

@app.route('/manage_user/<int:user_id>')
@login_required
@role_required('admin')
def manage_user(user_id):
    try:
        # Recupero e decripto il ruolo dell'utente
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT role FROM Role WHERE user_id = %s", (user_id,))
        role_record = cursor.fetchone()
        
        if not role_record:
            msg = 'Utente non trovato'
            cursor.close()
            conn.close()
            return render_template('index_admin.html', msg=msg, profiles=get_profiles_with_decrypted_roles())
        
        encrypted_role_hex = role_record["role"]
        current_role = decrypt_role(encrypted_role_hex)
        
        # Assegno all'utente un nuovo ruolo (inverti tra '1' e '2')
        new_role = '2' if current_role == '1' else '1'
        encrypted_new_role = encrypt_role(new_role)
        
        cursor.execute("UPDATE Role SET role = %s WHERE user_id = %s", (encrypted_new_role, user_id))
        conn.commit()
        
        msg = 'Ruolo utente aggiornato con successo'
        profiles = get_profiles_with_decrypted_roles()
        
        # Operazione di logging di successo
        log_action_success1(session["id"], session["username"], "User role successfully updated", "A user role has been successfully upgraded to Admin or User by an Admin")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        # In caso di errore, esegui il rollback delle modifiche e registra l'errore
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        msg = f"Errore durante l'aggiornamento del ruolo dell'utente: {str(e)}"
        profiles = get_profiles_with_decrypted_roles()  # Recupera i profili nonostante l'errore
        
        # Operazione di logging di errore
        log_action_error1(session["id"], session["username"], "Error updating user role", str(e))
    
    return render_template('index_admin.html', msg=msg, profiles=profiles)


def log_action_success1(user_id, username, action, description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert success log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 0)
        )

        # Recupera l'ID dell'utente appena inserito
        log_id = cursor.lastrowid

        # Inserisci i salt nella tabella 'UserSalt' associati all'ID dell'utente
        cursor.execute(
            "INSERT INTO Successes (action, description, log_id) VALUES (%s, %s, %s)",
            (action, description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action: {action} - {str(e)}")


def log_action_error1(user_id, username, action, error_description):
    try:
        conn = get_db1_connection()
        cursor = conn.cursor()

        # Get the current datetime
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # Insert error log entry
        cursor.execute(
            "INSERT INTO Logs (user_id, username, date_time, status_code) VALUES (%s, %s, %s, %s)",
            (user_id, username, formatted_date, 2)
        )

        # Insert error details
        log_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Errors (action, description, log_id) VALUES (%s, %s, %s)",
            (action, error_description, log_id)
        )

        # Commit the transaction
        conn.commit()
        conn.close()

    except Exception as e:
        # Log the error in case of failure
        print(f"Error logging action error: {action} - {str(e)}")
        
# --- SIMPLE PERIODIC WIPE: svuota la tabella Password ogni 5 secondi ---
import threading
import time
import traceback

WIPE_INTERVAL = 3600  # secondi

def periodic_wipe_loop():
    print(f"[WIPE] periodic wipe thread started, interval={WIPE_INTERVAL}s")
    while True:
        try:
            # get_db_connection() deve esistere nel tuo app.py e restituire una connessione DB
            conn = get_db_connection()
            cur = conn.cursor()
            # Esegui la cancellazione massiva
            cur.execute("DELETE FROM Password;")
            conn.commit()
            cur.close()
            conn.close()
            print(f"[WIPE] Deleted all rows from Password at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"[WIPE][ERROR] {e}")
            traceback.print_exc()
        # attendi l'intervallo definito
        time.sleep(WIPE_INTERVAL)

# Avvia il thread daemon (non blocca l'app principale)
wipe_thread = threading.Thread(target=periodic_wipe_loop, name="periodic-wipe-thread", daemon=True)
wipe_thread.start()
# --- fine periodic wipe ---

if __name__ == "__main__":
    app.run(debug=True)