from __future__ import annotations

from pathlib import Path, WindowsPath

from LSP.plugin import LspPlugin, OnPreStartContext
from lsp_utils import NodeManager
from sublime_lib import ResourcePath
from typing_extensions import override

__all__ = ["LspAstroPlugin", "plugin_loaded", "plugin_unloaded"]


def plugin_loaded() -> None:
    LspAstroPlugin.register()


def plugin_unloaded() -> None:
    LspAstroPlugin.unregister()


class LspAstroPlugin(LspPlugin):

    @classmethod
    @override
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        package_name = cls.plugin_storage_path.name
        server_directory_path = NodeManager.on_pre_start_async(
            context,
            cls.plugin_storage_path,
            ResourcePath('Packages', package_name, 'language-server'),
            Path('node_modules', '@astrojs', 'language-server', 'bin', 'nodeServer.js'),
            node_version_requirement='>=14',
        )

        # prefer explicit `typescript.tsdk` from LSP-astro.sublime-settings
        if not context.configuration.initialization_options.get("typescript.tsdk"):
            typescript_path = None
            typescript_relpath = Path("node_modules", "typescript", "lib")

            def find_typescript_path(path: Path) -> Path | None:
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
            if context.view and (file_name := context.view.file_name()):
                    typescript_path = find_typescript_path(Path(file_name).parent)

            # try to find typescript from first workspace folder
            if not typescript_path and context.workspace_folders:
                typescript_path = find_typescript_path(Path(context.workspace_folders[0].path))

            # use typescript bundled with LSP-astro
            if not typescript_path and server_directory_path:
                bundled_path = server_directory_path / typescript_relpath
                if bundled_path.is_dir():
                    typescript_path = bundled_path

            if typescript_path:
                # Escape Windows path separators
                # see: https://github.com/sublimelsp/LSP-astro/issues/120
                value = str(typescript_path)
                if isinstance(typescript_path, WindowsPath):
                    value = value.replace("\\", "\\\\")
                context.configuration.initialization_options.set("typescript.tsdk", value)
