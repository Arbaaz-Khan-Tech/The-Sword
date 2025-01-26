# Middleware initialization or shared logic
def common_middleware(app):
    @app.before_request
    def log_request():
        print(f"Request URL: {request.url}")
