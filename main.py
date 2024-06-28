import subprocess
import time
import os

def run_script(script_name):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"Starting {script_name} at {start_time}")
    
    process = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    stderr = process.stderr.read()
    returncode = process.poll()
    
    if returncode == 0:
        print(f"{script_name} executed successfully.")
    else:
        print(f"Error executing {script_name}:\n{stderr}")

def main():
    scripts = [
        'rss_digest.py',
        'rating-openai.py',
        'summerize-high-rated.py',
        'make_newsletter.py',
        'renderpng.py',
        'cleanup.py'
    ]

    for i, script in enumerate(scripts, start=1):
        print(f"Running script {i}/{len(scripts)}: {script}")
        run_script(script)

if __name__ == "__main__":
    main()