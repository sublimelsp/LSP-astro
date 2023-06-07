import os

from lsp_utils import NpmClientHandler


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

    typescript_relpath = os.path.join(
        'node_modules',
        'typescript',
        'lib',
        'tsserverlibrary.js'
    )

    @classmethod
    def find_typescript_path(cls, path):
        """
        Find typescript in the package specified ``path`` belongs to.

        :param path:
            The absolute path of a directory to use as starting point

        :returns:
            The absolute path to typescript language-server if exists.
        """
        name = True  # to get started with loop
        while path and name:
            if os.path.isfile(os.path.join(path, 'package.json')):
                typescript_path = os.path.join(path, cls.typescript_relpath)
                if os.path.isfile(typescript_path):
                    return typescript_path
                break

            path, name = os.path.split(path)

        return None

    @classmethod
    def is_allowed_to_start(cls, window, initiating_view, workspace_folders, configuration):
        if configuration is None:
            return

        if configuration.init_options.get('typescript.serverPath'):
            return  # don't find the `typescript.serverPath` if it was set explicitly in LSP-astro.sublime-settings

        typescript_path = None

        # try to find package root and typescript based on current file to support
        # nested packages, which are not directly added as folder to sidebar
        if initiating_view:
            file_name = initiating_view.file_name()
            if file_name:
                typescript_path = cls.find_typescript_path(os.path.dirname(file_name))

        # try to find typescript from first workspace folder
        if workspace_folders and not typescript_path:
            typescript_path = cls.find_typescript_path(workspace_folders[0].path)

        # use typescript bundled with LSP-astro
        if not typescript_path:
            typescript_path = os.path.join(cls._server_directory_path(), cls.typescript_relpath)

        if not typescript_path:
            return

        configuration.init_options.set('typescript.serverPath', typescript_path)
        configuration.init_options.set('typescript.tsdk', os.path.dirname(typescript_path))

    @classmethod
    def minimum_node_version(cls):
        return (14, 0, 0)
