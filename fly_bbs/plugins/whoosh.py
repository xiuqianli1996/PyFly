from whoosh.index import create_in, open_dir, exists_in
from whoosh import writing
import os


class WhooshSearcher:

    def __init__(self, app=None):
        self.initialized = False
        self.whoosh_path = 'whoosh_indexes'
        self.indexes = {}
        if app:
            self.init_app(app)

    def init_app(self, app):

        if 'whoosh_searcher' not in app.extensions:
            app.extensions['whoosh_searcher'] = self
        if app.config['WHOOSH_PATH'] is not None:
            self.whoosh_path = app.config['WHOOSH_PATH']
        if not os.path.exists(self.whoosh_path):
            os.mkdir(self.whoosh_path)
        self.initialized = True

    def add_index(self, index_name, schema):
        if not self.initialized:
            raise Exception('not initialized')

        if exists_in(self.whoosh_path, index_name):
            ix = open_dir(self.whoosh_path, index_name)
        else:
            ix = create_in(self.whoosh_path, schema, index_name)
        self.indexes[index_name] = ix

    def get_index(self, index_name):
        if not exists_in(self.whoosh_path, index_name):
            raise Exception('This index is not exists')
        ix = self.indexes[index_name]
        if ix is None:
            ix = open_dir(self.whoosh_path, index_name)
            self.indexes[index_name] = ix
        return ix

    def get_writer(self, index_name):
        return self.get_index(index_name).writer()

    def get_searcher(self, index_name):
        return self.get_index(index_name).searcher()

    def add_document(self, index_name, doc):
        writer = self.get_writer(index_name)
        writer.add_document(**doc)
        writer.commit()

    def update_document(self, index_name, unique_field, doc):
        writer = self.get_writer(index_name)
        writer.update_document(**unique_field, **doc)
        writer.commit()

    def delete_document(self, index_name, fieldname, termtext):
        writer = self.get_writer(index_name)
        writer.delete_by_term(fieldname, termtext)
        writer.commit()

    def clear(self, index_name):
        writer = self.get_writer(index_name)
        writer.commit(mergetype=writing.CLEAR)
