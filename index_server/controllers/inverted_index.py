from flask import *
from app import inverted_index_list,pageranklist
inverted_index = Blueprint('inverted_index', __name__, template_folder='templates')

@inverted_index.route('/' ,methods = ['GET','POST'])
def index_route():
    url = request.url
    atpos = url.find('w=')
    atand=url.find('&')
    weight=float(url[atpos+2:atand])
    atpos=url.find('q=')
    query=url[atpos+2:]
    query=query.split('+')
    querylist={}
    for q in query:
	    if q in querylist:
		    querylist[str(q)]=querylist[str(q)]+1
	    else:
		    querylist[str(q)]=1
    weight_query={}
    weight_doc={}
    score_doc={}
    ssum=0
    docslist=None
    for key in querylist:
	    weight_query[str(key)]=inverted_index_list[str(key)]['idf']*querylist[key]
	    ssum=ssum+weight_query[str(key)]
	    if docslist==None:
		    docslist=set(inverted_index_list[str(key)]['docs'].keys())
	    else:
		    docslist&=set(inverted_index_list[str(key)]['docs'].keys())
    for key in weight_query:
	    weight_query[str(key)]=weight_query[str(key)]/ssum

    for doc in docslist:
	    sum2=0
	    for key in querylist:
		    weight_doc[str(key)]=inverted_index_list[str(key)]['idf']*int(inverted_index_list[str(key)]['docs'][doc][0])/float(inverted_index_list[str(key)]['docs'][doc][1])
		    sum2=sum2+weight_doc[str(key)]*weight_query[str(key)]
	    score_doc[doc]=sum2/sqrt(sum(map(lambda x:x*x,weight_doc.values())))/sqrt(sum(map(lambda x:x*x,weight_query.values())))

    print('len is ',len(inverted_index_list))

    options = {
		'HAHA':1
		}
	
    return render_template("inverted_index.html", **options)