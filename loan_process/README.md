# Loan Processing System

A Django-based loan processing system with ML-powered risk assessment and a React frontend.

## Features

- User authentication and profile management
- Loan application submission and tracking
- Document upload and management
- ML-powered risk assessment and scoring
- Admin dashboard for loan management
- ML performance monitoring dashboard
- Email notifications for important events
- Rate limiting for sensitive APIs

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL database

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```
   cd loan_process
   pip install -r requirements.txt
   ```
3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```
4. Configure the database in `loan_process/settings.py`
5. Run migrations:
   ```
   python manage.py migrate
   ```

## Usage

The project includes a Makefile with common commands:

```
# Show available commands
make help

# Run the Django development server
make runserver

# Run the frontend development server
make frontend-dev

# Run tests
make test

# Run tests with coverage
make test-coverage

# Test email functionality
make test-email

# Train ML model
make train-model
```

## ML Performance Dashboard

The system includes a dashboard for monitoring ML model performance metrics:

- Access the dashboard at `/risk/models`
- View performance metrics (accuracy, precision, recall, AUC, F1 score)
- Filter by model version
- Visualize trends over time with line and bar charts
- Sort and filter data

## Email Notifications

The system sends email notifications for various events:

- Loan application submission
- Loan status updates
- Document uploads
- ML model performance updates and alerts

## Rate Limiting

Sensitive APIs are protected by rate limiting:

- Authentication endpoints: 5 requests per minute
- Registration: 10 requests per minute
- Loan application submission: 10 requests per hour
- Document uploads: 10 requests per hour

## Testing

Run tests using the Makefile:

```
make test
```

Or run specific test modules:

```
python manage.py test riskdashboards.tests.test_email_utils
python manage.py test loan_process.tests.test_throttling
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.