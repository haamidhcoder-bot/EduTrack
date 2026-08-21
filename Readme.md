# Student Performance Analysis

A web-based student performance management system designed to help schools manage student information, marks, attendance, examinations, and performance analysis.

## 🚀 Features

*  Teacher-side dashboard
*  Management-side dashboard
*  Student information management
*  Student performance analysis
*  Marks management
*  Attendance management
*  Performance charts and graphs
*  Class leaderboard
*  CSV student data import
*  User authentication
*  AI-powered student data assistance
*  Email functionality
*  Application logging

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* MySQL
* SQLAlchemy

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### Other Tools

* Pandas
* Git & GitHub

## 📂 Project Structure

```text
Student_Performance_Analysis/
│
├── teacher_side/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── app.py
│
├── management_side/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── app.py
│
├── shared/
│   ├── config.py
│   ├── models.py
│   └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Student_Performance_Analysis.git
```

### 2. Open the project

```bash
cd Student_Performance_Analysis
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

Make sure MySQL is installed and running.

Create the database:

```sql
CREATE DATABASE schooldb;
```

Configure your database connection in the project's configuration file.

> Never upload database passwords or API keys to GitHub.

## ▶️ Running the Application

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Then start the Flask application:

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 📊 Main Modules

### Teacher Side

Teachers can:

* View students
* Enter marks
* Manage attendance
* View student performance
* View class rankings
* Analyze examination results

### Management Side

Management can:

* Manage teachers
* Manage students
* Manage classes and sections
* View overall performance
* Monitor attendance
* Manage examinations

## 🔒 Security

The application should:

* Store passwords securely
* Keep secret keys outside the source code
* Never expose database credentials
* Validate uploaded files
* Validate user input
* Use sessions for authentication
* Prevent unauthorized access to protected routes

## 📁 CSV Import

The system supports importing student information through CSV files.

Example:

```csv
roll_no,student_name,class,section,student_gmail,DOB,mobile_no
1001,John Smith,10,A,john@gmail.com,2009-05-12,9876543210
1002,Jane Smith,10,A,jane@gmail.com,2009-08-20,9876543211
```

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Push the branch.
6. Create a Pull Request.

## 📜 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Haamidh Mohideen**

GitHub: `https://github.com/your-username`
