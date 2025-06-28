import uvicorn # ASGI server to run FastAPI applications.
from fastapi import FastAPI, HTTPException, Header # Core FastAPI components.
import httpx # An asynchronous HTTP client to make requests to other APIs.

# Initialize the FastAPI application.
# 'title', 'description', and 'version' are used for automatic API documentation (Swagger UI/ReDoc).
app = FastAPI(title="FastApi django client example",
              description="fastapi that consumes the API of django",
              version="1.0.0")

# Define the base URL for the Django API.
# This constant makes it easy to change the target API endpoint if needed.
DJANGO_API_BASE_URL = 'https://127.0.0.1:8000/api/'

@app.get("/")
async def read_root():
    """
    Root endpoint for the FastAPI application.
    Returns a simple welcome message to confirm the server is running.
    """
    return {'message': 'Welcome to the fastapi client for django api tasks'}

@app.get("/tasks")
async def get_tasks(
    authorization: str = Header(None, description="Token of authentication (e.g., 'Token My_token')")
):
    """
    Proxies a GET request to the Django API to retrieve a list of tasks.
    Requires an Authorization header (e.g., a Django REST Framework Token).
    """
    # Prepare the headers to be sent to the Django API.
    # If an Authorization header is provided by the client, it's included.
    headers = {'Authorization': authorization} if authorization else {}

    # Use an asynchronous HTTP client to make the request to the Django API.
    async with httpx.AsyncClient() as client:
        try:
            # Make a GET request to the Django tasks endpoint.
            response = await client.get(f"{DJANGO_API_BASE_URL}tasks/", headers=headers)
            # Raise an exception for bad HTTP status codes (4xx or 5xx).
            response.raise_for_status()

            # Return the JSON response received from the Django API.
            return response.json()
        except httpx.RequestError as exc:
            # Handles network-related errors (e.g., Django API is not running or unreachable).
            raise HTTPException(
                status_code=500, detail=f"Network error connecting to Django API: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            # Handles HTTP errors (4xx or 5xx) returned by the Django API.
            # Extracts the 'detail' message from Django's error response if available.
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from Django API: {exc.response.json().get('detail', 'Unknown error')}"
            )
        except Exception as exc:
            # Catches any other unexpected errors.
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {exc}"
            )
        

@app.get("/labels/")
async def get_labels(
    authorization: str = Header(None, description="Token of authorization of django")
):
    """
    Proxies a GET request to the Django API to retrieve a list of labels.
    Requires an Authorization header (e.g., a Django REST Framework Token).
    This function has similar logic to `get_tasks`.
    """
    # Prepare the headers to be sent to the Django API.
    headers = {'Authorization': authorization} if authorization else {}

    async with httpx.AsyncClient() as client:
        try:
            # Make a GET request to the Django labels endpoint.
            response = await client.get(f"{DJANGO_API_BASE_URL}labels/", headers=headers)
            # Raise an exception for bad HTTP status codes.
            response.raise_for_status()

            # Return the JSON response received from the Django API.
            return response.json()
        except httpx.RequestError as exc:
            # Handles network-related errors.
            raise HTTPException(
                status_code=500, detail=f"Network error connecting to Django API: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            # Handles HTTP errors returned by the Django API.
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from Django API: {exc.response.json().get('detail', 'Unknown error')}"
            )
        except Exception as exc:
            # Catches any other unexpected errors.
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {exc}"
            ) 
        
if __name__ == '__main__':
    """
    Standard Python idiom to run code only when the script is executed directly.
    """
    # Runs the FastAPI application using Uvicorn.
    # host="127.0.0.1": Binds the server to the local IP address.
    # port=8001: Specifies the port the server will listen on (to avoid conflict with Django's default 8000).
    # reload=True: Enables auto-reloading the server when code changes are detected (useful for development).
    uvicorn.run(app, host="127.0.0.1",
                port=8001, reload=True)