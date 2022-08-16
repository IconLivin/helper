import json
import os
import sys
from platform import system

def light_pattern(pattern: str, key: str) -> str:
    return pattern.replace(key, color_scheme[platform].format(key))

def procced_reverse(pattern: list | str, key: str) -> list | str:
    if isinstance(pattern, list):
        if any(map(lambda x: key in x, pattern)):
            return list(map(lambda x: light_pattern(x, key), pattern))
    if key in pattern:
        return light_pattern(pattern, key)


def dive_in(dive: dict, req: str, reverse: bool) -> dict:
    result = {}
    for key in dive.keys():
        if req in key:
            colored_key = light_pattern(key, req)
            result[colored_key] = dive[key]
        elif isinstance(dive[key], dict):
            deep = dive_in(dive[key], req, reverse)
            if deep:
                result[key] = deep
        elif reverse:
            matched_pattern = procced_reverse(dive[key], req)
            if matched_pattern:
                result[key] = matched_pattern
    return result


def print_dict(answer: dict, indent: int) -> None:
    for key in answer:
        if isinstance(answer[key], dict):
            print(f'{"  " * indent}{key}:')
            print_dict(answer[key], indent+1)
            continue
        elif isinstance(answer[key], list):
            print(f'{"  " * indent}{key}:')
            print_list(answer[key], indent + 1)
            continue
        print(f'{"  " * indent}{key}: {answer[key]}')


def print_list(answer: list, indent: int = 0) -> None:
    for ans in answer:
        if isinstance(ans, dict):
            print_dict(ans, indent)
            continue
        print('  ' * indent, ans)

script_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])

platform = system()

color_scheme = {
    "Linux" : "\033[32m{}\033[0m",
    "Windows" : "{}"
}

cross_commands = {
    "Linux" : {
        "clear" : "clear",
        "upscr" : "nvim ~/helper"
    },
    "Windows" : {
        "clear" : "cls",
        "upscr" : "code ."
    }
}



def main():
    with open(os.path.join(script_path, 'help.json'), 'r') as help:
        helper = json.load(help)
    request = ''

    commands_history = []

    while request != "exit":

        if request == "reread":
            with open(os.path.join(script_path, 'help.json'), 'r') as help:
                helper = json.load(help)
            os.system(cross_commands[platform]["clear"])

        request = input("Enter request: ")
        
        if not request:
            continue
        
        commands_history.append(request)

        if request.startswith('-h'):
            try:
                index = int(request.strip('-h'))
                if index < len(commands_history):
                    request = commands_history[index]
            except ValueError:
                print('\n', '\n'.join(f"{k} {c}" for k,c in enumerate(commands_history)), '\n',sep='')
                continue

        if request in cross_commands[platform]:
            os.system(cross_commands[platform][request])
            continue

        reverse = True if '-r' in request else False
        request = [r for r in request.split('-r') if r][0]
        print()
        result = dive_in(helper, request.strip().lower(), reverse)
        print_dict(result, indent=1)
        print('\n')
    sys.exit(0)


if __name__ == "__main__":
    main()
