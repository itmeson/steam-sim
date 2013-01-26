import threading
import smtplib

class Emailer:
	
	class Email(threading.Thread):
		def __init__(self, server, port, username, password, sender, recipient, _from, to, subject, body):
			threading.Thread.__init__(self)
			
			self.server = server
			self.port = port
			self.username = username
			self.password = password
			self._from = "%s <%s>" % (sender, _from)
			self.to = "%s <%s>" % (recipient, to)
			self.headers = "\r\n".join([
							"From: " + self._from,
							"To: " + self.to,
							"Subject: " + subject,
							"Mime-Version: 1.0",
							"Content-Type: text/html",
							"\r\n\r\n"
							])
			self.body = body
		
		# Do we need TLS?
		def starttls(self):
			return True if self.port in [465, 587] else False
		
		# Connect and send the email
		def run(self):
			session = smtplib.SMTP(self.server, self.port)
			session.ehlo()
			
			if self.starttls():
				session.starttls()
			
			session.ehlo()
			session.login(self.username, self.password)
			session.sendmail(self._from, self.to, self.headers + self.body)
			session.quit()
			return
	
	def __init__(self, server, port, username, password):
		self.server = server
		self.port = port
		self.username = username
		self.password = password
	
	# Start a new Email() thread to send the email
	def send(self, sender, recipient, _from, to, subject, body):
		email = self.Email(self.server, self.port, self.username, self.password, sender, recipient, _from, to, subject, body)
		email.start()
		