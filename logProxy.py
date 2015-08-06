import web
import json
import genMSC
import filter

import parseLog

MSC=""

render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/show', 'show',
)

class show:
    def GET(self):
        global MSC
        return render.show(MSC)
        
class index:
    def GET(self):
        processInfo, msgTypeInfo = parseLog.parseNGLog("log")
        return render.index(processInfo, msgTypeInfo)
    
    def POST(self):
        global MSC
        rules =  json.loads(web.data())
        filter.filterMsg(rules)
        MSC = genMSC.createMSC()
        url = "show"
        return url

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()