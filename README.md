# 🚀 Django Blog - Example Project

## Dự án mẫu cho khoá học Python Web Development with Django

### Tech Stack
- **Backend:** Django 5.2 LTS + Python 3.12+
- **Frontend:** Django Templates + Bootstrap 5 + HTMX 2.0
- **Database:** SQLite (dev) / PostgreSQL (production)
- **API:** Django REST Framework

### Cấu trúc dự án
```
django_project/
├── config/                 # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/                   # Blog application
│   ├── models.py          # Post, Category, Tag, Comment
│   ├── views.py           # ListView, DetailView, HTMX views
│   ├── forms.py           # PostForm, CommentForm, SearchForm
│   ├── admin.py           # Admin customization
│   ├── urls.py            # URL patterns
│   ├── tests/             # Unit tests
│   └── templatetags/      # Custom template tags
├── accounts/               # User authentication
├── templates/              # HTML templates
│   ├── base.html          # Master layout
│   ├── blog/              # Blog templates
│   │   ├── post_list.html
│   │   ├── post_detail.html
│   │   ├── post_form.html
│   │   └── partials/      # HTMX partial templates
│   └── accounts/          # Auth templates
├── static/                 # CSS, JS, images
├── media/                  # User uploads
└── requirements.txt
```

### Cài đặt & Chạy

```bash
# 1. Clone và tạo virtual environment
cd django_project
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Tạo database
python manage.py migrate

# 4. Tạo superuser
python manage.py createsuperuser

# 5. Chạy server
python manage.py runserver

# 6. Truy cập
# http://127.0.0.1:8000        - Blog
# http://127.0.0.1:8000/admin  - Admin panel
```

### Features đã implement
- [x] Blog CRUD (Create, Read, Update, Delete)
- [x] Category & Tag filtering
- [x] User authentication (Login/Logout)
- [x] HTMX live search
- [x] HTMX comment submission (no page reload)
- [x] Pagination
- [x] Admin panel customization
- [x] Unit tests
- [x] Responsive design (Bootstrap 5)

### Chạy Tests
```bash
python manage.py test
python manage.py test blog.tests -v 2
```
