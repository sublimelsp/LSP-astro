from pathlib import Path
from lsp_utils import NpmClientHandler


def plugin_loaded():
    LspAstroPlugin.setup()


def plugin_unloaded():
    LspAstroPlugin.cleanup()


class LspAstroPlugin(NpmClientHandler):
    package_name = __package__
    server_directory = "language-server"
    server_binary_path = Path(
        server_directory, "node_modules", "@astrojs", "language-server", "bin", "nodeServer.js"
    )

    @classmethod
    def is_allowed_to_start(cls, window, initiating_view, workspace_folders, configuration):
        if configuration is None:
            return

        # prefer explicit `typescript.tsdk` from LSP-astro.sublime-settings
        if configuration.init_options.get("typescript.tsdk"):
            return

        typescript_path = None
        typescript_relpath = Path("node_modules", "typescript", "lib")

        def find_typescript_path(path):
            """
            Find typescript in the package specified ``path`` belongs to.

            :param path:
                The absolute path of a directory to use as starting point

            :returns:
                The absolute path to typescript language-server if exists.
            """
            for root in (path, *path.parents):
                if (root / "package.json").is_file():
                    typescript_path = root / typescript_relpath
                    if typescript_path.is_dir():
                        return typescript_path

            return None

        # try to find package root and typescript based on current file to support
        # nested packages, which are not directly added as folder to sidebar
        if initiating_view:
            file_name = initiating_view.file_name()
            if file_name:
                typescript_path = find_typescript_path(Path(file_name).parent)

        # try to find typescript from first workspace folder
        if not typescript_path and workspace_folders:
            typescript_path = find_typescript_path(Path(workspace_folders[0].path))

        # use typescript bundled with LSP-astro
        if not typescript_path:
            bundled_path = Path(cls._server_directory_path(), typescript_relpath)
            if bundled_path.is_dir():
                typescript_path = bundled_path

        if not typescript_path:
            return

        configuration.init_options.set("typescript.tsdk", str(typescript_path))

    @classmethod
    def minimum_node_version(cls):
        return (14, 0, 0)
