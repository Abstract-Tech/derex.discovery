from whitenoise import WhiteNoise

application = __import__("course_discovery.wsgi").wsgi.application

application = WhiteNoise(application, root="/openedx/staticfiles", prefix="/static")
