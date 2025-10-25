# 🏊‍♂️ Aqualog - Freediving Society Management System

An internal web application for a small Italian freediving society to manage and visualize training and test data.

## ✨ Features

- **Member Management**: Complete society member registry with personal details
- **Cooper Test Tracking**: Visualization of 12-minute Cooper test sessions with dive/surface time analysis
- **Indoor Trial Analysis**: Performance tracking for indoor training sessions
- **Data Visualization**: Interactive charts and performance trend analysis
- **Synthetic Data Generation**: CLI tool for generating realistic test data
- **Authentication System**: Access control with admin/user roles
- **Modern Architecture**: Built with Streamlit, DuckDB and modern Python tools

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.50+ with Material Icons
- **Database**: DuckDB for local data storage
- **Authentication**: Database-based system with encryption
- **Data Generation**: Faker with Italian locale
- **CLI**: Typer for command line interface
- **Logging**: Loguru for structured logging
- **Package Management**: uv for dependency management
- **Code Quality**: ruff for linting and formatting
- **Containerization**: Docker for deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- uv (recommended) or pip
- Cryptography package for authentication

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aqualog
```

2. Install dependencies with uv:
```bash
uv sync
uv pip install cryptography>=41.0.0
```

3. Initialize the database:
```bash
python scripts/cli.py init-db
```

4. Generate sample data:
```bash
python scripts/cli.py populate --members 50 --clear
```

5. Start the application:
```bash
streamlit run main.py
```

6. Open browser at `http://localhost:8501`

### 🔐 Default Credentials

- **Username**: `admin`
- **Password**: `aqualog2024`
- **Role**: Administrator

## 📋 Usage

### CLI for Data Management

Generate synthetic data for testing and demonstration:

```bash
# Generate default dataset
python scripts/cli.py populate --members 50

# Generate larger dataset with specific parameters
python scripts/cli.py populate --members 200 --min-tests 2 --max-tests 8 --clear

# View database statistics
python scripts/cli.py stats --detailed

# Validate data integrity
python scripts/cli.py validate

# Backup database
python scripts/cli.py backup

# Optimize database performance
python scripts/cli.py optimize
```

### User Management

```bash
# Create new user
python scripts/cli.py create-user --username john --password secure123 --role user --name "John Doe"

# List all users
python scripts/cli.py list-users

# Change user role
python scripts/cli.py change-role --username john --role admin

# Change password
python scripts/cli.py change-password --username john --password newpassword

# Deactivate/activate user
python scripts/cli.py deactivate-user --username john
python scripts/cli.py activate-user --username john
```

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
uv sync --dev
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
uv run pytest
```

4. Run linting:
```bash
uv run ruff check .
```

5. Format code:
```bash
uv run ruff format .
```

### 📁 Project Structure

```
aqualog/
├── main.py                 # Streamlit entry point
├── app/                    # Main application code
│   ├── __init__.py
│   ├── pages/              # Streamlit pages
│   │   ├── __init__.py
│   │   └── login.py        # Login page
│   ├── utils/              # Application utilities
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication manager
│   │   ├── auth_utils.py   # Authentication utilities
│   │   └── config.py       # Application configuration
│   └── auth/               # Authentication backend
│       ├── __init__.py
│       └── db_auth.py      # Database authentication
├── scripts/                # CLI scripts and utilities
│   ├── __init__.py
│   ├── cli.py              # CLI tool for management
│   └── data_generator.py   # Synthetic data generation
├── db/                     # Database layer
│   ├── __init__.py
│   ├── connection.py       # DuckDB connection management
│   ├── schema.sql          # Database schema
│   ├── models.py           # Data models
│   ├── queries.py          # Centralized query functions
│   └── utils.py            # Database utilities
├── tests/                  # Test suite
│   └── __init__.py
├── .streamlit/             # Streamlit configuration
│   ├── config.json         # App configuration
│   └── encryption.key      # Encryption key (auto-generated)
└── data/                   # Application data
    └── aqualog.duckdb      # DuckDB database
```

## 🐳 Deployment Docker

### Build and Run

```bash
# Build the container
docker build -t aqualog .

# Start the container
docker run -p 8501:8501 -v $(pwd)/data:/app/data aqualog
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  aqualog:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - AQUALOG_ENCRYPTION_KEY=your_base64_key_here
```

## 🗄️ Database Schema

### Members Table
- Personal details (name, surname, date of birth)
- Contact information
- Membership start date

### Cooper Tests Table
- Test sessions with arrays of dive/surface times
- Pool length configuration
- Performance notes

### Indoor Trials Table
- Training session data
- Distance and optional timing
- Pool length and location tracking

### Dashboard Users Table
- Encrypted credentials for system access
- Role management (admin/user)
- Access control and account lockout

## ⚙️ Configuration

### Environment Variables

- `AQUALOG_ENCRYPTION_KEY`: Encryption key (base64, auto-generated)
- `AQUALOG_SESSION_TIMEOUT`: Session timeout in minutes (default: 60)
- `AQUALOG_MAX_LOGIN_ATTEMPTS`: Maximum login attempts (default: 5)
- `AQUALOG_LOG_LEVEL`: Logging level (default: INFO)

### Application Settings

Configure via `.streamlit/config.json`:
- Database connection settings
- Authentication parameters
- Performance and caching options
- UI customization

### 🔐 Security

- **Encryption**: Passwords encrypted with Fernet (AES-128)
- **Hashing**: SHA-256 with unique user salts
- **Key Management**: Secure auto-generated encryption keys
- **Access Control**: Admin/user role system
- **Account Protection**: Lockout after failed attempts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.
