from rich.syntax import Syntax
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich import print as rprint

import subprocess
import os
import sys
import platform
import json
import time


version = "r0.1-alpha"
date = "2023-11-28"


def compile(input_file:str, output_file:str):

    curr_settings = load_settings()
    compiler = curr_settings["compiler"]
    
    cmd = f"{compiler} -o {output_file} {input_file}"
    
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

    output = popen.stdout.read().decode()
    error = popen.stderr.read().decode()
    
    rprint(Text(output, style="bold"))
    if error != "":
        rprint(Text(error, style="bold red"))

    exit_code = popen.returncode
    t_finish_run = time.time()
    print(f"programm exited with code {exit_code} (0x{exit_code:02X}) after {t_finish_run - t_start:.3f}s (compile: {t_finish_compile - t_start:.2f}s, run: {t_finish_run - t_finish_compile:.2f}s)")

def insert_code_and_clean_up(code:list[str]) -> list[str]:
    # Insert code into template and clean up
    # like adding #include <iostream> and removing comments

    includes = ["#include <iostream>"]
    for line in code:
        if line.startswith("#include") and line not in includes:
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

    #check if a main() function is already defined
    main_function_exists = False
    for line in code:
        if line.startswith("int main"):
            main_function_exists = True
            break
    
    if main_function_exists:
        #remove "int main()" from template
        idx = template_lines.index("int main() {")
        template_lines.pop(idx)
    
    code = template_lines + code
    
    if not main_function_exists:
        code.append("}")
       
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
        "settings*": "Show and edit settings",
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
    #using rich library instead of the old custom regex method
    
    curr_settings = load_settings()
    
    code = "\n".join(code)
    
    theme = curr_settings["theme"]
    line_numbers = curr_settings["line_numbers"]
    word_wrap = curr_settings["word_wrap"]
    background_color = curr_settings["background_color"]
    syntax = Syntax(code,
                    lexer="cpp",
                    theme=theme,
                    line_numbers=line_numbers,
                    word_wrap=word_wrap,
                    background_color=background_color
                    )
    
    console = Console()
    
    console.print(syntax)


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

def settings():
    
    availible_themes = [
        "algol", "algol_nu", "arduino", "autumn", "borland", "abap", "colorful", "igor", "lovelace", "murphy", "pastie", "rainbow_dash", "stata-light", "trac", "vs", "emacs", "tango", "solarized-light", "manni", "gruvbox-light", "friendly", "friendly_grayscale", "perldoc", "paraiso-light", "zenburn", "nord", "material", "one-dark", "dracula", "nord-darker", "gruvbox-dark", "stata-dark", "paraiso-dark", "solarized-dark", "native", "inkpot", "fruity", "vim"
    ]
    
    curr_settings = load_settings()
    rprint(Markdown("## Current settings"))
    for key, value in curr_settings.items():
        print(f"{key: <20} - {value}")
    
    cmd_dict = { #command: description
                "help": "Show this help message",
                "save": "Save the current settings",
                "reset": "Reset the settings to default",
                "exit": "Exit the settings menu",
                "set [key] [value]": "Set a setting to a value"
                }

    rprint(Markdown("## Commands"))
    
    for cmd, desc in cmd_dict.items():
        print(f"{cmd: <20} - {desc}")
    
    line = ""
    while True:
        line = input("s>> ")
        if line == "exit" or [ord(char) for char in line] == [24]: #weird windows specific ctrl+x char
            break
        elif line == "help":
            rprint(Markdown("## Available settings"))
            
            availible_settings = { #settings: availible values
                "compiler": ["clang", "g++"],
                "theme": availible_themes,
                "line_numbers": ["True", "False"],
                "word_wrap": ["True", "False"],
                "background_color": ["any hex color code"]
            }
            
            for setting, values in availible_settings.items():
                rprint(Markdown(f"**{setting}**"), ', '.join(values))
                print()
            
            rprint(Markdown("## Commands"))
            for cmd, desc in cmd_dict.items():
                print(f"{cmd: <20} - {desc}")
            
        elif line == "save" or [ord(char) for char in line] == [19]: #weird windows specific ctrl+s char
            save_settings(curr_settings)
            print("Settings saved")
            
        elif line == "reset" or [ord(char) for char in line] == [18]: #weird windows specific ctrl+r char
            curr_settings = {
                "compiler": get_compiler(),
                "theme": "solarized-dark",
                "line_numbers": True,
                "word_wrap": True,
                "background_color": "#2E3440"
            }
            save_settings(curr_settings)
            print("Settings reset to default")
            
        elif line.startswith("set"):
            key, value = line.split(" ")[1:]
            if key in curr_settings:
                if value == "True":
                    value = True
                elif value == "False":
                    value = False
                curr_settings[key] = value
            else:
                print("Invalid key")
        
        else:
            print([ord(char) for char in line])
            print("Invalid command")
        
        print("Current settings:")
        for key, value in curr_settings.items():
            print(f"{key: <15} - {value}")



def load_settings():
    with open("settings.json", "r") as f:
        settings = json.load(f)
    return settings

def save_settings(settings:dict):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

def main(code = None):
    print_start_message()

    short_cuts = {
        chr(24): "exit", #ctrl+x
        chr(19): "save", #ctrl+s
        chr(18): "reset", #ctrl+r
    }
    

    if code is not None:
        previous_code = code
    else:
        previous_code = []
    while True:
        line = input(">>> ")

        
        if line in short_cuts:
            line = short_cuts[line]
        
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
            case "settings":
                settings()
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
                # Different commands between OS
                if platform.system() in ['Linux', 'Darwin']:
                    os.system("clear")
                else:
                    os.system("cls")
                previous_code = []
                print_start_message()
            case "show":
                color_print_code(previous_code)
            case "_load_sample":
                with open("./sample.cpp", "r") as f:
                    previous_code = f.readlines()
            case _:
                previous_code.append(line)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    if not os.path.exists("settings.json"):
        curr_settings = {
            "compiler": get_compiler(),
            "theme": "solarized-dark",
            "line_numbers": True,
            "word_wrap": True,
        }
        save_settings(curr_settings)
    else:
        curr_settings = load_settings()
    
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