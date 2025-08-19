from flask import render_template

def not_found(error):
    return render_template("404.html"), 404

def internal_error(error):
    return render_template("500.html"), 500

def register_handlers(app):
    app.register_error_handler(404, not_found)
    app.register_error_handler(500, internal_error)