# Django FAQ API with Multi-language Support

This project provides a REST API for managing FAQs with support for multi-language translations. It uses Django, Django REST Framework, and Redis for caching.

---

## Features

- **Multi-language FAQ Support**: Automatically translates FAQs into any language using Google Translate API.
- **WYSIWYG Editor**: Uses `django-ckeditor` for rich text formatting of FAQ answers.
- **Versioned Caching**: Implements a versioned caching mechanism to ensure cache consistency and invalidation.
- **Admin Panel**: User-friendly admin interface for managing FAQs and translations.

---

## Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/sudouserx/django_WYSIWYG_faqs.git
cd django_WYSIWYG_faqs
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up the Database**
```bash
python manage.py migrate
```

### **4. Create a Superuser (Optional)**
```bash
python manage.py createsuperuser
```

### **5. Run the Development Server**
```bash
python manage.py runserver
```

### **6. Start Redis (for Caching)**
```bash
redis-server
```

---

## API Usage

### **Fetch FAQs**
- **Default (English)**:
  ```bash
  curl http://localhost:8000/api/faqs/
  ```

- **Hindi**:
  ```bash
  curl http://localhost:8000/api/faqs/?lang=hi
  ```

- **Bengali**:
  ```bash
  curl http://localhost:8000/api/faqs/?lang=bn
  ```

- **Any Language**:
  Replace `lang` with the desired language code (e.g., `fr`, `es`, `de`).

---

### **Create a New FAQ**
```bash
curl -X POST http://localhost:8000/api/faqs/ \
-H "Content-Type: application/json" \
-d '{"question": "What is Python?", "answer": "Python is a programming language."}'
```

---

### **Retrieve a Single FAQ**
```bash
curl http://localhost:8000/api/faqs/1/
```

---

### **Update an FAQ**
```bash
curl -X PUT http://localhost:8000/api/faqs/1/ \
-H "Content-Type: application/json" \
-d '{"question": "What is Django?", "answer": "Django is a web framework."}'
```

---

### **Delete an FAQ**
```bash
curl -X DELETE http://localhost:8000/api/faqs/1/
```

---

## Admin Panel

Access the admin panel at `http://localhost:8000/admin/` to manage FAQs and translations.

- **Username**: `admin`
- **Password**: `admin` (or the one you set during `createsuperuser`).

---

## Versioned Caching Mechanism

The API uses a **versioned caching mechanism** to ensure cache consistency and automatic invalidation. Here's how it works:

- **Cache Keys**: Cache keys include a version number (e.g., `faqs_list_en_v1`).
- **Cache Invalidation**: Whenever an FAQ is created, updated, or deleted, the cache version is incremented, invalidating all existing cached data.
- **Language Support**: Cache keys are language-specific, ensuring that translations are cached separately.

---

## Running Tests

The project includes comprehensive unit tests with **92% coverage**. To run the tests:

```bash
pytest --cov=faqs --cov-report=term-missing
```

### **Test Coverage**
- **Models**: 100% coverage for FAQ and FAQTranslation models.
- **Views**: 100% coverage for FAQViewSet, including caching and translation logic.
- **Overall Coverage**: 92%

---

## Caching

The API uses Redis for caching. Ensure Redis is running:
```bash
redis-server
```

---

## Deployment

### **Docker Setup**

1. **Build the Docker Image**:
   ```bash
   docker-compose build
   ```

2. **Start the Services**:
   ```bash
   docker-compose up
   ```

3. **Access the Application**:
   - Open your browser and go to `http://localhost:8000`.

4. **Stop the Services**:
   ```bash
   docker-compose down
   ```

---

### **Heroku Deployment (Optional)**

1. **Install the Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a Heroku App**:
   ```bash
   heroku create
   ```

4. **Deploy the Application**:
   ```bash
   git push heroku main
   ```

5. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

6. **Create a Superuser**:
   ```bash
   heroku run python manage.py createsuperuser
   ```

7. **Open the App**:
   ```bash
   heroku open
   ```

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "feat: Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.