import os
import time
import subprocess

def install_dependencies():
    print("Installing dependencies...")
    # Update package lists
    os.system("sudo apt update")
    
    # Install Python and pip if not already installed
    os.system("sudo apt install -y python3 python3-pip tor")

    # Install Flask if not already installed
    os.system("pip3 install Flask")

def configure_tor():
    print("Configuring Tor...")
    # Create a directory for the hidden service
    os.makedirs("/var/lib/tor/hidden_service/", exist_ok=True)

    # Write the Tor configuration
    with open("/etc/tor/torrc", "a") as torrc:
        torrc.write("\n# Hidden Service Configuration\n")
        torrc.write("HiddenServiceDir /var/lib/tor/hidden_service/\n")
        torrc.write("HiddenServicePort 80 127.0.0.1:5000\n")

def start_tor():
    print("Starting Tor service...")
    # Restart Tor to apply new configurations
    os.system("sudo systemctl restart tor")

def get_onion_address():
    # Wait for Tor to generate the onion address
    print("Waiting for Tor to generate the hostname...")
    time.sleep(5)  # Give Tor some time to generate the address

    # Read the hostname file to get the .onion address
    with open("/var/lib/tor/hidden_service/hostname", "r") as f:
        onion_address = f.read().strip()
    return onion_address

def create_flask_app():
    # Create a simple Flask app
    app_code = """from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>This is your website</h1><h2>WE ARE ANONYMOUS</h2><h3>Thank you to indcrypt for your support.</h3>' \
           '<p>To customize your page, create an index.html in the same directory.</p>'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
"""

    with open("torsite.py", "w") as f:
        f.write(app_code)

def run_flask_app():
    print("Starting Flask app...")
    os.system("python3 torsite.py &")

if __name__ == "__main__":
    print("Starting setup...")
    install_dependencies()
    configure_tor()
    start_tor()
    onion_address = get_onion_address()
    print(f"Your hidden service is available at: http://{onion_address}")

    create_flask_app()
    run_flask_app()

    print("Setup complete. Access your hidden service using the .onion address provided above.")
