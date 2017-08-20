import os
from flask import *
import config
import re
import math
import json
from urllib.parse import unquote

app = Flask(__name__,template_folder='templates')

@app.route('/5f5h8f5m/p5/' ,methods = ['GET','POST'])
def index_route():
    url = unquote(request.url)
    atpos = url.find('w=')
    atand=url.find('&')
    weight=float(url[atpos+2:])
    print('weight:',weight)
    atpos=url.find('q=')
    query=url[atpos+2:atand]
    query=query.split(' ')
    scorerank={}
    
    for q in query:
        if q in stoplist:
            query.remove(q) 
    querylist={}
    for q in query:
        q=re.sub(r'[^a-zA-Z0-9]+','',str(q))
        q=str.lower(q)
        if len(q)==0: continue
        if q not in inverted_index_list:
            scorerank['hits']=[]
            return json.dumps(scorerank)
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
        ssum=ssum+weight_query[str(key)]*weight_query[str(key)]
        if docslist==None:
            docslist=set(inverted_index_list[str(key)]['docs'].keys())
        else:
            docslist&=set(inverted_index_list[str(key)]['docs'].keys())
    for key in weight_query:
        weight_query[str(key)]=weight_query[str(key)]/math.sqrt(ssum)
    if docslist !=None:
        for doc in docslist:
            sum2=0
            weight_doc={}
            for key in doc_key_list[doc]:
                tmp=inverted_index_list[str(key)]['docs'][doc]
                weight_doc[str(key)]=inverted_index_list[str(key)]['idf']*int(tmp[0])/float(tmp[1])
                if key in querylist:##
                    sum2=sum2+weight_doc[str(key)]*weight_query[str(key)]
            if doc not in pageranklist:
                score_doc[doc]=sum2/math.sqrt(sum(map(lambda x:x*x,weight_doc.values())))/math.sqrt(sum(map(lambda x:x*x,weight_query.values())))*(1.0-weight)
            else:
                score_doc[doc]=sum2/math.sqrt(sum(map(lambda x:x*x,weight_doc.values())))/math.sqrt(sum(map(lambda x:x*x,weight_query.values())))*(1.0-weight)+weight*pageranklist[doc]
    sorted(score_doc, key=score_doc.get, reverse=True)
    i=0
    scorerank['hits']={}
    list1=[]
    for key in score_doc:
        temp={}
        temp['score']=score_doc[key]
        temp['docid']=key  
        list1.append(temp)
        i=i+1
    scorerank['hits']=list1
    # option={
    #     "HAHA":scorerank
    # }
    # return render_template("inverted_index.html",**option)
    return json.dumps(scorerank)

if __name__ == '__main__':
    # listen on external IPs
    filename=open('test_final_output.txt','r')
    # filename=open("inverted index.txt",'r')
    inverted_index_list={}
    doc_key_list={}
    for line in filename.readlines():
        line=line[:len(line)-5]
        strlist=line.split(' ')
        inverted_index_list[strlist[0]]={}
        inverted_index_list[strlist[0]]['idf']=float(strlist[1])
        inverted_index_list[strlist[0]]['docs']={}
        i=2
        while i<=len(strlist)-3:
            inverted_index_list[strlist[0]]['docs'][strlist[i]]=strlist[i+1:i+3]
            if strlist[i] not in doc_key_list:
                doc_key_list[strlist[i]]=[]
            doc_key_list[strlist[i]].append(strlist[0])
            i=i+3

    filename.close()
    pagerank=open('pagerank.out','r')

    pageranklist={}
    for line in pagerank.readlines():
        tmp=line.split(',')
        pageranklist[str(tmp[0])]=float(tmp[1])

    pagerank.close()
    print("len",len(inverted_index_list))


    stoplist=[]
    stopwords=open('stopwords.txt','r')
    for line in stopwords.readlines():
        tmp=line[0:len(line)-1]
        stoplist.append(tmp)
    stopwords.close() 
    app.run(host=config.env['host'], port=config.env['port'], debug=True)
    