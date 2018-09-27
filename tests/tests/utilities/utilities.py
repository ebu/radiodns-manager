import re


def sql_alchemy_result_to_list(result):
    """
    Converts the result of a sqlAlchemy proxy result object into a list of list (list of rows).
    :param result: the sqlAlchemy query result.
    :return: the converted list.
    """
    result_list = []
    for row in result:
        result_list.append(list(row))

    return result_list


def normalize_list(string_list):
    """
    Normalizes the contents of a list of strings by removing tabs and line return and removing any extra blanks.
    :param string_list: the list to normalize.
    :return: The normalized list.
    """
    line_return = re.compile(r'[\t\n]+')
    more_than_two_spaces = re.compile(r'[\s]{2,}')
    return list(map(lambda x: re.sub(
        more_than_two_spaces,
        ' ',
        re.sub(
            line_return,
            '',
            x
        )
    ).strip(), string_list))


def compare_lists(list_a, list_b, strict=False):
    """
    Compare two lists of string. If strict, compare their raw values. Otherwise normalize lists with
    normalize_list.
    :param list_a: the first list.
    :param list_b: the second list.
    :param strict: If strict, no normalization is done and the two list are compared with their raw values.
    :return: True if the lists are the same (same contents (spaces depending on strict),
    same length but not same order), False otherwise.
    """
    if 0 == len(list_a) == len(list_b):
        return True

    if not strict:
        list_a = normalize_list(list_a)
        list_b = normalize_list(list_b)

    diff = set(list_a).difference(list_b)
    if len(diff) != 0:
        print("""[normalize_and_compare_lists] {a} is not the same as {b}"""
              .format(a=diff, b=set(list_b).difference(list_a)))

    # check lists
    return len(diff) == 0 and len(list_a) == len(list_b)
