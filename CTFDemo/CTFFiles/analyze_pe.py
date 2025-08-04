import subprocess
import sys

def analyze_file(file_path):
    print("Analyzing file strings (simulated header analysis):")
    try:
        result = subprocess.run(['strings', file_path], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
    except FileNotFoundError:
        print("Error: 'strings' command not found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_pe.py <file_path>")
        sys.exit(1)
    analyze_file(sys.argv[1])