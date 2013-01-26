import cherrypy

from main import STEAM, Admin, handle_error

root = STEAM()
admin = Admin()

dispatcher = cherrypy.dispatch.RoutesDispatcher()
dispatcher.explicit = False

# Public Pages
dispatcher.connect('index', '/', root.index)
dispatcher.connect('login_page', '/login', root.login_page)
dispatcher.connect('register_page', '/register', root.register_page)

# Auth
dispatcher.connect('auth_logout', '/auth/logout', root.auth_logout)
dispatcher.connect('auth_getsession', '/auth/getsession', root.auth_getsession)

# User Account Pages
#

# Admin Pages
#