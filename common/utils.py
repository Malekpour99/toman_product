def normalize_size(size: int) -> str:
    """
    Normalizes file or volume sizes and returns it with the proper suffix,
    showing the decimal only if it's non-zero.
    """
    size = float(size)
    if size < 1024:
        return f"{int(size)} B" if size.is_integer() else f"{size:.1f} B"
    elif size < 1024 * 1024:
        size_kb = size / 1024
        return f"{int(size_kb)} KB" if size_kb.is_integer() else f"{size_kb:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        size_mb = size / (1024 * 1024)
        return f"{int(size_mb)} MB" if size_mb.is_integer() else f"{size_mb:.1f} MB"
    else:
        size_gb = size / (1024 * 1024 * 1024)
        return f"{int(size_gb)} GB" if size_gb.is_integer() else f"{size_gb:.1f} GB"
