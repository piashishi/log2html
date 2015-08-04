import web
import json
import urllib
import genMSC
import filter

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
#         content = urllib.unquote(web.data())
        rules =  json.loads(web.data())
        filter.filterMsg(rules)
        msc = genMSC.createMSC()
        return msc

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()