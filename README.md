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

#### Starting the Application with Docker Compose
Starting from this version, you can also run the application using Docker Compose. After pulling the latest changes from the repository, follow these steps:

1. **Build and Start Containers:**
   ```bash
   docker-compose up -d --build
   ```

2. **Import SQL Files:**
   Import SQL files into your respective DBMS instances (e.g., MySQL, PostgreSQL) using their native tools or interfaces.

#### Project Functionality

- **User Levels:**
  - Regular User: Access level set to `1`.
  - Admin User: Access level set to `2` (default, changeable after initial user creation).

- **Password Security:**
  - **User Passwords:** Hashed using salting and peppering techniques for irreversible storage.
  - **Admin Passwords:** Encrypted using `Fernet` from `cryptography` for secure storage.

By following the above steps and leveraging the security measures in place, you can manage and store passwords securely within the Flask application.

**Note**

- This project is tested on Windows environment, utilizing XAMPP as the local DBMS.

---

Feel free to adjust any details specific to your setup or preferences. This README should now reflect the updated deployment process using Docker Compose for easier setup and management of your Flask Password Manager application.
