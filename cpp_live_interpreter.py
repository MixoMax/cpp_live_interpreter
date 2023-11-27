import subprocess
import os
import sys
import platform
import time

version = "r0.1alpha0"
date = "Nov 11 2023"

def run_cpp_code(code:list[str]):
    t_start = time.time()
    if os.path.exists("temp.cpp"):
        os.remove("temp.cpp")
    
    template_lines = [
        "//Auto injected code from cpp_live_interpreter.py",
        "#include <iostream>",
        "using namespace std;",
        "template<typename T>void print(T t) {cout << t << endl;}",
        "int main() {",
        "//End of auto injected code"
    ]
    code = template_lines + code + ["}"]
    
    with open("temp.cpp", "w") as f:
        for line in code:
            f.write(line)
            f.write("\n")
            
    popen = subprocess.Popen(["g++", "temp.cpp", "-o", "temp.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.wait()
    if popen.returncode != 0:
        print(popen.stderr.read().decode())
        return
    popen = subprocess.Popen(["temp.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.wait()
    print(popen.stdout.read().decode())
    print(popen.stderr.read().decode())
    
    print(f"Time taken: {time.time() - t_start:.2f}s")

def get_sys_info() -> list[str]:
    # Get system info
    # like os, architechture, g++ version, etc

    
    arch_info = platform.machine()
    os_info = platform.system()
    os_release_info = platform.release()
    os_arch_info = platform.architecture()
    
    sys_info = f"{os_info} {os_release_info} - {arch_info} ({os_arch_info[0]})"
    
    return sys_info
            

def main():
    start_message = [
        f"C++ Live Interpreter (v:{version} / {date})",
        f"{get_sys_info()}", #Windows 10 - AMD64 (64bit)
        'Type "help", "copyrigfht", "credits" or "license" for more information.',
        'Type "exit" to exit.',
    ]
    print("\n".join(start_message))
    
    previous_code = []
    while True:
        line = input(">>> ")
        
        match line:
            case "exit":
                return 0
            case "help":
                cmd_dict = { #command: description
                    "help": "Show this help message",
                    "credits": "Show credits",
                    "license": "Show license",
                    "version": "Show version",
                    "exit": "Exit the interpreter",
                    "end": "End the code input and run the code",
                    "run": "Run the code without ending the code input (eg. variables will be saved)",
                    "pop": "Delete the last line of code",
                    "clear": "Clear the screen",
                    "show": "Show the current code"
                }
                for cmd, desc in cmd_dict.items():
                    print(cmd.ljust(10),"-\t", desc)
            case "credits":
                credits_and_contact = {
                    "E-Mail": "linus@linushorn.dev",
                    "website": "https://linushorn.dev",
                    "github": "https://github.com/MixoMax",
                }
                credits_text = ["This Project was made completely by myself.",
                                "It is open source and you can find the source code on github.",
                                "Any contributions are welcome: https://github.com/MixoMax/cpp_live_interpreter",
                                "If you have any questions, suggestions, or problems, feel free to contact me."]
                
                print("\n".join(credits_text))
                for name, contact in credits_and_contact.items():
                    print(name.ljust(10), "-", contact)
            case "license":
                license_text = [
                    "Thsi project is open source and licensed under the Apache License 2.0",
                    "For More info see:",
                    "http://www.apache.org/licenses/LICENSE-2.0",
                    "or ./LICENSE.md"
                ]
                print("\n".join(license_text))
            case "version":
                print(version, date, sep=" / ")


if __name__ == "__main__":
    args = sys.argv[1:]
    built_in_commands = ["help", "credits", "license", "version"]
    if len(args) > 0:
        if args[0] in built_in_commands:
            match args[0]:
                case "help":
                    print("This is the help message")
                case "credits":
                    print("This is the credits message")
                case "license":
                    print("This is the license message")
                case "version":
                    print(version, date, sep=" / ")
        else:
            print("Unknown command")
    else:
        main()