from unittest import TestCase

from parliament.extract import _split_vote_result, mydict


class TestProvider(TestCase):

    def test_split_vote(self):

        vote = "afavor:ps,psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkm"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "ps,psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkm".split(",")
        })

        vote = "afavor:be,pcp,pan,pev,cr,jkmcontra:ps,psd,cds-pp,ilausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,pan,pev,cr,jkm".split(","),
            "contra": "ps,psd,cds-pp,il".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:be,pcp,cds-pp,pev,ch,ilcontra:ps,psdabstenção:pan,crausência:jkm"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,cds-pp,pev,ch,il".split(","),
            "contra": "ps,psd".split(","),
            "abstenção": "pan,cr".split(","),
            "ausência": "jkm".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkmcontra:ps"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkm".split(","),
            "contra": "ps".split(",")
        })

        vote = "afavor:be,pcp,pan,pev,ch,cr,jkmcontra:psabstenção:psd,cds-pp,il"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "be,pcp,pan,pev,ch,cr,jkm".split(","),
            "contra": "ps".split(","),
            "abstenção": "psd,cds-pp,il".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,il,cr,jkmabstenção:psausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,il,cr,jkm".split(","),
            "abstenção": "ps".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:ps,psd,be,pcp,cds-pp,pan,pev,il,cr,jkmausência:ch"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "ps,psd,be,pcp,cds-pp,pan,pev,il,cr,jkm".split(","),
            "ausência": "ch".split(",")
        })

        vote = "afavor:psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkmabstenção:ps"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "psd,be,pcp,cds-pp,pan,pev,ch,il,cr,jkm".split(","),
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

        vote = "afavor:ps,cds-pp,pan,ch,cr,1-psd,2-be,contra:2-ps,2-psd,be,pcp,pev,il,abstenção:3-ps,1-be,psd,jkm"
        res = _split_vote_result(vote)

        self.assertDictEqual(res, {
            "afavor": "ps,cds-pp,pan,ch,cr".split(","),
            "contra": "be,pcp,pev,il".split(","),
            "abstenção": "psd,jkm".split(","),
            "outros_afavor": "1-psd,2-be".split(","),
            "outros_contra": "2-ps,2-psd".split(","),
            "outros_abstenção": "3-ps,1-be".split(",")
        })

    def test_mydict(self):
        
        d = {'a': None, 'b': 5, 'c': {'a': None, 'b': 1, 'c': {'a': None, 'b': 1}}}
        
        self.assertTrue(mydict(d).get('a', {}) == {})
        self.assertTrue(mydict(d).get('a', 10) == 10)
        self.assertTrue(mydict(d).get('b', {}) == 5)
        self.assertTrue(mydict(d).get('c', {}).get('a', {}) == {})
        self.assertTrue(mydict(d).get('c', {}).get('a', 10) == 10)
        self.assertTrue(mydict(d).get('c', {}).get('b', {}) == 1)
        self.assertTrue(mydict(d).get('c', {}).get('c', {}).get('a', {}) == {})
        self.assertTrue(mydict(d).get('c', {}).get('c', {}).get('a', 10) == 10)
        self.assertTrue(mydict(d).get('c', {}).get('c', {}).get('b', {}) == 1)
        self.assertTrue(mydict(d).get('c', {}).get('d', {}) == {})
        self.assertTrue(mydict(d).get('c', {}).get('d', 10) == 10)
        self.assertTrue(mydict(d).get('d', {}) == {})
        self.assertTrue(mydict(d).get('d', 10) == 10)
