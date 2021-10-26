def yes_or_no(msg: str) -> bool:
    answer = input(f"{msg} [y/N]: ").lower()
    if answer.startswith("y"):
        return True
    else:
        return False
