import json
import paramiko

def execute_ephemeral_agent_task(untrusted_code_string: str) -> str:
    """Spins up a local Firecracker microVM on minbox, executes code, 
    returns stdout/stderr, and cleanly terminates everything.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Establish connection down to your Linux minbox
    ssh.connect(hostname="192.168.1.50", username="mboxer", port=22)
    
    vm_id = None
    try:
        # Step 1: Fire up the ephemeral microVM boundary
        # Slicing directly off an OCI image ensures the clean-room environment is fresh
        create_cmd = "sudo vmsan create --from-image python:3.12-slim --json"
        _, stdout, stderr = ssh.exec_command(create_cmd)
        
        # Parse the execution JSON state metadata output
        vm_info = json.loads(stdout.read().decode())
        vm_id = vm_info["id"]
        
        # Step 2: Inject the untrusted code string safely into the runtime inside the kernel
        # Escaping double quotes inside the inline execution block strings
        escaped_code = untrusted_code_string.replace('"', '\\"')
        exec_cmd = f'sudo vmsan exec {vm_id} python -c "{escaped_code}"'
        _, run_stdout, run_stderr = ssh.exec_command(exec_cmd)
        
        output = run_stdout.read().decode()
        errors = run_stderr.read().decode()
        
        return output if not errors else f"Execution Error:\n{errors}"
        
    except Exception as e:
        return f"Harness Error: {str(e)}"
        
    finally:
        # Step 3: Tear down and wipe the hardware allocation footprint
        if vm_id:
            ssh.exec_command(f"sudo vmsan rm {vm_id}")
        ssh.close()

# --- Example Workflow Integration ---
agent_generated_logic = """
import math
# The agent performs resource-heavy processing entirely hidden away from the host
result = [math.factorial(x) for x in range(1, 10)]
print("Result computed inside hardware boundary:", result)
"""

# The run happens dynamically and leaves zero lingering processes on your 8GB VM
print(execute_ephemeral_agent_task(agent_generated_logic))