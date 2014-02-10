#!/usr/bin/env python

from SimpleHTTPServer import SimpleHTTPRequestHandler, test
from itertools import count
from json import dumps, loads
from optparse import OptionParser
import os
import sys


ID_ATTRIBUTE = 'id'

collections = {}


class Collection(object):

    def __init__(self, records=None):
        if records is None:
            records = {}
        self.records = records
        self.id_counter = count(len(self.records) + 1)

    def create(self, record, _):
        row_id = self.id_counter.next()
        record[ID_ATTRIBUTE] = row_id
        self.records[row_id] = record
        return record

    def list_or_get(self, record, row_id):
        if row_id is not None:
            # Specific record requested.
            return self.records[row_id]
        else:
            # Return a list of all records.
            return self.records.values()

    def update(self, record, row_id):
        self.records[row_id] = record
        return record

    def delete(self, record, row_id):
        del self.records[row_id]
        return {}


def parse_path(path):
    """Parse the path, returning the collection name and item id.
    Either may be None.

        >>> parse_path('/index.html')
        ('index.html', None)
        >>> parse_path('/books')
        ('books', None)
        >>> parse_path('/books/12')
        ('books', 12)
    """
    parts = [p for p in path.split('/') if p]
    if len(parts) == 1:
        return (parts[0], None)
    elif len(parts) == 2 and parts[1].isdigit():
        return (parts[0], int(parts[1]))
    else:
        return (None, None)


def record_handler(collection_method, fallback=None):

    def handle(handler):
        collection_name, record_id = parse_path(handler.path)
        if collection_name in collections:
            collection = collections[collection_name]
            body = handler.request_to_json()
            json = collection_method(collection, body, record_id)
            return handler.json_to_response(json)
        elif fallback:
            return fallback(handler)
        else:
            return handler.send_404()
    return handle


class BackBoneServer(SimpleHTTPRequestHandler):

    do_GET = record_handler(Collection.list_or_get,
                            fallback=SimpleHTTPRequestHandler.do_GET)
    do_POST = record_handler(Collection.create)
    do_PUT = record_handler(Collection.update)
    do_DELETE = record_handler(Collection.delete)

    def request_to_json(self):
        """Read a JSON object from request body"""
        size = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(size)
        if size > 0:
            return loads(body)
        else:
            return None

    def json_to_response(self, json):
        content = dumps(json)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_404(self):
        self.send_error(404, "File not found")


def load_collections(filename):
    """Load collections from disk if file exists"""
    if not os.path.exists(filename):
        return
    with open(filename) as json_file:
        json = loads(json_file.read())
    for name, records in json.items():
        collections[name] = Collection(records)


def persist_collections(filename):
    """Persist collections to disk"""
    json = {}
    for name, collection in collections.items():
        json[name] = collection.records
    with open(filename, 'w') as outputfile:
        outputfile.write(dumps(json, indent=2))


def pop_arguments():
    """Pop and return arguments from command line, leaving it in a state
    for test(...) to use"""
    arguments = []
    while len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[-1].isdigit():
            # Port number for test server supplied.
            return arguments
        arguments.insert(0, sys.argv.pop())
    return arguments


def get_options():
    """Get command line options"""
    parser = OptionParser()
    parser.add_option('-p', '--persist', dest='persist')
    return parser.parse_args(pop_arguments())


def run_server():
    settings, args = get_options()

    for collection_name in args:
        print 'Adding collection:', collection_name
        collections[collection_name] = Collection()

    if settings.persist:
        load_collections(settings.persist)

    try:
        test(HandlerClass=BackBoneServer)
    except KeyboardInterrupt:
        print 'Shutting down.'
        if settings.persist:
            print 'Saving records to', settings.persist
            persist_collections(settings.persist)


if __name__ == '__main__':
    run_server()
