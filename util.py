def strip_indented_string(value: str) -> str:
    """Strip shortest whitespace prefix from each line"""

    shortest_prefix: int | None = None
    for line in value.splitlines():
        if line.strip() != "":
            prefix_len = len(line) - len(line.lstrip())
            if shortest_prefix is None:
                shortest_prefix = prefix_len
            else:
                shortest_prefix = min(shortest_prefix, prefix_len)

    return "\n".join(line[shortest_prefix:] for line in value.splitlines())
