# querychinaillness
A data collection project for Chinese illness  from offical website

长春长生生产的疫苗有质量问题，是否和国内的传染病疫情有相关关系，这个工程从卫生部网站收集过去4年的传染病数据并分析。

项目用python 3,主要使用了urllib采集网页，pandas处理数据。

最终的结果用Excel表画图展示了百日咳等数据随时间变化的趋势。

Python用Eclipse工程,只有一个python文件getdata.py, 
1.获取html文件存入html目录
2.从html文件解析各种疾病的数据存入data目录下的rawdata.xlsx
3.手工拷贝数据到analysis.xlsx，加入了几个疾病随时间变化的趋势
