import sys
import django
import ast
import os

def find_settings_module(project_path: str) -> str:
    """
    Parse manage.py using AST to extract DJANGO_SETTINGS_MODULE assignment.
    Works even if inside functions. Includes debug output.
    """
    manage_path = os.path.join(project_path, 'manage.py')
    print(f"🔍 Looking for manage.py at: {manage_path}")

    if not os.path.isfile(manage_path):
        raise FileNotFoundError("❌ Could not find manage.py in the provided project path.")

    with open(manage_path) as f:
        source = f.read()

    print("📄 Successfully loaded manage.py. Parsing with AST...")

    try:
        tree = ast.parse(source, filename="manage.py")
    except SyntaxError as e:
        print(f"❌ Syntax error while parsing manage.py: {e}")
        raise

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "setdefault"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "environ"
            ):
                args = node.args
                if len(args) >= 2:
                    key_arg, value_arg = args[0], args[1]
                    if (
                        isinstance(key_arg, ast.Constant)
                        and key_arg.value == "DJANGO_SETTINGS_MODULE"
                        and isinstance(value_arg, ast.Constant)
                    ):
                        print(f"✅ Found DJANGO_SETTINGS_MODULE: {value_arg.value}")
                        return value_arg.value

    print("⚠️ Could not find DJANGO_SETTINGS_MODULE in manage.py")
    raise RuntimeError("❌ Could not determine DJANGO_SETTINGS_MODULE from manage.py")



def load_django_project(project_path: str):
    """
    Dynamically configure Django environment from the outside.
    """
    project_path = os.path.abspath(project_path)
    sys.path.insert(0, project_path)

    settings_module = find_settings_module(project_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    django.setup()
