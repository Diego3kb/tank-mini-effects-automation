"""Listar portas MIDI detectadas no Windows sem enviar comandos ao pedal."""

import ctypes


def ports(api: ctypes.WinDLL, direction: str) -> list[str]:
    count = getattr(api, f"midi{direction}GetNumDevs")()
    get_caps = getattr(api, f"midi{direction}GetDevCapsW")
    names = []
    for index in range(count):
        buffer = ctypes.create_string_buffer(256)
        status = get_caps(index, buffer, len(buffer))
        if status:
            names.append(f"{index}: erro {status}")
        else:
            name = buffer.raw[8:72].decode("utf-16le", errors="ignore").split("\0", 1)[0]
            names.append(f"{index}: {name}")
    return names


def main() -> None:
    api = ctypes.WinDLL("winmm")
    for direction, title in (("In", "entradas"), ("Out", "saidas")):
        found = ports(api, direction)
        print(f"MIDI {title}: {len(found)}")
        for line in found:
            print(f"  {line}")


if __name__ == "__main__":
    main()
