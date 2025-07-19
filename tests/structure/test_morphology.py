from structure.morphology import MorphologyNode


def item(gloss, *overrides):
    return MorphologyNode(gloss, *overrides)


def test_gloss_affixes():
    cases = [
        (item('').add_node('prefixes', 'tā', item('1n-').add_node('items', 'tou', item('p'))), 'tātou', True, ['1n-p']),
        (item('').add_node('suffixes', 'tou', item('-p').add_node('items', 'tā', item('1n'))), 'tātou', False, ['1n-p']),
        (item('').add_node('prefixes', 't', item('dem.s-').add_node('items', 'ā', item('a'))), 'tā', True, ['dem.s-a']),
        (item('').add_node('prefixes', 't', item('dem.s-', 'dem.p.').add_node('items', 'ā', item('dem.p.a'))), 'tā', True, ['dem.s-a'])
    ]

    for sut, text, is_prefix, expected in cases:
        result = sut.gloss_affixes(text, is_prefix)

        assert list(result) == expected
