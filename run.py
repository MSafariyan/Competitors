from app import app
import rq_dashboard

app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")

if __name__ == '__main__':
    app.run()
