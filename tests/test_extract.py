from unittest import TestCase

from parliament.extract import _split_vote_result


class TestProvider(TestCase):

    def test_split_vote(self):

        vote = "afavor:ps,psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "ps,psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(",")
        })

        vote = "afavor:be,pcp,pan,pev,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)contra:ps,psd,cds-pp,ilausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,pan,pev,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "contra": "ps,psd,cds-pp,il".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:be,pcp,cds-pp,pev,ch,ilcontra:ps,psdabstenção:pan,cristinarodrigues(ninsc)ausência:joacinekatarmoreira(ninsc)"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,cds-pp,pev,ch,il".split(","),
            "contra": "ps,psd".split(","),
            "abstenção": "pan,cristinarodrigues(ninsc)".split(","),
            "ausência": "joacinekatarmoreira(ninsc)".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)contra:ps"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "contra": "ps".split(",")
        })

        vote = "afavor:be,pcp,pan,pev,ch,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)contra:psabstenção:psd,cds-pp,il"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,pan,pev,ch,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "contra": "ps".split(","),
            "abstenção": "psd,cds-pp,il".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)abstenção:psausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "abstenção": "ps".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:ps,psd,be,pcp,cds-pp,pan,pev,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)ausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "ps,psd,be,pcp,cds-pp,pan,pev,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)abstenção:ps"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,ch,il,cristinarodrigues(ninsc),joacinekatarmoreira(ninsc)".split(","),
            "abstenção": "ps".split(",")
        })

        vote = "ausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "ausência": "ch".split(",")
        })

        vote = ""
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {})
