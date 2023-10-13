from flask import Flask, request, jsonify
from flask_cors import CORS
import paramiko
import shlex

app = Flask(__name__)
CORS(app)

# List of approved commands
approved_commands = [
    "cat",
    "ls",
    "echo",
    "who",
    "uptime",
    "ip",
    "df",
    "uname",
    "systemctl status",  # Specify the full command you want to allow
]

def is_command_approved(command):
    for approved_command in approved_commands:
        if approved_command in command:
            return True
    return False

def run_command(server, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(server, username='kthengil')

        if is_command_approved(command):
            stdin, stdout, stderr = ssh.exec_command(command)
            command_output = stdout.read().decode("utf-8").strip()
            command_error = stderr.read().decode("utf-8").strip()
            ssh.close()

            if command_error:
                return "Failed with Error: " + command_error
            else:
                return "Execution Success: " + command_output
        else:
            return "Command not Approved: " + command
    except Exception as e:
        return "Failed with Error: " + str(e)

@app.route('/cmd', methods=['GET'])
def get_result():
    server = request.args.get('server')
    command = request.args.get('command')

    if not server or not command:
        return jsonify({"error": "Server and command parameters are required."}), 400

    result = run_command(server, command)

    return jsonify({"server": server, "command_output": result, "approved_commands": approved_commands})

if __name__ == '__main__':
    app.run(debug=True)
