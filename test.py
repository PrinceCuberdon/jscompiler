#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import unittest

import jscompiler


# Get the current directory (the test directory)
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests")


def get_file_name(file_name):
    """ Returns the well formed path for the filename
    """
    return os.path.join(TEST_DIR, file_name)


class TestJsCompiler(unittest.TestCase):
    """ Test the open_file function
    """
    def _open_file(self, file_name):
        content = jscompiler.open_file(get_file_name(file_name))
        self.assertIsNotNone(content)
        return content

    def test_open_regular_file(self):
        """ Open a existing file (in fact: the test of test method)
        """
        content = self._open_file("test_comments.js")
        self.assertIsNotNone(content)

    def test_open_unexisting_file(self):
        """ Try to open a unknow file
        """
        with self.assertRaises(IOError):
            self._open_file("unknowfile.js")

    def test_replace_strings(self):
        """ Test replace string with convention
        """
        content = self._open_file("test_comments.js")
        result = jscompiler.replace_strings(content)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], list)

        # test_comments.js contains two string
        self.assertEquals(len(result[1]), 2)
        self.assertRegexpMatches(result[0], r"__\{\d+\}__")
        self.assertEquals(len(re.findall(r"__\{\d+\}__", result[0])), 2)

    def test_put_strings(self):
        """ Test the opposite of replace_strings
        """
        content = self._open_file("test_comments.js")
        new_content, str_all = jscompiler.replace_strings(content)

        # First arg
        self.assertIsNotNone(new_content)
        self.assertIsInstance(new_content, str)
        self.assertNotEqual(len(content), 0)

        # Second arg
        self.assertIsInstance(str_all, list)
        self.assertNotEqual(len(str_all), 0)

        # put
        put_content = jscompiler.put_strings(new_content, str_all)
        self.assertEqual(content, put_content)

    def test_strip_empty_lines(self):
        """ Test the empty line removal
        """
        content = self._open_file("test_empty_line.js")
        result = jscompiler.strip_empty_lines(content)
        self.assertLessEqual(len(content.split("\n")), result.split("\n"))

    def test_strip_comments(self):
        """ Test remove comments
        """
        content = self._open_file("test_comments.js")
        result = jscompiler.strip_comments(content)
        expected = self._open_file("test_comment_result.js")
        self.assertEqual(result, expected)

    def test_remove_eol(self):
        """
        Remove MS Windows end of line which are (\n)
        """
        content = self._open_file("test_eol_windows.js")
        result = jscompiler.remove_eol(content)
        self.assertNotRegexpMatches(r'\r|\n', result)

    def test_remove_semicolon(self):
        """
        Remove the semi-colon
        """
        content = self._open_file("test_semi_colon.js")
        result = jscompiler.remove_semi_colon(content)
        self.assertEqual(len(re.findall(r";", result)), 3)

    def test_remove_unneeded_semi_colon(self):
        content = self._open_file("test_remove_unneeded_semi_colon.js")
        result = jscompiler.remove_unneeded_semi_colon(content)
        self.assertEqual(len(re.findall(r';', result)), 0)

    def test_remove_identation(self):
        content = self._open_file("test_semi_colon.js")
        result = jscompiler.remove_double_space_or_tabs(content)
        self.assertNotIn('\t', result)
        self.assertNotIn('  ', result)

    def test_remove_unneeded_spaces(self):
        pass

    def test_remove_trailing_slashes(self):
        pass

    def test_get_javascript_files(self):
        files = [
            'test_comment_result.js',
            'test_comments.js',
            'test_empty_line.js',
            'test_eol_windows.js',
            'test_remove_unneeded_semi_colon.js',
            'test_semi_colon.js'
        ]
        files = [os.path.join(TEST_DIR, f) for f in files]
        files.sort()

        real_files = jscompiler.get_javascript_files(TEST_DIR)
        real_files.sort()

        self.assertEqual(files, real_files)

# Starts the test
if __name__ == '__main__':
    unittest.main()
