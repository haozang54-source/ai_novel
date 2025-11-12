def register_routes(app):
    from .projects import bp as projects_bp
    from .outlines import bp as outlines_bp
    from .chapters import chapters_bp
    from .ai_assistant import ai_assistant_bp
    from .characters import bp as characters_bp
    from .worldviews import bp as worldviews_bp
    from .locations import bp as locations_bp
    from .items import bp as items_bp
    from .foreshadowings import bp as foreshadowings_bp
    from .writing_styles import bp as writing_styles_bp
    
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(outlines_bp, url_prefix='/api')
    app.register_blueprint(chapters_bp)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(characters_bp)
    app.register_blueprint(worldviews_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(foreshadowings_bp)
    app.register_blueprint(writing_styles_bp)
