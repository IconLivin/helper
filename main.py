#!/usr/bin/python3

import json
import os
import sys
from platform import system
from enum import Enum, auto
import re

class Reversative(Enum):
    reverse = auto()
    force_reverse = auto()
    no = auto()

def light_pattern(pattern: str, key: str) -> str:
    return pattern.replace(key, COLOR.format(key))

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
            deep = dive_in(dive[key], req, reverse) # type: ignore
            if deep:
                result[key] = deep # type: ignore
        elif reverse in [Reversative.force_reverse, Reversative.reverse]:
            matched_pattern = procced_reverse(dive[key], req) # type: ignore
            if matched_pattern:
                result[key] = matched_pattern # type: ignore
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
COLOR = "{}"
SPECIAL_CHAR = '\x1b'

def main():
    global COLOR
    with open(os.path.join(script_path, 'help.json'), 'r') as help,\
        open(os.path.join(script_path, 'color_config.json'), 'r') as color_config:
        helper : JsonConfigAsDict = json.load(help)
        colors : dict[str, str] = json.load(color_config)
    border = colors.get("background", {}).get("Default", "{}")
    COLOR = "\033" + border + "\033" + colors.get("text", {}).get("Default", "{}") + "{}\033[0m"
    request : str = ''


    commands_history : list[str] = []

    while request != "exit":

        if request == "cchange":
            os.system(cross_commands[platform]["clear"])
            print("{:<17} {:<35}".format("TEXT COLOR", "BORDER"))
            for (text, text_color), (bg, bg_color) in zip(colors.get("text", {}).items(), colors.get("background", {}).items()):
                new_color = SPECIAL_CHAR + text_color + "{}\x1b[0m"
                new_border = SPECIAL_CHAR + bg_color + "{}\x1b[0m"
                print("{:<26} {:<35}".format(new_color.format(text), new_border.format(bg)))

            print(f'\n{COLOR.format("CURRENT PATTERN")}')
            color = SPECIAL_CHAR + colors.get('text', {}).get('Default', '') + "{}\x1b[0m"
            new_color = input(f"\nType new text color, {color.format('CURRENT TEXT')} (skip): ")
            if new_color in colors.get("text", {}):
                colors["text"]["Default"] = colors["text"][new_color]
                COLOR = SPECIAL_CHAR + colors["text"][new_color] + "{}\033[0m"
                print('\x1b[3A\x1b[2K', f'{COLOR.format("CURRENT PATTERN")}', sep='', end='\n\n\n')
            border  = SPECIAL_CHAR + colors.get('background', {}).get('Default', '') + "{}\x1b[0m"
            new_border = input(f"Type new text border, {border.format('CURRENT BORDER')} (skip): ")
            if new_border in colors.get("background", {}):
                colors["background"]["Default"] = colors["background"][new_border]
                COLOR = SPECIAL_CHAR + colors["background"]["Default"] + SPECIAL_CHAR + colors["text"]["Default"] + "{}" + "\x1b[0m"
                print('\x1b[4A\x1b[3K\x1b', f'{COLOR.format("CURRENT PATTERN")}', sep='', end='\n\n\n\n')
            update_conf = input("Update default value on config (y/n): ")
            if update_conf == 'y':
                with open(os.path.join(script_path, 'color_config.json'), 'w') as color_config:
                    json.dump(colors, color_config, indent=4)
            os.system(cross_commands[platform]["clear"])

        if request == "reread":
            with open(os.path.join(script_path, 'help.json'), 'r') as help:
                helper : JsonConfigAsDict = json.load(help)
            os.system(cross_commands[platform]["clear"])

        request = input("Enter request: ")
        request = re.sub(r"\x1b\[A", "!", request).strip()

        if not request:
            request = "helper"

        add_to_history = True

        if request.startswith('!'):
            try:
                request = commands_history[-1 * request.count('!')] + request.lstrip('!')
                add_to_history = False
            except IndexError:
                print("Out of requests!")
                request = '-h'


        if request.startswith('-h'):
            try:
                index = int(request.strip('-h'))
                if index < len(commands_history):
                    request = commands_history[index]
                    add_to_history = False
            except ValueError:
                print('\n', '\n'.join(f"{k} {c}" for k,c in enumerate(commands_history)), '\n',sep='')
                continue
        if add_to_history:
            commands_history.append(request)
        if request in cross_commands[platform]:
            os.system(cross_commands[platform][request])
            continue

        print(ERASE_TOP_AND_MOVE, f"Enter request: {COLOR.format(request)}", sep='')
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
