

with open('/mnt/hdfs/tmp/decom/20171225/_part-0-1.pending', 'r') as f:
    for line in f.readlines():
        list = line.split(",")
        print len(list)


s1 = "1514136468658,AdData,1acdafa7eb668af0|864297037163513,864297037163513,24844829,2017-12-25 01:27:48,33caec89-cc42-4378-9a95-d4d462cb1db9,android_ma_wechat,null,null,null,android,5.1,OPPO A59s,2.6.1.5,OPPO,WIFI,exposure,695,null,4-3,null,null,null,null,null,null,null,null,null,null,98959198-320b-4cdf-a277-7c0b1ab72815,null,864297037163513,1280,720,1,0,null,null,null,null,null,newsearn,1514136468658,null,0,0,null,null,null,null,null,null,null,null,search,null,null,null,null,null,null,null,null,2017-52,null,null,null," \
     "112.87.10.109,null,null,null,null,null,null,null,null,null"
s2 = "1514136468260,WebShare,22345762|22345762,22345762,22345762,2017-12-25 01:27:48,96b19df9-ee1c-48a7-aee3-2fd1e389a46d,,null,pv,分享落地页,android,null,null,null,null,null,null,null,null,null,null,null,null,null,null,https://www.coohua.com/share/xwz_article/pic_text.html?id=3501983&userId=22345762&environment=production,null,null,null,null,1608990833d3b-09687d0265e6c7-1504617e-230400-16089908344f4,null,22345762,640,360,null,1,null,null,null,null,null,newsearn,1514136468260,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,2017-52,null,null,null," \
     "115.152.30.49,null,null,null,mozilla/5.0 (linux; android 5.0.2; vivo y37 build/lrx22g; wv) applewebkit/537.36 (khtml, like gecko) version/4.0 chrome/53.0.2785.49 mobile mqqbrowser/6.2 tbs/043632 safari/537.36,null,null,null,null,nul"

print len(s1.split(","))
print len(s2.split(","))


sl1 = s1.split(",")
sl2 = s2.split(",")


for i in range(80):
    print str(i) + sl1[i]
    print str(i) + sl2[i]
