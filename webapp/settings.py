import urls

ROOT_URL = "/var/www/wilhall.com/steam/"

config = {
	'global': {
		'environment': "embedded",
		'server.environment': "development",
		'log.screen': False,
		'log.error_file': ROOT_URL + "logs/cherrypy_error.log",
		'log.access_file': ROOT_URL + "logs/cherrypy_access.log",
		'log.js_file': ROOT_URL + "logs/javascript_error.log",
		'ROOT_URL': ROOT_URL
	},
	'/': {
		'request.dispatch': urls.dispatcher,
		'error_page.default': urls.handle_error
	},
	'db': {
		'DB_HOST': "localhost",
		'DB_NAME': "steam",
		'DB_USERNAME': "steamadmin",
		'DB_PASSWORD': "petrifiedcomputationaldevices"
	},
	'emailer': {
		'server': "smtp.gmail.com",
		'port': 587,
		'username': "steam@wilhall.com",
		'password': "petrifiedcomputationaldevices",
		'sender': "STEAM Club",
		'from': "steam@wilhall.com"
	},
	'profilemanager': {
		'imagepath': ROOT_URL + "static/upload/profiles/",
		'imageurl': "/static/upload/profiles/"
	},
	'mako': {
		'MAKO_DIRECTORIES': [ROOT_URL + "static/html/"]
	}
}