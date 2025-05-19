from django.urls import URLPattern, URLResolver, get_resolver

def normalize_path(path):
    """Ensure the path starts with a slash and doesn't end with one unless root."""
    return "/" + path.lstrip("/")

def should_exclude_path(path, exclude_prefixes):
    if not exclude_prefixes:
        return False

    normalized_path = normalize_path(path)

    for prefix in exclude_prefixes:
        normalized_prefix = normalize_path(prefix)
        if normalized_path.startswith(normalized_prefix):
            return True
    return False

def collect_urlpatterns(urlpatterns, prefix='', exclude_prefixes=None):
    collected = []

    for pattern in urlpatterns:
        raw_pattern = str(pattern.pattern)
        full_path = prefix + raw_pattern
        full_path = full_path.replace("^", "")

        if isinstance(pattern, URLPattern):
            if should_exclude_path(full_path, exclude_prefixes):
                continue
            else:
                collected.append((full_path, pattern))

        elif isinstance(pattern, URLResolver):
            nested_prefix = prefix + raw_pattern
            nested_prefix = nested_prefix.replace("^", "")
            collected.extend(
                collect_urlpatterns(pattern.url_patterns, prefix=nested_prefix, exclude_prefixes=exclude_prefixes)
            )

    return collected


def get_all_urlpatterns(exclude_prefixes=None):
    resolver = get_resolver()
    return collect_urlpatterns(resolver.url_patterns, exclude_prefixes=exclude_prefixes)
