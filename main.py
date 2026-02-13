import uvicorn
from server import app

def main():
    uvicorn.run(app, host = "0.0.0.0", port = 7590, reload = False, log_level = "debug")

if __name__ == "__main__":
    main()
