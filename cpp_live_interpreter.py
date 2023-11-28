import subprocess
import os
import sys
import platform
import re
import time

version = "r0.1alpha1"
date = "Nov 11 2023"


def compile(input_file:str, output_file:str):
    compiler = get_compiler() #"clang" or "g++"
    
    if compiler == "clang":
        cmd = f"clang++ -o {output_file} {input_file}"
    elif compiler == "g++":
        cmd = f"g++ -o {output_file} {input_file}"
    
    print(cmd)
    
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.wait()
    
    if popen.returncode != 0:
        print(popen.stderr.read().decode(), end="")
        print(f"Compilation failed with exit code {popen.returncode}")

def run_cpp_code(code:list[str]):
    t_start = time.time()
    if os.path.exists("temp.cpp"):
        os.remove("temp.cpp")
    
    code = insert_code_and_clean_up(code)
    if not code_will_run(code):
        print("Code will not run. Please check brackets and curly brackets")
        return
    
    
    with open("temp.cpp", "w") as f:
        for line in code:
            f.write(line)
            f.write("\n")
            
    compile("temp.cpp", "temp.exe")
    t_finish_compile = time.time()
    
    popen = subprocess.Popen(["./temp.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen.wait()
    print(popen.stdout.read().decode(), end="")
    print(popen.stderr.read().decode(), end="")
    
    exit_code = popen.returncode
    t_finish_run = time.time()
    print(f"programm exited with code {exit_code} (0x{exit_code:02X}) after {t_finish_run - t_start:.3f}s (compile: {t_finish_compile - t_start:.3f}s, run: {t_finish_run - t_finish_compile:.3f}s)")

def insert_code_and_clean_up(code:list[str]) -> list[str]:
    # Insert code into template and clean up
    # like adding #include <iostream> and removing comments
    
    includes = ["#include <iostream>"]
    for line in code:
        if line.startswith("#include"):
            includes.append(line)
            
    code = [line for line in code if not line.startswith("#include")]
    
    
    code = [f"print({line});" if is_direct_print(line) else line for line in code]
    
    template_lines = [
        "//Auto injected code from cpp_live_interpreter.py",
        *includes,
        "using namespace std;",
        "template<typename T>void print(T t) {cout << t << endl;}",
        "int main() {",
        "//End of auto injected code"
    ]
    
    code = template_lines + code + ["}"]
    
    
    
    
    return code

def code_will_run(code:list[str]) -> bool:
    # Absoulutly turing complete code checker
    
    code_str = "\n".join(code)
    
    #delete string literals
    while True:
        start = code_str.find("\"")
        if start == -1:
            break
        end = code_str.find("\"", start+1)
        code_str = code_str[:start] + code_str[end+1:]
    
    #delete comments
    while True:
        start = code_str.find("//")
        if start == -1:
            break
        end = code_str.find("\n", start+1)
        code_str = code_str[:start] + code_str[end+1:]
    
    
    # count brackets and curly brackets
    bracket_count = 0
    curly_bracket_count = 0
    for char in code_str:
        match char:
            case "{": curly_bracket_count += 1
            case "}": curly_bracket_count -= 1
            case "(": bracket_count += 1
            case ")": bracket_count -= 1
    
    if bracket_count == 0 and curly_bracket_count == 0:
        return True
    else:
        print(bracket_count, curly_bracket_count)

def is_direct_print(line:str) -> bool:
    # Check if a line is a direct print statement
    #it can only include numbers, vars, and operators
    
    allowed_chars = "0123456789+-*/%() "
    
    r = all([char in allowed_chars for char in line])
    if not r:
        return False
    else:
        return True

def get_sys_info() -> list[str]:
    # Get system info
    # like os, architechture, g++ version, etc

    py_version = platform.python_version()
    
    compiler = get_compiler()
    compiler_version = subprocess.Popen([compiler, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    compiler_version.wait()
    gpp_version = compiler_version.stdout.read().decode().split("\n")[0].split(" ")[-1]
    
    arch_info = platform.machine()
    os_info = platform.system()
    os_release_info = platform.release()
    os_arch_info = platform.architecture()
    
    sys_info = f"{os_info} {os_release_info} - {arch_info} ({os_arch_info[0]}) - Python {py_version} - g++ v{gpp_version}"
    
    return sys_info
            
def print_help():
    cmd_dict = { #command: description
        "help*": "Show this help message",
        "credits*": "Show credits",
        "license*": "Show license",
        "version*": "Show version",
        "exit": "Exit the interpreter",
        "end": "End the code input and run the code",
        "run": "Run the code without ending the code input (eg. variables will be saved)",
        "pop": "Delete the last line of code",
        "clear": "Clear the screen and delete all code",
        "show": "Show the current code with syntax highlighting",
    }
    print("Commands with * are also available as command line arguments\n")
    for cmd, desc in cmd_dict.items():
        print(f"{cmd: <10} - {desc}")

def print_credits():
    # Print credits and contact info
    credits_and_contact = {
        "E-Mail": "linus@linushorn.dev",
        "website": "https://linushorn.dev",
        "github": "https://github.com/MixoMax",
    }
    credits_text = ["This Project was made completely by myself.",
                    "It is open source and you can find the source code on github.",
                    "Any contributions are welcome: https://github.com/MixoMax/cpp_live_interpreter",
                    "If you have any questions, suggestions, or problems, feel free to contact me.",
                    ""
    ]

    print("\n".join(credits_text))
    for name, contact in credits_and_contact.items():
        print(f"{name: <10} - {contact}")

def print_license():
    license_text = [
        "Thsi project is open source and licensed under the Apache License 2.0",
        "For More info see:",
        "http://www.apache.org/licenses/LICENSE-2.0",
        "or ./LICENSE.md"
    ]
    print("\n".join(license_text))

def print_start_message():
    start_message = [
        f"C++ Live Interpreter (v:{version} / {date})",
        get_sys_info(),
        'Type "help", "copyright", "credits" or "license" for more information.',
        'Type "exit" to exit.'
    ]
    print(*start_message, sep="\n")

def color_print_code(code: list[str]):
    # ANSI escape codes for syntax highlighting
    COLOR_KEYWORD = '\033[94m'  # Blue
    COLOR_TYPE = '\033[95m'     # Magenta
    COLOR_FUNC = '\033[93m'     # Yellow
    COLOR_STRING = '\033[92m'   # Green
    COLOR_COMMENT = '\033[90m'  # Dark grey
    COLOR_NUMBER = '\033[96m'   # Cyan
    COLOR_RESET = '\033[0m'     # Reset to default

    # Regular expressions for C++ syntax elements
    keywords = r'\b(asm|auto|break|case|catch|class|const|const_cast|continue|default|delete|do|else|enum|explicit|export|extern|for|friend|goto|if|mutable|namespace|new|operator|private|protected|public|register|reinterpret_cast|return|sizeof|static|static_cast|struct|switch|template|this|throw|try|typedef|typeid|typename|union|using|virtual|volatile|while|alignas|alignof|constexpr|decltype|noexcept|nullptr|static_assert|thread_local|override|final|import|module|co_await|co_return|co_yield|concept|requires|consteval|constinit)\b'
    types = r'\b(void|char|short|int|long|float|double|bool|unsigned|signed|size_t|string)\b'
    funcs = r'\b(main|printf|scanf|cout|cin|endl|std|getline|reinterpret_cast|static_cast|dynamic_cast|const_cast|typeid|sizeof|alignof|decltype|noexcept|throw|delete|new|operator|explicit|friend|inline|mutable|namespace|private|protected|public|template|this|virtual|volatile|auto|bool|break|case|catch|char|class|const|constexpr|continue|default|do|else|enum|extern|false|for|goto|if|register|return|short|signed|static|struct|switch|typedef|union|unsigned|using|wchar_t|while)\b'
    numbers = r'\b\d+\b'
    strings = r'\".*?\"'
    comments = r'//.*?$|/\*.*?\*/'

    # Function to apply color to matches
    def colorize(match, color_code):
        return f'{color_code}{match.group(0)}{COLOR_RESET}'

    # Apply syntax highlighting
    for line in code:
        # String literals
        line = re.sub(strings, lambda match: colorize(match, COLOR_STRING), line)
        
        # Comments (both single line and multi-line)
        line = re.sub(comments, lambda match: colorize(match, COLOR_COMMENT), line, flags=re.MULTILINE|re.DOTALL)
        
        # Keywords
        line = re.sub(keywords, lambda match: colorize(match, COLOR_KEYWORD), line)
        
        # Types
        line = re.sub(types, lambda match: colorize(match, COLOR_TYPE), line)
        
        # Functions
        line = re.sub(funcs, lambda match: colorize(match, COLOR_FUNC), line)
        
        # Numbers
        line = re.sub(numbers, lambda match: colorize(match, COLOR_NUMBER), line)

        # Print the syntax-highlighted line
        print(line)

def get_compiler() -> str:
    #detect if Clang or GCC is installed
    #return "clang" or "gcc"
    #prefer clang because it is faster
    
    try:
        popen = subprocess.Popen(["clang", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen.wait()
        if popen.returncode == 0:
            return "clang"
    except:
        return "g++" 
    finally:
        return "g++" 


def main(code = None):
    print_start_message()
    
    if code is not None:
        previous_code = code
    else:
        previous_code = []
    while True:
        line = input(">>> ")
        
        match line:
            case "exit":
                return 0
            case "help":
                print_help()
            case "credits":
                print_credits()
            case "license":
                print_license()
            case "version":
                print(version, date, sep=" / ")
            case "run":
                run_cpp_code(previous_code)
            case "":
                run_cpp_code(previous_code)
            case "end":
                run_cpp_code(previous_code)
                previous_code = []
            case "pop":
                if len(previous_code) > 0:
                    previous_code.pop()
                else:
                    print("No code to pop")
            case "clear":
                os.system("cls")
                previous_code = []
                print_start_message()
            case "show":
                color_print_code(previous_code)
            case _:
                previous_code.append(line)


if __name__ == "__main__":
    args = sys.argv[1:]
    built_in_commands = ["help", "credits", "license", "version"]
    if len(args) > 0:
        if args[0] in built_in_commands:
            match args[0]:
                case "help":
                    print_help()
                case "credits":
                    print_credits()
                case "license":
                    print_license()
                case "version":
                    print(version, date, sep=" / ")
        else:
            main(args)
    else:
        main()