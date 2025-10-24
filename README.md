# Aqualog

An internal web application for a small Italian freediving society to manage and visualize training and test data.

## Features

- **Member Management**: Complete registry of society members with personal details
- **Cooper Test Tracking**: Visualization of 12-minute Cooper test sessions with diving/surface time analysis
- **Indoor Trial Analysis**: Performance tracking for indoor training sessions
- **Data Visualization**: Interactive charts and performance trend analysis
- **Synthetic Data Generation**: CLI tool for generating realistic test data
- **Modern Architecture**: Built with Streamlit, DuckDB, and modern Python tooling

## Technology Stack

- **Frontend**: Streamlit 1.50+ with Material Icons
- **Database**: DuckDB for local data storage
- **Data Generation**: Faker with Italian locale
- **CLI**: Typer for command-line interface
- **Logging**: Loguru for structured logging
- **Environment**: uv for package management
- **Code Quality**: ruff for linting and formatting
- **Containerization**: Docker for deployment

## Quick Start

### Prerequisites

- Python 3.13+
- uv (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aqualog
```

2. Install dependencies with uv:
```bash
uv sync
```

Or with pip:
```bash
pip install -r requirements.txt
```

3. Generate sample data:
```bash
uv run python scripts/populate_db.py --members 50 --cooper-tests 200 --indoor-trials 300
```

4. Run the application:
```bash
uv run streamlit run app/main.py
```

5. Open your browser to `http://localhost:8501`

## Usage

### Data Population CLI

Generate synthetic data for testing and demonstration:

```bash
# Generate default dataset
uv run python scripts/populate_db.py

# Generate larger dataset with specific parameters
uv run python scripts/populate_db.py --members 200 --cooper-tests 1000 --indoor-trials 1500

# Clear and regenerate with seed for reproducibility
uv run python scripts/populate_db.py --clear-existing --seed 42

# Generate data for specific pool configurations
uv run python scripts/populate_db.py --pool-lengths 25 --pool-lengths 50

# Validate existing data
uv run python scripts/populate_db.py validate-data

# Clear all data
uv run python scripts/populate_db.py clear-database
```

### Authentication

Default credentials (configurable via environment variables):
- Username: `admin`
- Password: `freediving2024`

Set custom credentials:
```bash
export AQUALOG_USERNAME="your_username"
export AQUALOG_PASSWORD="your_password"
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

### Project Structure

```
freedive_app/
├── app/                    # Main application package
│   ├── main.py            # Streamlit entry point and routing
│   ├── login.py           # Authentication logic
│   └── pages/             # Individual page modules
│       ├── landing.py     # Dashboard with KPIs
│       ├── members.py     # Member registry display
│       ├── cooper_tests.py # Cooper test visualizations
│       └── indoor_trials.py # Indoor trial visualizations
├── db/                    # Database layer
│   ├── connection.py      # DuckDB connection management
│   ├── schema.sql         # Database schema definition
│   ├── queries.py         # Centralized query functions
│   └── utils.py           # Database utility functions
├── config/                # Configuration management
│   └── settings.py        # Application settings and constants
├── scripts/               # Utility scripts
│   └── populate_db.py     # Data generation script
└── tests/                 # Test suite
    └── test_db.py         # Database tests
```

## Docker Deployment

### Build and Run

```bash
# Build the container
docker build -t aqualog .

# Run the container
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
      - AQUALOG_USERNAME=admin
      - AQUALOG_PASSWORD=your_secure_password
```

## Database Schema

### Members Table
- Personal details (name, surname, date of birth)
- Contact information
- Membership start date

### Cooper Tests Table
- Test sessions with diving/surface time arrays
- Pool length configuration
- Performance notes

### Indoor Trials Table
- Training session data
- Distance and optional timing
- Pool length and location tracking

## Configuration

### Environment Variables

- `AQUALOG_USERNAME`: Authentication username (default: admin)
- `AQUALOG_PASSWORD`: Authentication password (default: aqualog2024)
- `DB_PATH`: Database file path (default: data/aqualog.duckdb)
- `LOG_LEVEL`: Logging level (default: INFO)

### Application Settings

Configure via `config/settings.py`:
- Database connection settings
- Authentication parameters
- Performance and caching options
- UI customization

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