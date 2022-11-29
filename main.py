import json
import os
import sys
from platform import system
from enum import Enum, auto

class Reversative(Enum):
    reverse = auto()
    force_reverse = auto()
    no = auto()

def light_pattern(pattern: str, key: str) -> str:
    return pattern.replace(key, "\033[32m{}\033[0m".format(key))

def procced_reverse(pattern: list[str] | str, key: str) -> list[str] | str | None:
    if isinstance(pattern, list):
        if any(map(lambda x: key in x, pattern)):
            return list(map(lambda x: light_pattern(x, key), pattern))
    if key in pattern:
        return light_pattern(pattern, key) # type: ignore

JsonConfigAsDict = dict[str, dict[str, str | list[str] | dict[str, str]]]

def dive_in(dive: JsonConfigAsDict, req: str, reverse: Reversative) -> JsonConfigAsDict:
    result : JsonConfigAsDict = {}
    for key in dive.keys():
        if req in key and reverse != Reversative.force_reverse:
            colored_key = light_pattern(key, req)
            result[colored_key] = dive[key]
        elif isinstance(dive[key], dict):
            deep = dive_in(dive[key], req, reverse)
            if deep:
                result[key] = deep
        elif reverse in [Reversative.force_reverse, Reversative.reverse]:
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

ERASE_TOP_AND_MOVE = '\x1b[1A\x1b[2K'

def main():
    with open(os.path.join(script_path, 'help.json'), 'r') as help:
        helper : JsonConfigAsDict = json.load(help)
    request : str = ''

    commands_history : list[str] = []

    while request != "exit":

        if request == "reread":
            with open(os.path.join(script_path, 'help.json'), 'r') as help:
                helper : JsonConfigAsDict = json.load(help)
            os.system(cross_commands[platform]["clear"])

        request = input("Enter request: ")

        if not request:
            request = "helper"

        add_to_history = True

        if request.startswith('!'):
            try:
                request = commands_history[-1 * request.count('!')] + request.lstrip('!')
                print(ERASE_TOP_AND_MOVE, f'Enter request: {request}', sep='')
                add_to_history = False
            except IndexError:
                print("Out of requests!")
                request = '-h'


        if request.startswith('-h'):
            try:
                index = int(request.strip('-h'))
                if index < len(commands_history):
                    request = commands_history[index]
                    print(ERASE_TOP_AND_MOVE, f'Enter request: {request}', sep='')
                    add_to_history = False
            except ValueError:
                print('\n', '\n'.join(f"{k} {c}" for k,c in enumerate(commands_history)), '\n',sep='')
                continue
        if add_to_history:
            commands_history.append(request)
        if request in cross_commands[platform]:
            os.system(cross_commands[platform][request])
            continue

        reverse_option = Reversative.no
        if (x := request.strip(' ')).endswith('-r') or x.endswith('-fr'):
            reverse_option = Reversative.reverse if x.endswith('-r') else Reversative.force_reverse
            request = request.rstrip('-r').rstrip('-fr')

        print()
        result = dive_in(helper, request.strip().lower(), reverse_option)
        print_dict(result, indent=1)
        print('\n')
    sys.exit(0)


if __name__ == "__main__":
    main()
