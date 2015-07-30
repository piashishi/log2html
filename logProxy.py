import web

import parseLog

render = web.template.render('templates/')

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        processInfo, msgTypeInfo = parseLog.parseNGLog("log")
        return render.index(processInfo, msgTypeInfo)
    
    def POST(self):
        content = web.data()
        return content

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()