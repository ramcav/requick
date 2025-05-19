import click
from httpgen.django_plugin.django_loader import load_django_project
from httpgen.utils import get_all_urlpatterns

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--exclude-prefix', default=None, multiple=True, help='Exclude URL paths that start with this prefix')
def main(project_path, exclude_prefix):
    """Scan a Django project and print its URL patterns"""
    load_django_project(project_path)

    urls = get_all_urlpatterns(exclude_prefixes=exclude_prefix)
    for path, pattern in urls:
        view = pattern.callback
        print(f"{path}  =>  {view.__module__}.{view.__name__}")

if __name__ == "__main__":
    main()