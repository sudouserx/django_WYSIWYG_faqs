# Django FAQ API with Multi-language Support

This project provides a REST API for managing FAQs with support for multi-language translations. It uses Django, Django REST Framework, and Redis for caching.

## Features

- **Multi-language FAQ Support**: Automatically translates FAQs into any language using Google Translate API.
- **WYSIWYG Editor**: Uses `django-ckeditor` for rich text formatting of FAQ answers.
- **Caching**: Implements Redis caching for improved performance.
- **Admin Panel**: User-friendly admin interface for managing FAQs and translations.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/django-faq-api.git
   cd django-faq-api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**:
   ```bash
   python manage.py migrate
   ```

4. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

5. **Start Redis** (for caching):
   ```bash
   redis-server
   ```

## API Usage

### Fetch FAQs
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

### Create a New FAQ
```bash
curl -X POST http://localhost:8000/api/faqs/ -H "Content-Type: application/json" -d '{"question": "What is Python?", "answer": "Python is a programming language."}'
```

### Update an FAQ
```bash
curl -X PUT http://localhost:8000/api/faqs/1/ -H "Content-Type: application/json" -d '{"question": "What is Django?", "answer": "Django is a web framework."}'
```

### Delete an FAQ
```bash
curl -X DELETE http://localhost:8000/api/faqs/1/
```

## Admin Panel

Access the admin panel at `http://localhost:8000/admin/` to manage FAQs and translations.

- **Username**: `admin`
- **Password**: `admin` (or the one you set during `createsuperuser`)

## Running Tests

To run unit tests:
```bash
python manage.py test
```

## Caching

The API uses Redis for caching. Ensure Redis is running:
```bash
redis-server
```

## Deployment

### Docker
1. Build the Docker image:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up
   ```

### Heroku (Optional)
1. Install the Heroku CLI.
2. Deploy:
   ```bash
   heroku create
   git push heroku main
   ```

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

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
```