### Project Description: Flask Password Manager

#### Introduction
This project utilizes Flask, a lightweight web framework for Python, to create a secure password manager. The password manager allows for the creation of users with different access levels and ensures password security through advanced hashing and encryption techniques.

#### Basic Commands to Start the Project
To get started with the project, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/flask-password-manager.git
   cd flask-password-manager
   ```

2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**
   Create a `.env` file in the project root with the following content:
   ```plaintext
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

5. **Initialize the Database:**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the Application:**
   ```bash
   flask run
   ```

#### Project Functionality

- **User Levels:**
  - Regular User: Access level set to `1`.
  - Admin User: Access level set to `2` (default, after creating first user, change it to 1 from app.py #def signin()).



- **Password Security:**
  - **User Passwords:** User passwords are hashed using a combination of salting and peppering techniques. These passwords are then encoded and stored irreversibly to ensure high security.
  - **Admin Passwords:** Admin passwords are encrypted using symmetric key encryption provided by the `Fernet` library from `cryptography`. This ensures that the admin passwords can be securely stored and retrieved when needed.

By following the above steps and leveraging the security measures in place, you can manage and store passwords securely within the Flask application.

**Note**

- This project is tested on windows environment, leveraging Xampp as local Dbsm.
