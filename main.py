import os
import platform
import socket

from flask import Flask

app = Flask(__name__)

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "processor": platform.processor() or "N/A",
        "pid": os.getpid(),
        "working_dir": os.getcwd(),
        "container_host": os.getenv("HOSTNAME", "N/A"),
    }

@app.get("/")
def hello():
    info = get_system_info()
    return f"""
    <h1>Ну это просто контейнер</h1>
    
    <pre>
Hostname:       {info["hostname"]}
OS:             {info["os"]}
OS release:     {info["os_release"]}
Architecture:   {info["architecture"]}
Python version: {info["python_version"]}
Processor:      {info["processor"]}
PID:            {info["pid"]}
Working dir:    {info["working_dir"]}
Container host: {info["container_host"]}
    </pre>    
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
