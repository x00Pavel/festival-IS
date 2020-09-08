import handlers
import db_handlers
import flask

main = flask.Flask(__name__)

# TODO: handlers
main.add_url_rule('/', view_func=handlers.hello)

# TODO: db_handlers
main.add_url_rule('/blogs', view_func=db_handlers.listBlog)

if __name__ == '__main__':
    main.run(debug=True, host='0.0.0.0', port=5000)