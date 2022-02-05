import re
import json
import logging
import urllib
import azure.functions as func

url_pattern='(http[^"]+)"\,[0-9^,]+\,[0-9^,]+'
size_pattern=re.compile('",|,')

def main(req: func.HttpRequest) -> func.HttpResponse:

    ### no id provided
    id = req.params.get('id')
    if not id:
        return func.HttpResponse("Please provide an id", status_code=400)

    try:
        
        ## grab web page
        response = urllib.request.urlopen("https://photos.app.goo.gl/" + id)
        urls = re.finditer(url_pattern, response.read().decode('utf-8'))
        result = []

        ## parse urls
        for url in urls:

            parts = size_pattern.split(url.group(0))
            width = parts[1]
            height = parts[2]

            if height:

                ## some random sizing issues
                act_height = int(height)
                while act_height > 2000: act_height = int(act_height/2)
                data = {
                    "src": parts[0] + "=h" + str(act_height),
                    "w": int(width),
                    "h": int(height)
                }
                result.append(data)
    
        return func.HttpResponse("{ \"images\": {" + json.dumps(result) + " }", status_code=200)

    except urllib.error.HTTPError as httpEx:
        logging.error("Invalid request %s", str(httpEx))
        return func.HttpResponse("Request failed, please check id", status_code=400)

    except re.error as reErr:
        logging.error("Processing response %s", str(reErr))
        return func.HttpResponse("Problem processing google photos response", status_code=400)
