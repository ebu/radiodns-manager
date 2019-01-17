from tests.utilities.utilities import compare_lists


class TestNormalizeAndCompareLists(object):
    def test_lists_empty_string(self):
        assert compare_lists(["", "", ""], ["", "", ""])

    def test_lists_not_same_size(self):
        assert not compare_lists(["", ""], ["", "", ""])

    def test_lists_empty(self):
        assert compare_lists([], [])

    def test_list_empty_and_other_not(self):
        assert not compare_lists([], ["foo"])
        assert not compare_lists(["foo"], [])

    def test_list_tabs(self):
        assert compare_lists(["\t", ""], ["\t", ""])

    def test_list_mixed_order(self):
        assert compare_lists(["", "\t"], ["\t", ""])
        assert compare_lists(["", "foo"], ["foo", ""])
        assert compare_lists(["foo", ""], ["foo", ""])
        assert not compare_lists(["bar", ""], ["foo", ""])
        assert not compare_lists(["", "bar"], ["foo", ""])

    def test_list_mix_tabs_spaces_letters(self):
        assert not compare_lists(["foo \t", "bar"], ["\t", ""])
        assert compare_lists(["foo   dssdsd\t", "bar"], ["\tfoo dssdsd", "\tbar"])

    def test_strict_mode(self):
        assert not compare_lists(["foo \t", "bar"], ["foo", "bar"], True)
        assert compare_lists(["foo", "bar"], ["foo", "bar"], True)
