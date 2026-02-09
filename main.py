import uvicorn
from masterServer import app

def main():
    uvicorn.run(app, host = "0.0.0.0", port = 7590)

if __name__ == "__main__":
    main()
