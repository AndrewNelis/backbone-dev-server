backbone-dev-server
===================

You might be familiar with using Python's `SimpleHTTPServer` module to run a test server:

    $ python -m SimpleHTTPServer
    Serving HTTP on 0.0.0.0 port 8000 ...

This starts a basic server, dishing up content in the current folder.

`backbone_server.py` extends this module and allows you to add named model API endpoints for consumption by 
[Backbone](http://backbonejs.org/). You just need to specify the model names on the command line and a simple
RESTful API is exposed with that name. For example:

    $ python backbone_server.py books
    Adding collection: books
    Serving HTTP on 0.0.0.0 port 8000 ...
    
Now we have a number of URLs exposed on top of the static content:

    url         HTTP Method  Operation
    /books      GET          Get an array of all books
    /books/:id  GET          Get the book with id of :id
    /books      POST         Add a new book and return the book with an id attribute added
    /books/:id  PUT          Update the book with id of :id
    /books/:id  DELETE       Delete the book with id of :id
    
A model could take advantage of this with the following JS declaration:

    var Book = Backbone.Model.extend({urlRoot: '/books'});
    
And a collection with:

    var BookShelf = Backbone.Collection.extend(url: '/books');

On the server side, we're just keeping a dictionary that corresponds the the JSON submitted by Backbone, there's
nothing fancy going on.

### Many Models ###

You can specify multiple models on the command line:

    $ python backbone_server.py books authors ratings
    Adding collection: books
    Adding collection: authors
    Adding collection: ratings
    Serving HTTP on 0.0.0.0 port 8000 ...

### Persistence ###

By default, when you stop the server (with Ctrl+Z), all the data is lost. But you can persist the data in a named file:

    $ python backbone_server.py books --persist books.json

When the server starts, existing records will be read from that file and on shutdown, the records will be written to that file, overwriting it.
