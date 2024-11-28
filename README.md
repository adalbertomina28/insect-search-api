# Insectos Backend

Backend service for the Insectos App that handles integration with the iNaturalist API.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server with:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

- `GET /`: Welcome message
- `GET /api/observations`: Search for insect observations
  - Query parameters:
    - `query`: Search term
    - `per_page`: Number of results per page (default: 10)
    - `page`: Page number (default: 1)
- `GET /api/species/{taxon_id}`: Get detailed information about a specific species

## Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
