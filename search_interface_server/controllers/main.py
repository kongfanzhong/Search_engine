from flask import request, Blueprint, render_template
from config import env
from extensions import db

import re
import requests
import json

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/wikipedia/')
def search_route():
    q = request.args.get("q")
    w = request.args.get("w")
    haveResults = False
    showResults = None

    if q != None and w != None:
        results = requests.get("http://localhost:{}/5f5h8f5m/p5/?q={}&w={}".format(env["port"] - 1, q, w))
        
        #  convert the body text of a HTML request message into json and reads the hits part
        results = json.loads(results.text)
        results = results["hits"]
        
        haveResults = (len(results) != 0)

        results = sorted(results, key = lambda x: x['score'], reverse = True)
        # Only list 10 results
        if len(results) > 10:
            results = results[:10]

        for result in results:
            print(result['score'])

        showResults = []
        for result in results:
            cur = db.cursor()
            cur.execute("select docid, title from Documents where docid = {}".format(result["docid"]))
            showResults.append(cur.fetchone())

    options = {
        "searchs" : dict(w = w, q = q),
        "haveResults" : haveResults,
        "results" : showResults,
        "urlSearch" : "http://localhost:{}/5f5h8f5m/p5/wikipedia/".format(env["port"])
    }

    return render_template("Search.html", **options)


@main.route('/wikipedia/summary')
def summary_route():
    docid = request.args.get("id")
    cur = db.cursor()
    cur.execute("select * from Documents where docid = {}".format(docid))
    result = cur.fetchone()
    
    similarResults = None
    similarDocs = requests.get("http://localhost:{}/5f5h8f5m/p5/?q={}&w={}".format(env["port"] - 1, re.sub(r'[^a-zA-Z0-9]+', " ", result["title"].lower()), 0.15))
    # convert the body text of a HTML request message into json and reads the hits part
    similarDocs = json.loads(similarDocs.text)
    similarDocs = similarDocs['hits']
    # get rid of the current document since one cannot show in its own similar docs.
    similarDocs = sorted(similarDocs, key = lambda x: x['score'], reverse = True)
    
    for i in range(min([10, len(similarDocs)])):
        if similarDocs[i]["docid"] == docid:
            similarDocs.remove(similarDocs[i])
            break

    if len(similarDocs) > 10:
        similarDocs = similarDocs[:10]

    similarResults = []
    for similarDoc in similarDocs:
        cur = db.cursor()
        cur.execute("select docid, title from Documents where docid = {}".format(similarDoc["docid"]))
        similarResults.append(cur.fetchone())


    options = {
        "result" : result,
        "similarResults" : similarResults
    }
    return render_template("Summary.html", **options)
