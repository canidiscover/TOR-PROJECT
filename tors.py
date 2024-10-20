import os
import subprocess
import time
from flask import Flask, send_from_directory, render_template_string

# Flask app setup
app = Flask(__name__)

# Paths
TOR_DIR = os.path.expanduser("~/.tor")
HIDDEN_SERVICE_DIR = os.path.join(TOR_DIR, "hidden_service")
LOG_FILE = os.path.join(TOR_DIR, "tor.log")

def install_dependencies():
    """Install all necessary dependencies (Tor, Flask)."""
    print("Installing dependencies...")
    os.system("pkg update -y && pkg upgrade -y")
    os.system("pkg install python tor -y")
    os.system("pip install flask")

def configure_tor():
    """Create and configure the Tor hidden service."""
    print("Configuring Tor...")
    if not os.path.exists(HIDDEN_SERVICE_DIR):
        os.makedirs(HIDDEN_SERVICE_DIR, mode=0o700)

    # Write the Tor configuration
    torrc_path = os.path.join(TOR_DIR, "torrc")
    with open(torrc_path, "w") as f:
        f.write(f"HiddenServiceDir {HIDDEN_SERVICE_DIR}/\n")
        f.write("HiddenServicePort 80 127.0.0.1:5000\n")
        f.write(f"Log notice file {LOG_FILE}\n")

def start_tor():
    """Start Tor in a background process."""
    print("Starting Tor...")
    subprocess.Popen(['tor', '-f', os.path.join(TOR_DIR, 'torrc')],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(15)  # Give Tor some time to initialize

def get_onion_address():
    """Wait for and retrieve the .onion URL."""
    print("Waiting for the .onion address...")
    hostname_file = os.path.join(HIDDEN_SERVICE_DIR, "hostname")

    # Check every 5 seconds, for up to 50 seconds
    for _ in range(10):
        if os.path.exists(hostname_file):
            with open(hostname_file, "r") as f:
                onion_url = f.read().strip()
                print(f"Your Tor hidden service is running at: {onion_url}")
                return onion_url
        else:
            print("Still waiting for Tor to generate the hostname...")
            time.sleep(5)

    print("Error: hostname file not found. Check your Tor configuration.")
    return None

# Default HTML to display if index.html is not found
DEFAULT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anonymous Website</title>
    <style>
        body {
            background-color: #000;
            color: #0f0;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        h1 {
            font-size: 3em;
        }
        p {
            font-size: 1.2em;
        }
        a {
            color: #0ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div>
        <h1>WE ARE ANONYMOUS</h1>
        <p>We are legion.</p>
        <p>Thanks to <strong>IndCrypt</strong> for making this possible.</p>
        <p>If you want to customize this page, create an <code>index.html</code> file in your Termux or Linux setup.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Serve the index.html file or the default page."""
    if os.path.exists("index.html"):
        return send_from_directory(os.getcwd(), 'index.html')
    else:
        return render_template_string(DEFAULT_HTML)

if __name__ == '__main__':
    print("Starting setup...")
    install_dependencies()  # Install all required packages
    configure_tor()          # Configure the Tor hidden service
    start_tor()              # Start the Tor process

    onion_url = get_onion_address()  # Wait for the .onion address

    if onion_url:
        print(f"Access your site at: {onion_url}")

    # Run the Flask web server
    print("Starting Flask server...")
    app.run(host='127.0.0.1', port=5000)
