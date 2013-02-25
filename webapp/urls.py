import cherrypy

from main import STEAM, Account, Admin, handle_error

root = STEAM()
account = Account()
admin = Admin()

dispatcher = cherrypy.dispatch.RoutesDispatcher()
dispatcher.explicit = False

# Public Pages
dispatcher.connect('index', '/', root.index)
dispatcher.connect('problems', '/problems', root.problems)
dispatcher.connect('login_page', '/login', root.login_page)
dispatcher.connect('register_page', '/register', root.register_page)
dispatcher.connect('ajax_jslog', '/ajax/jslog', root.ajax_jslog)

# Auth
dispatcher.connect('auth_logout', '/auth/logout', root.auth_logout)
dispatcher.connect('auth_activate', '/auth/activate/:vtoken', root.auth_activate)
dispatcher.connect('auth_getsession', '/auth/getsession', root.auth_getsession)

# User Account Pages
dispatcher.connect('user_account', '/user/account', account.user_account)
dispatcher.connect('edit_profile', '/ajax/editprofile', account.edit_profile)
dispatcher.connect('edit_image', '/ajax/editimage', account.edit_image)

# Admin Pages
#