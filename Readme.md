# EduTrack

EduTrack is a web-based student management and performance analysis platform designed to help schools manage students, teachers, examinations, marks, attendance, and academic performance through a centralized system.

## Features

* Teacher-side dashboard
* Management-side dashboard
* Student information management
* Teacher management
* Marks management
* Attendance management
* Examination management
* Student performance analysis
* Performance charts and graphs
* Class leaderboard
* CSV student data import
* User authentication
* AI-assisted student data interaction
* Email functionality
* Application logging

## Technologies Used

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

### Libraries and Tools

* Pandas
* MySQL Connector
* Git
* GitHub

## Project Structure

```text
EduTrack/
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

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/haamidhcoder-bot/EduTrack.git
```

### 2. Navigate to the project directory

```bash
cd EduTrack
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

On Windows:

```bash
.venv\Scripts\activate
```

### 5. Install the required dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

EduTrack uses MySQL as its database.

Create the database:

```sql
CREATE DATABASE schooldb;
```

Configure the database connection according to your environment.

Do not commit database passwords, API keys, secret keys, or other sensitive information to the repository.

## Running the Application

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

Start the Flask application:

```bash
python app.py
```

The application can then be accessed at:

```text
http://127.0.0.1:5000
```

## Teacher Side

The teacher side provides functionality for:

* Viewing students
* Managing marks
* Recording attendance
* Viewing examination results
* Analyzing student performance
* Viewing class rankings
* Monitoring academic progress

## Management Side

The management side provides functionality for:

* Managing students
* Managing teachers
* Managing classes and sections
* Managing examinations
* Monitoring attendance
* Viewing academic performance
* Managing school-related information

## Performance Analysis

EduTrack provides several tools for analyzing academic performance, including:

* Student performance summaries
* Subject-wise marks
* Examination results
* Class rankings
* Performance graphs
* Attendance information

These features help teachers and management monitor student progress and make better academic decisions.

## CSV Import

EduTrack supports importing student information using CSV files.

Example:

```csv
roll_no,student_name,class,section,student_gmail,DOB,mobile_no
1001,John Smith,10,A,john@gmail.com,2009-05-12,9876543210
1002,Jane Smith,10,A,jane@gmail.com,2009-08-20,9876543211
```

## Security

EduTrack follows security practices such as:

* Session-based authentication
* Protected routes
* Input validation
* CSV validation
* Secure credential management
* Prevention of unauthorized access

Sensitive information such as passwords, API keys, and secret keys should be stored outside the source code.

## AI Assistance

EduTrack includes an AI-assisted interface for interacting with student data and obtaining useful information from the school's database.

## Email Functionality

The application supports email functionality for system-related communication, including sending generated files and notifications.

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Commit your changes:

```bash
git commit -m "Add your feature"
```

5. Push the branch:

```bash
git push origin feature/your-feature
```

6. Create a Pull Request.

## License

This project is licensed under the MIT License.

## Author

**Haamidh Mohideen**

GitHub: `https://github.com/haamidhcoder-bot`
