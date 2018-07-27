#encoding=utf-8
'''
Created on 2018年7月26日

@author: zhangxiao
'''
from urllib import request
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import pandas as pd

SITE="http://www.nhfpc.gov.cn/"
LISTURL=SITE+"zwgk/yqbb3/ejlist{}.shtml"

now=int(time.time())

df_num=None
df_die=None

def needreload(fname,reloadinterval):
    '''如果文件存在，并在在reloadinterval分钟取的就忽略
    '''
    if not os.path.exists(fname):
        print(fname)
        return True
    print("get statinfo") 
    changetime=os.path.getctime(fname)
    print((now-changetime)<reloadinterval*60)
    if (now-changetime)<reloadinterval*60:
        return False
    else:
        return True
    
def geturl(url,fname):
    print("get",url)
    reloadflag=needreload(fname,180)
    if reloadflag:
        response = request.urlopen(url,timeout=30)
        html = response.read()
        print("save to ",fname)
        f=open(fname,"w+b")
        f.write(html)
        f.close()

def convertlistno(no):
    listname="html"+os.sep+"list"+os.sep+"list{}.html"
    fname=listname.format(no)
    if no==1:
        url=LISTURL.format("")
    else:
        url=LISTURL.format("_"+str(no))
    return url,fname

def parselist(no):
    url,fname=convertlistno(no)
    geturl(url,fname)
    
    f=open(fname,"rb")
    content=f.read()
    #https://cuiqingcai.com/1319.html
    soup = BeautifulSoup(content,'lxml')
    ttlist=soup.select(".tt")
    print(ttlist)
    for item in ttlist:
        print(item.string)
        link=item.find("a").get("href")
        #将相对路径换为绝对路径
        if link.startswith("../"):
            link=urljoin(url,link)
        gatherdetail(item.string,link)
    print(content)
    f.close()
    
def parsedetail(year,month):
    print("parsing_{}_{}".format(year,month))
    name=convertdetailname(year, month)

    if not os.path.exists(name):
        print("Year:{} Month {} doesn't exist.".format(year,month))
        return 
    f=open(name,"rb")
    content=f.read()
    #https://blog.csdn.net/after95/article/details/52347160  获取表格数据
    soup=BeautifulSoup(content,'lxml')
    trs=soup.find_all(name='tr')

    global df_num
    global df_die
    
    col_ill=[]
    col_num=[]
    col_die=[]
    for tr in trs:
        _soup=BeautifulSoup(str(tr),"html.parser")
        tds=_soup.find_all(name='td')
        #for td in tds:
        #    print(td.span.string)
        #print(len(tds))
        #print(tds[0].find('span').string)
        
#        ss=tds[0].find_all('span')
        #print(ss[-1])
#         if len(ss)==0 or ss[-1].string is None or len(ss[-1].string)==0:
#             print(tds[0])
#             continue
#         ss=ss[-1]
#         while ss.string.find('span')!=-1:
#             ss=ss.span
#        illname=ss.string
        span_list=tds[0].find_all('span')
        if len(span_list)>0:
            illname=span_list[0].string
            if illname is None:
                #病毒性肝炎* 和  人感染H7N9禽流感
                try:
                    illname=span_list[0].span.string
                except AttributeError:
                    print(span_list[0])
                    continue
                    #print(len(span_list),span_list[1].string)
        else:
            print(tds[0])
            continue
        
        if illname is None or illname=="":
            continue
        #if illname is None:
        #    illname=tds[0].span[0].string
#         if illname.find("*")!=-1:
#             illname=illname.replace('*',"")
        col_ill.append(illname)
        col_num.append(tds[1].span.string)
        col_die.append(tds[2].span.string)

    pref="{}_{}_".format(year,month)
    d_num={"key":col_ill,pref+"num":col_num}
    d_die={"key":col_ill,pref+"die":col_die}
    df1_num=pd.DataFrame.from_dict(d_num)
    df1_die=pd.DataFrame.from_dict(d_die)
    #https://blog.csdn.net/milton2017/article/details/54406482/
    #df=df.join(df1,on='key') #pd.merge(df,df1,)    
    if df_num is None:
        df_num=df1_num
        df_die=df1_die
    else:
        df_num=pd.merge(df_num,df1_num,on="key",how = 'outer')
        df_die=pd.merge(df_die,df1_die,on="key",how = 'outer')
    #print(df)
    
    f.close()
    
    
def gatherlist(maxpage):
    #第一页是zwgk/yqbb3/ejlist.shtml
    #第二页开始是zwgk/yqbb3/ejlist_n.shtml，这里n表示第几页
    for n in range(1,maxpage):
        url,fname=convertlistno(n)
        geturl(url,fname)
   
    pass

def convertdetailname(year,month):
    name="html"+os.sep+"detail"+os.sep+"{}_{}.html".format(year,month)
    return name

def gatherdetail(name,url):
    year=""
    month=""
    if name.find(u"年"):
        l=re.findall(r"([1-9]\d*)年",name)
        if len(l)>0:
            year=l[0]
    else:
        return
    
    if name.find(u"月"):
        l=re.findall(r"([1-9]\d*)月",name)
        if len(l)>0:
            month=l[0]
    fname=convertdetailname(year,month)
    
    geturl(url,fname)


def createdir(p):
    if not os.path.exists(p):
        os.mkdir(p)

if __name__ == '__main__':
    createdir("html")
    createdir("data")
    createdir("html"+os.sep+"list")
    createdir("html"+os.sep+"detail")
    
    #for n in range(1,20):
    #    parselist(n)
    for year in range(2014,2018):
        for month in range(1,13):
            if year==2014 and (month==10 or month==11):
                continue  #这两个月的格式不一致
            parsedetail(year,month)
            
    parsedetail(2018,1)
    parsedetail(2018,2)
    #https://blog.csdn.net/brink_compiling/article/details/76890198?locationNum=7&fps=1
    writer = pd.ExcelWriter('data'+os.sep+'rawdata.xlsx')
    df_num.to_excel(writer,'number')
    df_die.to_excel(writer,'die')
    writer.save()

    
    #parselist(1)