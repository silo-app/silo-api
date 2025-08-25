import fnmatch


def match_any_permission(
    method: str, path: str, permissions: dict[str, list[str]]
) -> bool:
    method = method.upper()
    allowed = permissions.get(method, [])
    for pattern in allowed:
        pat = pattern if pattern.startswith("/") else f"/{pattern}"
        if fnmatch(path, pat):
            return True
    return False
