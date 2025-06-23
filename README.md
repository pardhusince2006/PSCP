# PSCP Project

A Django-based web application for managing projects with distinct teacher and student dashboards, secure authentication, and robust data management.

## Features
- Role-based dashboards for teachers and students
- Secure user authentication and registration
- Project creation, management, and notifications
- Dynamic HTML templates and static file handling
- Comprehensive automated testing with pytest

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PSCP
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
6. **Access the app:**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Running Tests
```bash
pytest
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
