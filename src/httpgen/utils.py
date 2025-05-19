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
                info = extract_view_metadata(pattern)
                info["path"] = full_path
                collected.append(info)

        elif isinstance(pattern, URLResolver):
            nested_prefix = prefix + raw_pattern
            nested_prefix = nested_prefix.replace("^", "")
            collected.extend(
                collect_urlpatterns(pattern.url_patterns, prefix=nested_prefix, exclude_prefixes=exclude_prefixes)
            )
    return collected

def extract_view_metadata(pattern: URLPattern):
    callback = pattern.callback

    # DRF: class-based views
    if hasattr(callback, 'cls'):
        view_cls = callback.cls
        view_name = view_cls.__name__
        view_module = view_cls.__module__

        # Extract supported HTTP methods
        methods = [
            method.upper() for method in ['get', 'post', 'put', 'patch', 'delete']
            if hasattr(view_cls, method)
        ]

        # Extract serializer if DRF-style
        serializer_class = getattr(view_cls, 'serializer_class', None)

    else:
        # Function-based view
        view_name = getattr(callback, '__name__', str(callback))
        view_module = getattr(callback, '__module__', 'unknown')
        methods = getattr(callback, 'allowed_methods', ['GET'])  # fallback
        serializer_class = None

    return {
        "view": callback,
        "view_name": view_name,
        "view_module": view_module,
        "methods": methods,
        "serializer": serializer_class,
    }


def get_all_urlpatterns(exclude_prefixes=None):
    resolver = get_resolver()
    return collect_urlpatterns(resolver.url_patterns, exclude_prefixes=exclude_prefixes)

def pretty_print_route(route):
    path = route["path"]
    methods = ", ".join(route.get("methods", ["GET"]))
    view_str = f"{route['view_module']}.{route['view_name']}"
    serializer = route.get("serializer")
    serializer_str = (
        f"{serializer.__module__}.{serializer.__name__}"
        if serializer else "None"
    )

    print(f"✅ {methods} /{path.lstrip('/')}")
    print(f"   → {view_str}")
    print(f"   Serializer: {serializer_str}\n")