import json
from chirptext import JiCache, WebHelper, TextReport, FileHelper
from chirptext.leutile import AppConfig
from chirptext.chirpnet import SmartURL
from chirptext.texttaglib import TaggedDoc

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

cfg = AppConfig(name='omwtk')
web = WebHelper(cache=JiCache(cfg.config.get('DEFAULT', 'webcache')))
DEFAULT_LANG = cfg.config.get("BABELFY", "lang")
DEFAULT_KEY = cfg.config.get("BABELFY", "key")
DEFAULT_DOCPATH = cfg.config.get("OMWTK", "docpath")
DEFAULT_DOCNAME = cfg.config.get("OMWTK", "docname")


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def showinfo():
    print("Babelfy toolkit information")
    print("Working dir     : {}".format(FileHelper.abspath(".")))
    print("Cache location  : {}".format(web.cache.location))
    print("Default language: {}".format(DEFAULT_LANG))
    print("Default key     : {}".format(DEFAULT_KEY))
    print("Default doc path: {}".format(DEFAULT_DOCPATH))
    print("Default doc name: {}".format(DEFAULT_DOCNAME))


def make_url(text, lang=DEFAULT_LANG, key=DEFAULT_KEY, **kwargs):
    ''' Make Babelfy URL '''
    u = SmartURL('https://babelfy.io/v1/disambiguate')
    u.query['text'] = text
    u.query['lang'] = lang if lang else DEFAULT_LANG
    u.query['key'] = key if key else DEFAULT_KEY
    for k, v in kwargs.items():
        u.query[k] = v
    return str(u)


def babelfy(text, lang=DEFAULT_LANG, key=DEFAULT_KEY, **kwargs):
    ''' Babelfy a sentence
    '''
    api_url = make_url(text, lang, key, **kwargs)
    return web.fetch(api_url, encoding="utf-8")


def babelfy_doc(docpath=DEFAULT_DOCPATH, docname=DEFAULT_DOCNAME, outfile=None, **kwargs):
    ''' Babelfy a tagged document
    '''
    speckled = TaggedDoc(docpath, docname).read()
    sents = []
    for s in speckled:
        output = json.loads(babelfy(s.text, **kwargs))
        sents.append((s.ID, output))
    if outfile:
        with TextReport(outfile) as rp:
            rp.write(json.dumps(sents, indent=2))
    return sents
