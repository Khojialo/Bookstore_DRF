# Jigar Bookstore 📚

Jigar Bookstore is an **online bookstore project built with Django**. The project allows users to browse, search, and manage books, while providing administrators with a powerful admin panel for content management.

---

## 🚀 Features

* 📖 Book listing and detail pages
* 🔍 Search and filtering functionality
* 🧾 Automatic ISBN generation
* 👤 User registration and authentication
* 🛠 Book management via Django Admin
* 🔐 Secure authentication system
* 🐳 Docker support for deployment
* ⚙️ Production-ready configuration

---

## 🧰 Tech Stack

* **Backend:** Python, Django
* **Database:** PostgreSQL (production), SQLite (development)
* **Frontend:** Django Templates, HTML, CSS
* **Deployment:** Docker, Gunicorn
* **CI/CD:** GitHub Actions

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/jigar_bookstore.git
cd jigar_bookstore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

---

## ⚙️ Environment Variables

For production environment, set the following variables:

```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://...
ALLOWED_HOSTS=yourdomain.com
```

---

## 🐳 Docker

```bash
docker build -t jigar_bookstore .
docker run -p 8000:8000 jigar_bookstore
```

---

## 📄 Project Structure

```
jigar_bookstore/
│
├── books/
├── users/
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

---

## 👨‍💻 Project Owner

* **Khojialo**

---

## 📜 License

This project is licensed under the MIT License.

---

⭐ If you find this project useful, don’t forget to give it a star!
