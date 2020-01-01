def create_module(app):
    from .views import equimolar_bp
    app.register_blueprint(equimolar_bp)