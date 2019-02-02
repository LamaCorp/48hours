def get_available(what, where):
    names = []

    for file in os.listdir(where):
        name = os.path.basename(file)
        match = what.match(name)
        if match:
            names.append(match.group(1).title())

    return sorted(names)

get_available_levels = ["level_0"]