def create_module(app):
    from .views2 import blueprint
    app.register_blueprint(blueprint)