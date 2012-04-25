"""
XXX BGH: This possibly obsolete module uses the avatar store directly, which is bad.
It should be refactored to use request stores.
"""

from storm.locals import Storm
from storm.properties import PropertyPublisherMeta
from storm.info import get_obj_info

from warp.runtime import avatar_store

DELETE_SQL = "DELETE FROM warp_fulltext WHERE model = ?::text AND doc_id = ?"
INSERT_SQL = "INSERT INTO warp_fulltext (model, doc_id, fulltext) VALUES (?::text, ?, to_tsvector(?::text::regconfig, ?::text))"

SEARCH_SQL = """
SELECT model, doc_id
FROM warp_fulltext, 
     plainto_tsquery(?::text::regconfig, ?::text) AS query
WHERE fulltext @@ query
ORDER BY ts_rank_cd(fulltext, query) DESC
"""

searchModels = {}

class SearchMeta(Storm.__metaclass__):
    def __init__(self, name, bases, dict):

        # Avoid adding Searchable itself
        if bases[0] is not Storm:
            searchModels[self.__name__] = self

        return super(SearchMeta, self).__init__(name, bases, dict)
    

class Searchable(Storm):

    __metaclass__ = SearchMeta

    _searchSeparator = u' $$ '

    def getSearchVals(self):
        return [getattr(self, col) for col in self.searchColumns]

    def getSearchLanguage(self):
        return 'english'

    def __storm_flushed__(self):
        avatar_store.execute(DELETE_SQL, (self.__class__.__name__, self.id))

        if get_obj_info(self).get("store") is not None:
            
            vals = [v for v in self.getSearchVals() if v is not None]

            if vals:
                text = self._searchSeparator.join(vals).encode("utf-8")

                avatar_store.execute(INSERT_SQL,
                                     (self.__class__.__name__,
                                      self.id,
                                      self.getSearchLanguage(),
                                      text))
        avatar_store.commit()


def reindex():
    import storm.database
    avatar_store.execute("DELETE FROM warp_fulltext")
    for klass in searchModels.itervalues():
        for obj in avatar_store.find(klass):
            obj.__storm_flushed__()


def search(term, language='english'):
    for modelName, doc_id in avatar_store.execute(SEARCH_SQL, (language, term.encode("utf-8"))):
        model = searchModels[modelName]
        yield avatar_store.get(model, doc_id)
