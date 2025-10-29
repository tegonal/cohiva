def pluralize(count, singular, plural):
    if count == 1:
        return f"1 {singular}"
    return f"{count} {plural}"
