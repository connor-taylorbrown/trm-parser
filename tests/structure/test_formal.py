from structure.formal import NonTerminal, Ranking, Mapper, Sentence, Terminal


def test_outranks():
    ranks = {
        'part': {'part'},
        'def': {'*'},
        'dem': {'*', 'mod'},
        '*': {'*', 'mod'},
        'pron': {'mod'},
        'mod': {'mod'}
    }
    cases = [
        ('1s', '*', False, 'Missing ranking should throw'),
        ('part', 'part', True, 'Recursive ranking should be supported'),
        ('def', 'def', False, 'Non-recursive ranking should be supported'),
        ('dem.pron', '*', True, 'Complex glosses should be supported on "."'),
        ('pron.dem', '*', True, 'Complex glosses should be supported on "."'),
        ('dem-pron', '*', True, 'Complex glosses should be supported on "-"'),
        ('pron-dem', '*', True, 'Complex glosses should be supported on "-"'),
        ('dem.s-a-pron.1s', '*', True, 'Complex glosses may contain noise'),
        ('pron', '*', False, 'Complex gloss may contain inconsistent component')
    ]

    for antecedent, token, expected, message in cases:
        sut = Ranking(ranks)

        result = sut.outranks(antecedent, token)

        assert result == expected, message


def test_add():
    sums = [
        ({'r', 'pron'}, '$'),
        ({'def', '*'}, 'ref'),
        ({'*', 'mod'}, 'desc'),
        ({'mod'}, 'mod')
    ]
    cases = [
        ('r-a-pron.1s', 'def', '$', 'Antecedent implies result'),
        ('def', '*', 'ref', 'Both imply result'),
        ('*', 'mod', 'desc', 'Priority implies result'),
        ('mod', 'mod', 'mod', 'Priority implies result')
    ]

    for antecedent, token, expected, message in cases:
        sut = Mapper(sums)

        result = sut.add(antecedent, token)

        assert result == expected, message


def test_read():
    ranking = Ranking({
        '$': {'def', 'part', '$', '#'},
        'part': {'part', 'pron'},
        'def': {'*'}
    })

    mapper = Mapper([
        ({'r', 'pron'}, '$'),
        ({'dem', 'pron'}, 'def'),
        ({'def', '*'}, 'ref')
    ])

    naku = Terminal('r-a-pron.1s', 'nāku')
    te = Terminal('def.s', 'te')
    na = Terminal('part.r-a', 'nā')
    tatou = Terminal('pron.1n-p', 'tātou')
    ta = Terminal('part.dem.s-a', 'tā')
    whare = Terminal('*', 'whare')
    i = Terminal('part.r', 'i')

    cases = [
        (Sentence(ranking, mapper), naku.gloss, naku.text, [naku], 'First token should be pushed'),
        (Sentence(ranking, mapper).read(naku.gloss, naku.text), te.gloss, te.text, [NonTerminal('$', naku, None), te], 'Antecedent phrasal words should be resolved'),
        (Sentence(ranking, mapper).read(na.gloss, na.text).read(tatou.gloss, tatou.text), te.gloss, te.text, [NonTerminal('$', na, tatou), te], 'Antecedent phrases should be resolved'),
        (Sentence(ranking, mapper).read(na.gloss, na.text).read(ta.gloss, ta.text).read(tatou.gloss, tatou.text), whare.gloss, whare.text, [na, NonTerminal('def', ta, tatou), whare], 'Partial resolution should be supported'),
        (Sentence(ranking, mapper).read(na.gloss, na.text).read(tatou.gloss, tatou.text).read(te.gloss, te.text).read(whare.gloss, whare.text), i.gloss, i.text, [NonTerminal('$', na, tatou), NonTerminal('$', NonTerminal('ref', te, whare), None), i], 'Promotion should be supported'),
        (Sentence(ranking, mapper).read(na.gloss, na.text).read(tatou.gloss, tatou.text).read(te.gloss, te.text).read(whare.gloss, whare.text), '#', '', [NonTerminal('$', na, tatou), NonTerminal('$', NonTerminal('ref', te, whare), None)], 'Stop token should be supported'),
        (Sentence(ranking, mapper).read(na.gloss, na.text).read(tatou.gloss, tatou.text).read(na.gloss, na.text).read(tatou.gloss, tatou.text), '#', '', [NonTerminal('$', na, tatou), NonTerminal('$', na, tatou)], 'Repetition should be supported')
    ]

    for sentence, gloss, text, expected, message in cases:
        result = sentence.read(gloss, text)

        assert result.nodes == expected, message
