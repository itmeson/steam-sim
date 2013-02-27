import cherrypy

from main import STEAM, Auth, Account, Admin, SuperAdmin, handle_error

root = STEAM()
auth = Auth()
account = Account()
admin = Admin()
superadmin = SuperAdmin()

dispatcher = cherrypy.dispatch.RoutesDispatcher()
dispatcher.explicit = False

# ----------
# - Public Pages
# ----------
dispatcher.connect('index', '/', root.index)
dispatcher.connect('about', '/about', root.about)
dispatcher.connect('login_page', '/login', root.login_page)
dispatcher.connect('register_page', '/register', root.register_page)
dispatcher.connect('ajax_jslog', '/ajax/jslog', root.ajax_jslog)

# ----------
# - Problem Pages
# ----------
dispatcher.connect('view_problem', '/problems/{category:([-\w]+)}/{slug:([-\w]+)}', root.view_problem)
dispatcher.connect('problems', '/problems/{category:([-\w]+)}', root.problems)
dispatcher.connect('problems', '/problems', root.problems)

# ----------
# - Auth Pages
# ----------
dispatcher.connect('auth_logout', '/auth/logout', auth.auth_logout)
dispatcher.connect('auth_activate', '/auth/activate/:vtoken', auth.auth_activate)
dispatcher.connect('auth_getsession', '/auth/getsession', auth.auth_getsession)

# ----------
# - Public Pages
# ----------
dispatcher.connect('user_account', '/user/account', account.user_account)
dispatcher.connect('edit_profile', '/ajax/editprofile', account.edit_profile)
dispatcher.connect('edit_image', '/ajax/editimage', account.edit_image)

# ----------
# - Admin Pages
# ----------
# None Yet!

# ----------
# - SuperAdmin Pages
# ----------
dispatcher.connect('admin_problems', '/admin/problems', superadmin.admin_problems)
dispatcher.connect('ajax_problems', '/ajax/problems', superadmin.ajax_problems)


