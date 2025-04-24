import pytest
import py
import glob
import subprocess
import time
import os
import sys
import pathlib
import shutil

from . import runresult
from . import runresulterror
from . import checkoutput


@pytest.fixture
def testdirectory(tmpdir):
    """Creates the py.test fixture to make it usable withing the unit tests.
    See the TestDirectory class for more information.
    """
    return TestDirectory(tmpdir=pathlib.Path(str(tmpdir)))


class TestDirectory:
    """Testing code by invoking executable which potentially creates and deletes
    files and directories can be hard and error prone.

    The purpose of this module is to simplify this task.

    To make it easy to use in with pytest the TestDirectory object can be
    injected into a test function by using the testdirectory fixture.

    Example::

        def test_this_function(testdirectory):
            images = testdirectory.mkdir('images')
            images.copy_files('test/images/*')

            r = testdirectory.run('imagecompress --path=images')

            # r is an RunResult object containing information about the command
            # we just executed
            assert r.returncode == 0


    The testdirectory is an instance of TestDirectory and represents an actual
    temporary directory somewhere on the machine running the test code. Using
    the API we can create additional temporary directories, populate them with
    an initial set of files and finally run some executable and observe its
    behavior.

    Inspiration:
     - http://search.cpan.org/~sanbeg/Test-Directory-0.041/lib/Test/Directory.pm
     - pytest internal plugin for doing the same thing:
           https://github.com/pytest-dev/pytest/blob/master/_pytest/capture.py

    """

    def __init__(self, tmpdir):
        """Create a new TestDirectory instance.

        :param tmpdir: The temporary directory as a py.path.local instance or str.
        """
        self.tmpdir = tmpdir

    @staticmethod
    def from_path(path):
        """Create a new TestDirectory instance from a path.

        :param path: The path as a string or pathlib.Path object.
        """
        path = pathlib.Path(path)

        if not path.is_dir():
            raise ValueError(f"{path} does not exist or is not a directory")

        return TestDirectory(tmpdir=path)

    def mkdir(self, directory):
        """Create a sub-directory in the temporary / test dir.

        :param directory: The sub-directory to create as a string or pathlib.Path.
        """
        directory = pathlib.Path(directory)

        child_directory = self.tmpdir / directory
        child_directory.mkdir(parents=True, exist_ok=True)

        return TestDirectory(tmpdir=child_directory)

    def rmdir(self):
        """Remove the directory. If the directory is not empty, remove all
        files and directories recursively."""
        if self.tmpdir.exists():
            shutil.rmtree(self.tmpdir)

        # @todo not sure if this is a good idea, but I guess the tmpdir is
        # invalid after the remove?
        self.tmpdir = None

    def join(self, *args):
        """Get a TestDirectory instance representing an existing path"""

        new_path = self.tmpdir.joinpath(*args)

        if not new_path.exists():
            raise ValueError(f"{new_path} does not exist")

        return TestDirectory(tmpdir=new_path)

    def rmfile(self, filename):
        """Remove a file.

        :param filename: The name of the file to remove as a pathlib.Path or string.
        """
        file_path = self.tmpdir / pathlib.Path(filename)

        if file_path.is_file():
            file_path.unlink()
        else:
            raise FileNotFoundError(f"{filename} does not exist or is not a file.")

    def path(self):
        """:return: The path to the temporary directory as a string"""
        return str(self.tmpdir)

    def copy_file(self, filename, rename_as=""):
        """Copy the file to the test directory. Preserve file flags.

        :param filename: The filename as a string or pathlib.Path object.
        :param rename_as: If specified rename the file represented by filename
            to the name given in rename_as as a string.
        :return: The path to the file in its new location as a pathlib.Path object.
        """
        file_path = pathlib.Path(filename)
        new_path = pathlib.Path(str(self.tmpdir)) / (
            rename_as if rename_as else file_path.name
        )
        shutil.copy2(str(file_path), str(new_path))
        return new_path

    def symlink_file(self, filename, rename_as="", relative=True):
        """Create a symlink to the file in the test directory.

        :param filename: The filename as a string. This is the original
            file we want to create a symlink to.
        :param rename_as: If specified rename the file represented by filename
            to the name given in rename_as as a string.
        :param relative: Make the symlink use a relative path to the file.
        :return: The path to the file in its new location as a string.
        """

        filename = self._expand_filename(filename=filename)

        filepath = str(py.path.local(filename))

        if relative:
            filepath = os.path.relpath(start=str(self.tmpdir), path=filepath)

        link_name = self.tmpdir.joinpath(os.path.basename(filepath))
        if rename_as:
            link_name = self.tmpdir.joinpath(rename_as)

        self._create_symlink(str(filepath), str(link_name), isdir=False)

        return str(link_name)

    def symlink_dir(self, directory, rename_as="", relative=True):
        """Create a symlink to the file in the test directory.

        :param filename: The filename as a string. This is the original
            file we want to create a symlink to.
        :param rename_as: If specified rename the file represented by filename
            to the name given in rename_as as a string.
        :param relative: Make the symlink use a relative path to the file.
        :return: The path to the file in its new location as a string.
        """

        # Make sure directory is a string
        directory = str(directory)
        directory = self._expand_filename(filename=directory)

        # Get the name of the directory:
        # https://stackoverflow.com/a/3925147/1717320
        directory_name = os.path.basename(os.path.normpath(directory))

        if relative:
            directory = os.path.relpath(start=str(self.tmpdir), path=directory)

        link_name = self.tmpdir.joinpath(directory_name)

        if rename_as:
            link_name = self.tmpdir.joinpath(rename_as)

        self._create_symlink(source=directory, link_name=str(link_name), isdir=True)

        return str(link_name)

    def copy_files(self, filename):
        """Copy files into testdirectory. Expand filename by expanding wildcards
        e.g. ``dir/*``

        :param filename: The filename as a string or pathlib.Path. This
            represents a single file or glob pattern.
        """

        # Expand filename by expanding wildcards e.g. 'dir/*', the
        # glob returns a list of files
        files = glob.glob(filename)

        for file in files:
            self.copy_file(filename=file)

    def copy_dir(self, directory):
        """Copy a directory into the test directory.

        Example (using the test fixture test_directory)::

            def test_something(test_directory):

                # Prints /tmp/pytest-9/some_test
                print(test_directory.path())

                app_dir = test_directory.copy_dir('/home/ok/app')

                # Prints /tmp/pytest-9/some_test/app
                print(app_dir.path())

        :param directory: Path to the directory as a string or pathlib.Path
        :return: TestDirectory object representing the copied directory
        """
        src_dir = pathlib.Path(directory)
        dst_dir = self.tmpdir / src_dir.name
        shutil.copytree(src_dir, dst_dir)

        return TestDirectory(tmpdir=dst_dir)

    def write_text(self, filename, data, encoding="utf-8"):
        """Writes a file in the temporary directory.

        :param filename: Filename as string or pathlib.Path
        :param data: The text data to write
        :param encoding: The encoding to use (default utf-8)
        :return: The path to the file as a pathlib.Path
        """
        file_path = self.tmpdir / pathlib.Path(filename)
        file_path.write_text(data, encoding=encoding)
        return file_path

    def write_binary(self, filename, data):
        """Writes binary data to a file in the temporary directory.

        :param filename: Filename as string or pathlib.Path
        :param data: The binary data to write
        :return: The path to the file as a pathlib.Path
        """
        file_path = self.tmpdir / pathlib.Path(filename)
        file_path.write_bytes(data)
        return file_path

    def contains_file(self, filename):
        """Checks for the existence of a file.

        :param filename: The filename to check for as a string or pathlib.Path.
                        May contain glob patterns.
        :return: True if the file is contained within the test directory.
        :raises: ValueError if there is more than one match.
        """
        matches = list(self.tmpdir.glob(filename))
        if len(matches) == 1 and matches[0].is_file():
            return True
        elif len(matches) > 1:
            raise ValueError(f"Found multiple matches for {filename}")
        else:
            return False

    def contains_dir(self, *directories):
        """Checks for the existence of a directory.

        :param dirname: The directory name to check for.
        :return: True if the directory is contained within the test directory.
        """

        # Expand filename by expanding wildcards e.g. 'dir/*/file.txt', the
        # glob should return only one file
        directories = glob.glob(os.path.join(self.path(), *directories))

        if len(directories) != 1:
            return False

        # Follow symlinks
        if not os.path.exists(directories[0]):
            return False

        return True

    def run(self, args, **kwargs):
        """Runs the command in the test directory.

        :param args: String or list of arguments
        :param kwargs: Keyword arguments passed to Popen(...)

        :return: A RunResult object representing the result of the command
        """

        if "shell" not in kwargs:
            kwargs["shell"] = True

            # The rules for how subprocess handles arguments is a bit complex we
            # typically would like to have environment variable expansion etc.
            # so we would run commands via the shell - this seems to imply that
            # the command should be passed as a string.
            if isinstance(args, list):
                args = " ".join(args)

        if "env" not in kwargs:
            # If 'env' is not passed as keyword argument use a copy of the
            # current environment.
            kwargs["env"] = os.environ.copy()

        if "stdout" not in kwargs:
            kwargs["stdout"] = subprocess.PIPE

        if "stderr" not in kwargs:
            kwargs["stderr"] = subprocess.PIPE

        if "cwd" not in kwargs:
            # Sets the current working directory to the path of
            # the tmpdir
            kwargs["cwd"] = str(self.tmpdir)

        start_time = time.time()

        popen = subprocess.Popen(
            args,
            # Need to decode the stdout and stderr with the correct
            # character encoding (http://stackoverflow.com/a/28996987)
            universal_newlines=True,
            **kwargs,
        )

        stdout, stderr = popen.communicate()

        end_time = time.time()

        # The stdout and stderr are wrapped in a CheckOutput object to make
        # it easy to assert whether it contains specific data / strings.

        if stdout is not None:
            stdout = checkoutput.CheckOutput(output=stdout)

        if stderr is not None:
            stderr = checkoutput.CheckOutput(output=stderr)

        command = args
        if isinstance(command, list):
            command = " ".join(command)

        result = runresult.RunResult(
            command=command,
            path=self.path(),
            stdout=stdout,
            stderr=stderr,
            returncode=popen.returncode,
            time=end_time - start_time,
        )

        if popen.returncode != 0:
            raise runresulterror.RunResultError(result)

        return result

    def __str__(self):
        """Generate a single string representation of the testdirectory.

        :return: String representation of the testdirectory which is
            the path.
        """
        return str(self.tmpdir)

    def _create_symlink(self, source, link_name, isdir):
        """Create a symbolic link pointing to source named link_name."""

        # os.symlink() is not available in Python 2.7 on Windows.
        # We use the original function if it is available, otherwise we
        # create a helper function for Windows
        os_symlink = getattr(os, "symlink", None)
        if not callable(os_symlink) and sys.platform == "win32":

            def symlink_windows(source, link_name):
                # mklink is used to create an NTFS junction, i.e. symlink
                cmd = ["mklink"]
                if isdir:
                    cmd += ["/D"]
                cmd += [
                    '"{}"'.format(link_name.replace("/", "\\")),
                    '"{}"'.format(source.replace("/", "\\")),
                ]

                self.run(" ".join(cmd), shell=True)

            os_symlink = symlink_windows

        os_symlink(source, link_name)

    def _expand_filename(self, filename):
        r"""Expand filename by expanding wildcards e.g. ``'dir/*/file.txt'``.

        The glob should return only one file
        """

        filename = pathlib.Path(filename)
        files = list(filename.parent.glob(filename.name))

        if len(files) != 1:
            raise ValueError(
                f"Expected one file matching {filename}, found {len(files)}."
            )

        return files[0]
