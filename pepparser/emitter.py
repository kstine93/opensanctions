import logging
from pprint import pprint  # noqa

from pepparser.util import clean_obj, unique_objs
from pepparser.schema import validate
from pepparser.model import EntityManager


log = logging.getLogger(__name__)


class Emitter(object):

    def __init__(self, engine):
        self.manager = EntityManager(engine)
        self.entities = []

    def entity(self, data):
        data['identities'] = unique_objs(data.get('identities'))
        data['other_names'] = unique_objs(data.get('other_names'))
        data['addresses'] = unique_objs(data.get('addresses'))
        data = clean_obj(data)
        validate(data)
        # log.info('%r: %s', data.get('uid'), data.get('name'))
        self.entities.append(data)

    def save(self):
        log.info("Parsed %s entities", len(self.entities))
        self.manager.save_entities(self.entities)