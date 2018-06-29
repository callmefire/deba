import web

web.config.debug = False
urls = (
	"/count", "count",
	"/reset", "reset"
)
app = web.application(urls, locals())

# Set cookie's timeout interval
web.config.session_parameters['timeout'] = 5
# Define private variable in cookie, which will be write into the cookie file on client side
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer = {'my_count':0})

class count:
    def GET(self):
        session.my_count += 1
        print session._config.cookie_name, session.session_id, session.ip
        return str(session.my_count)

class reset:
    def GET(self):
        session.kill()
        return ""

if __name__ == "__main__":
    app.run()
