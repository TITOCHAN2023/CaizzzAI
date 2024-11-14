import uvicorn

from routes import create_app
from env import API_HOST, API_PORT

app = create_app()

def main() -> None:
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="critical",
    )


if __name__ == "__main__":
    main()
