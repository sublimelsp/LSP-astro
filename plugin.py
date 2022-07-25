from LSP.plugin.core.typing import Tuple
from lsp_utils import NpmClientHandler
import os


def plugin_loaded():
    LspAstroPlugin.setup()


def plugin_unloaded():
    LspAstroPlugin.cleanup()


class LspAstroPlugin(NpmClientHandler):
    package_name = __package__
    server_directory = "language-server"
    server_binary_path = os.path.join(
        server_directory,
        "node_modules",
        "@astrojs",
        "language-server",
        "bin",
        "nodeServer.js",
    )

    @classmethod
    def minimum_node_version(cls) -> Tuple[int, int, int]:
        return (14, 0, 0)
