# -*- coding: utf-8 -*-
import web
import os
import redis

# Entrance of web access
class Subway:
    def __init__(self):
        self.app_root       = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root,'template')
        self.render         = web.template.render(self.templates_root)
        self.redis          = redis.StrictRedis(password=12345678, decode_responses=True)

    def GET(self):
        return self.render.subway("地铁线路查询","","","","")

    def POST(self):
        form = web.input()

        stations = stations_init()
        lines    = lines_init(stations)

        result   = Route()
        temp     = Route()
        start    = get_station_by_name(str(form['start']), stations)
        end      = get_station_by_name(str(form['end']), stations)

        if start is not None and end is not None:
            key = start.name + ':' + end.name + ':' + form['rule']
            if self.redis.exists(key):
                output = self.redis.get(key)
            else:
                #compute(start, end, None, 0, temp, result, form['rule'])
                compute2(start, end, result, form['rule'])
                self.redis.set(key, result.output())
                output = result.output()
            return self.render.subway("路线查询结果", start.name, end.name, form['rule'], output)
        else:
            return self.render.subway("路线查询结果", "", "", form['rule'], result.output())

# Class for subway line
class Line:
    def __init__(self, number, name, is_loop):
        self.number   = number
        self.name     = name
        self.is_loop  = is_loop
        self.stations = []

    def insert(self, station):
        self.stations.append(station)

    def distance(self, start, end):
        if self.is_loop is True:
            return min(abs(self.stations.index(start) - self.stations.index(end)),
                   abs(len(self.stations) - abs(self.stations.index(start) - self.stations.index(end))))
        else:
            return abs(self.stations.index(start) - self.stations.index(end))

    def has_station(self, station):
        if station in self.stations:
            return True
        else:
            return False

    def is_loop(self):
        return self.is_loop

    def get_line_number(self):
        return self.number
    def get_line_name(self):
        return self.name
    def transfer_stations(self):
        for i in self.stations:
            if i.is_transfer() is True:
                yield i

# Class for subway station
class Station:
    def __init__(self, name):
        self.name   = name
        self.lines  = []
        self.passed = False
        self.refcnt = 0
        self.sfrom  = None
        self.efrom  = None
    def set_line(self, line):
        self.lines.append(line)
    def get_line(self):
        return self.lines
    def is_transfer(self):
        if len(self.lines) > 1:
            return True
        else:
            return False
    def is_passed(self):
        return self.passed
    def set_passed(self):
        self.passed = True
    def clear_passed(self):
        self.passed = False
    def get(self):
        self.refcnt += 1
    def put(self):
        self.refcnt -= 1
    def get_refcnt(self):
        return self.refcnt
    def set_sfrom(self, stop):
        self.sfrom = stop
    def set_efrom(self, stop):
        self.efrom = stop

# Class for route
class Route:
    def __init__(self):
        self.route = []
        self.debug = 0
    def push(self, stop):
        self.route.append(stop)
        stop.get()
        stop.set_passed()
        if self.debug > 0:
            print("push", stop.name)
    def pop(self):
        stop = self.route.pop()
        stop.put()
        if self.debug > 0:
            print("pop", stop.name)
        return stop
    def extend(self,route):
        self.route.extend(route.route)
    def show(self):
        for st in self.route:
            print(st.name)
    def compute_stops(self):
        stops = 0
        if len(self.route) == 0: return 0xFFFFFFFF
        for i in range(0, len(self.route)-1):
            stops += compute_same_line(self.route[i],self.route[i+1])
        return stops
    def transer_times(self):
        return len(self.route) - 1
    def is_empty(self):
        if len(self.route) == 0:
            return True
        else:
            return False
    def output(self):
        buf = ''
        if self.is_empty() is True:
            buf += '没有找到匹配路线，请重新查询'
            return  buf
        for i in range(0, len(self.route)-1):
            line = get_shortest_line(self.route[i], self.route[i+1])
            stops = line.distance(self.route[i], self.route[i+1])
            if i == 0:
                buf += '在' + self.route[i].name + '站搭乘地铁' + line.get_line_name()  + '线经过' + str(stops) + '站到达' + self.route[i+1].name + '站，'
            else:
                buf += '在' + self.route[i].name + '站换乘地铁' + line.get_line_name() + '线经过' + str(stops) + '站到达' + self.route[i + 1].name + '站，'
        buf += '行程总共' + str(self.compute_stops()) + '站'
        return buf

# global variable
global stations
stations = {}

# Register stations
def stations_init():
    # line 4
    tiangy   = Station("天宫院")
    stations.update({"天宫院":tiangy})
    yyjd     = Station("生物医药基地")
    stations.update({"生物医药基地":yyjd})
    yihz     = Station("义和庄")
    stations.update({"义和庄":yihz})
    hchcz    = Station("黄村火车站")
    stations.update({"黄村火车站":hchcz})
    hcxdj    = Station("黄村西大街")
    stations.update({"黄村西大街":hcxdj})
    zaoy     = Station("枣园")
    stations.update({"枣园":zaoy})
    gmdn     = Station("高米店南")
    stations.update({"高米店南":gmdn})
    gmdb     = Station("高米店北")
    stations.update({"高米店北":gmdb})
    xihm     = Station("西红门")
    stations.update({"西红门":xihm})
    xingong  = Station("新宫")
    stations.update({"新宫":xingong})
    gyxq     = Station("公益西桥")
    stations.update({"公益西桥":gyxq})
    jiaomx   = Station("角门西")
    stations.update({"角门西":jiaomx})
    majp     = Station("马家堡")
    stations.update({"马家堡":majp})
    bjnz     = Station("北京南站")
    stations.update({"北京南站":bjnz})
    taort    = Station("陶然亭")
    stations.update({"陶然亭":taort})
    caisk    = Station("菜市口")
    stations.update({"菜市口":caisk})
    xuanwm   = Station("宣武门")
    stations.update({"宣武门":xuanwm})
    xidan    = Station("西单")
    stations.update({"西单":xidan})
    ljht     = Station("灵境胡同")
    stations.update({"灵境胡同":ljht})
    xisi     = Station("西四")
    stations.update({"西四":xisi})
    pingal   = Station("平安里")
    stations.update({"平安里":pingal})
    xinjk    = Station("新街口")
    stations.update({"新街口":xinjk})
    xizm     = Station("西直门")
    stations.update({"西直门":xizm})
    dongwy   = Station("动物园")
    stations.update({"动物园":dongwy})
    gjtsg    = Station("国家图书馆")
    stations.update({"国家图书馆":gjtsg})
    weigc    = Station("魏公村")
    stations.update({"魏公村":weigc})
    rmdx     = Station("人民大学")
    stations.update({"人民大学":rmdx})
    zhonggc  = Station("中关村")
    stations.update({"中关村":zhonggc})
    bjdxdm   = Station("北京大学东门")
    stations.update({"北京大学东门":bjdxdm})
    yuanmy   = Station("圆明园")
    stations.update({"圆明园":yuanmy})
    xiyuan   = Station("西苑")
    stations.update({"西苑":xiyuan})
    beigm    = Station("北宫门")
    stations.update({"北宫门":beigm})
    ahqb     = Station("安河桥北")
    stations.update({"安河桥北":ahqb})

    # line 10
    jiaomd     = Station("角门东")
    stations.update({"角门东":jiaomd})
    dahm       = Station("大红门")
    stations.update({"大红门":dahm})
    shilz      = Station("石榴庄")
    stations.update({"石榴庄":shilz})
    songjz     = Station("宋家庄")
    stations.update({"宋家庄":songjz})
    chengss    = Station("成寿寺")
    stations.update({"成寿寺":chengss})
    fenzs      = Station("分钟寺")
    stations.update({"分钟寺":fenzs})
    shilh      = Station("十里河")
    stations.update({"十里河":shilh})
    panjy      = Station("潘家园")
    stations.update({"潘家园":panjy})
    jinsong    = Station("劲松")
    stations.update({"劲松":jinsong})
    shuangjing = Station("双井")
    stations.update({"双井":shuangjing})
    guomao     = Station("国贸")
    stations.update({"国贸":guomao})
    jtxz       = Station("金台夕照")
    stations.update({"金台夕照":jtxz})
    hujl       = Station("呼家楼")
    stations.update({"呼家楼":hujl})
    tuanjh     = Station("团结湖")
    stations.update({"团结湖":tuanjh})
    nyzlg      = Station("农业展览馆")
    stations.update({"农业展览馆":nyzlg})
    liangmq    = Station("亮马桥")
    stations.update({"亮马桥":liangmq})
    sanyq      = Station("三元桥")
    stations.update({"三元桥":sanyq})
    taiyg      = Station("太阳宫")
    stations.update({"太阳宫":taiyg})
    shaoyj     = Station("芍药居")
    stations.update({"芍药居":shaoyj})
    hxxjnk     = Station("惠新西街南口")
    stations.update({"惠新西街南口":hxxjnk})
    anzm       = Station("安贞门")
    stations.update({"安贞门":anzm})
    beitc      = Station("北土城")
    stations.update({"北土城":beitc})
    mudy       = Station("牡丹园")
    stations.update({"牡丹园":mudy})
    xitc       = Station("西土城")
    stations.update({"西土城":xitc})
    zhiclu      = Station("知春路")
    stations.update({"知春路":zhiclu})
    zhicli      = Station("知春里")
    stations.update({"知春里":zhicli})
    hdhz        = Station("海淀黄庄")
    stations.update({"海淀黄庄":hdhz})
    suzj        = Station("苏州街")
    stations.update({"苏州街":suzj})
    bagou       = Station("巴沟")
    stations.update({"巴沟":bagou})
    huoqy       = Station("火器营")
    stations.update({"火器营":huoqy})
    changcq     = Station("长春桥")
    stations.update({"长春桥":changcq})
    chedg       = Station("车道沟")
    stations.update({"车道沟":chedg})
    ciss        = Station("慈寿寺")
    stations.update({"慈寿寺":ciss})
    xidyt       = Station("西钓鱼台")
    stations.update({"西钓鱼台":xidyt})
    gongzf      = Station("公主坟")
    stations.update({"公主坟":gongzf})
    lianhq      = Station("莲花桥")
    stations.update({"莲花桥":lianhq})
    liulq       = Station("六里桥")
    stations.update({"六里桥":liulq})
    xiju        = Station("西局")
    stations.update({"西局":xiju})
    niwa        = Station("泥洼")
    stations.update({"泥洼":niwa})
    fengtz      = Station("丰台站")
    stations.update({"丰台站":fengtz})
    shoujm      = Station("首经贸")
    stations.update({"首经贸":shoujm})
    jijm        = Station("纪家庙")
    stations.update({"纪家庙":jijm})
    caoq        = Station("草桥")
    stations.update({"草桥":caoq})

    # line 1
    pinggy      = Station("苹果园")
    stations.update({"苹果园":pinggy})
    gucheng     = Station("古城")
    stations.update({"古城":gucheng})
    bjyly       = Station("八角游乐园")
    stations.update({"八角游乐园":bjyly})
    babs        = Station("八宝山")
    stations.update({"八宝山":babs})
    yuql        = Station("玉泉路")
    stations.update({"玉泉路":yuql})
    wuks        = Station("五棵松")
    stations.update({"五棵松":wuks})
    wansl       = Station("万寿路")
    stations.update({"万寿路":wansl})
    jsbwg       = Station("军事博物馆")
    stations.update({"军事博物馆":jsbwg})
    muxd        = Station("木樨地")
    stations.update({"木樨地":muxd})
    nlsl        = Station("南礼士路")
    stations.update({"南礼士路":nlsl})
    fuxm        = Station("复兴门")
    stations.update({"复兴门":fuxm})
    tamx        = Station("天安门西")
    stations.update({"天安门西":tamx})
    tamd        = Station("天安门东")
    stations.update({"天安门东":tamd})
    wangfj      = Station("王府井")
    stations.update({"王府井":wangfj})
    dongdan     = Station("东单")
    stations.update({"东单":dongdan})
    jiangm      = Station("建国门")
    stations.update({"建国门":jiangm})
    yongal      = Station("永安里")
    stations.update({"永安里":yongal})
    dawl        = Station("大望路")
    stations.update({"大望路":dawl})
    sihui       = Station("四惠")
    stations.update({"四惠":sihui})
    sihuid      = Station("四惠东")
    stations.update({"四惠东":sihuid})

    # line 2
    xuanwm     = Station("宣武门")
    stations.update({"宣武门":xuanwm})
    hepm       = Station("和平门")
    stations.update({"和平门":hepm})
    qianm      = Station("前门")
    stations.update({"前门":qianm})
    chongwm    = Station("崇文门")
    stations.update({"崇文门":chongwm})
    beijz      = Station("北京站")
    stations.update({"北京站":beijz})
    chaoym     = Station("朝阳门")
    stations.update({"朝阳门":chaoym})
    dsst       = Station("东四十条")
    stations.update({"东四十条":dsst})
    dongzm     = Station("东直门")
    stations.update({"东直门":dongzm})
    yonghg     = Station("雍和宫")
    stations.update({"雍和宫":yonghg})
    andm       = Station("安定门")
    stations.update({"安定门":andm})
    gldj       = Station("鼓楼大街")
    stations.update({"鼓楼大街":gldj})
    jist       = Station("积水潭")
    stations.update({"积水潭":jist})
    chegz      = Station("车公庄")
    stations.update({"车公庄":chegz})
    fucm       = Station("阜成门")
    stations.update({"阜成门":fucm})
    changcj    = Station("长椿街")
    stations.update({"长椿街":changcj})

    # line 5
    songjz     = Station("宋家庄")
    stations.update({"宋家庄":songjz})
    liujy      = Station("刘家窑")
    stations.update({"刘家窑":liujy})
    puhy       = Station("蒲黄榆")
    stations.update({"蒲黄榆":puhy})
    ttdm       = Station("天坛东门")
    stations.update({"天坛东门":ttdm})
    ciqk       = Station("磁器口")
    stations.update({"磁器口":ciqk})
    dengsk     = Station("灯市口")
    stations.update({"灯市口":dengsk})
    dongsi     = Station("东四")
    stations.update({"东四":dongsi})
    zzzl       = Station("张自忠路")
    stations.update({"张自忠路":zzzl})
    beixq      = Station("北新桥")
    stations.update({"北新桥":beixq})
    hplbj      = Station("和平里北街")
    stations.update({"和平里北街":hplbj})
    hpxq       = Station("和平西桥")
    stations.update({"和平西桥":hpxq})
    hxxjbk     = Station("惠新西街北口")
    stations.update({"惠新西街北口":hxxjbk})
    dtld       = Station("大屯路东")
    stations.update({"大屯路东":dtld})
    bylb       = Station("北苑路北")
    stations.update({"北苑路北":bylb})
    lsqn       = Station("立水桥南")
    stations.update({"立水桥南":lsqn})
    lisq       = Station("立水桥")
    stations.update({"立水桥":lisq})
    ttyn       = Station("天通苑南")
    stations.update({"天通苑南":ttyn})
    tianty     = Station("天通苑")
    stations.update({"天通苑":tianty})
    ttyb       = Station("天通苑北")
    stations.update({"天通苑北":ttyb})

    # line 6
    hdwlj      = Station("海淀五路居")
    stations.update({"海淀五路居":hdwlj})
    huayq      = Station("花园桥")
    stations.update({"花园桥":huayq})
    bsqn       = Station("白石桥南")
    stations.update({"白石桥南":bsqn})
    cgzx       = Station("车公庄西")
    stations.update({"车公庄西":cgzx})
    beihb      = Station("北海北")
    stations.update({"北海北":beihb})
    nlgx       = Station("南锣鼓巷")
    stations.update({"南锣鼓巷":nlgx})
    dongdq     = Station("东大桥")
    stations.update({"东大桥":dongdq})
    jintl      = Station("金台路")
    stations.update({"金台路":jintl})
    shilb      = Station("十里堡")
    stations.update({"十里堡":shilb})
    qingnl     = Station("青年路")
    stations.update({"青年路":qingnl})
    dalp       = Station("褡裢坡")
    stations.update({"褡裢坡":dalp})
    huangq     = Station("黄渠")
    stations.update({"黄渠":huangq})
    changy     = Station("常营")
    stations.update({"常营":changy})
    caof       = Station("草房")
    stations.update({"草房":caof})
    wzxyl      = Station("物资学院路")
    stations.update({"物资学院路":wzxyl})
    tzbg       = Station("通州北关")
    stations.update({"通州北关":tzbg})
    tongym     = Station("通运门")
    stations.update({"通运门":tongym})
    byhx       = Station("北运河西")
    stations.update({"北运河西":byhx})
    byhd       = Station("北运河东")
    stations.update({"北运河东":byhd})
    haojf      = Station("郝家府")
    stations.update({"郝家府":haojf})
    dongxy     = Station("东夏园")
    stations.update({"东夏园":dongxy})
    lucheng     = Station("潞城")
    stations.update({"潞城":lucheng})

    # line 7
    bjxz       = Station("北京西站")
    stations.update({"北京西站":bjxz})
    wanzi      = Station("湾子")
    stations.update({"湾子":wanzi})
    dagy       = Station("达官营")
    stations.update({"达官营":dagy})
    gamn       = Station("广安门内")
    stations.update({"广安门内":gamn})
    hufq       = Station("虎坊桥")
    stations.update({"虎坊桥":hufq})
    zhusk      = Station("珠市口")
    stations.update({"珠市口":zhusk})
    qiaow      = Station("桥湾")
    stations.update({"桥湾":qiaow})
    gqmn       = Station("广渠门内")
    stations.update({"广渠门内":gqmn})
    gqmw       = Station("广渠门外")
    stations.update({"广渠门外":gqmw})
    jiuls      = Station("九龙山")
    stations.update({"九龙山":jiuls})
    dajt       = Station("大郊亭")
    stations.update({"大郊亭":dajt})
    baizw      = Station("百子湾")
    stations.update({"百子湾":baizw})
    huag       = Station("化工")
    stations.update({"化工":huag})
    nlzz       = Station("南楼梓庄")
    stations.update({"南楼梓庄":nlzz})
    hlgjq      = Station("欢乐谷景区")
    stations.update({"欢乐谷景区":hlgjq})
    fatou      = Station("垡头")
    stations.update({"垡头":fatou})
    shuangh    = Station("双合")
    stations.update({"双合":shuangh})
    jiaohc     = Station("焦化厂")
    stations.update({"焦化厂":jiaohc})

    # line 8
    zhuxz      = Station("朱辛庄")
    stations.update({"朱辛庄":zhuxz})
    yuzl       = Station("育知路")
    stations.update({"育知路":yuzl})
    pingxf     = Station("平西府")
    stations.update({"平西府":pingxf})
    hlgddj     = Station("回龙观东大街")
    stations.update({"回龙观东大街":hlgddj})
    huoy       = Station("霍营")
    stations.update({"霍营":huoy})
    yuxin      = Station("育新")
    stations.update({"育新":yuxin})
    xixk       = Station("西小口")
    stations.update({"西小口":xixk})
    yongtz     = Station("永泰庄")
    stations.update({"永泰庄":yongtz})
    lincq      = Station("林萃桥")
    stations.update({"林萃桥":lincq})
    slgynm     = Station("森林公园南门")
    stations.update({"森林公园南门":slgynm})
    alpkgy     = Station("奥林匹克公园")
    stations.update({"奥林匹克公园":alpkgy})
    atzx       = Station("奥体中心")
    stations.update({"奥体中心":atzx})
    anhq       = Station("安华桥")
    stations.update({"安华桥":anhq})
    adlbj      = Station("安德里北街")
    stations.update({"安德里北街":adlbj})
    shich      = Station("什刹海")
    stations.update({"什刹海":shich})

    # line 9
    baidz      = Station("白堆子")
    stations.update({"白堆子":baidz})
    llqd       = Station("六里桥东")
    stations.update({"六里桥东":llqd})
    qilz       = Station("七里庄")
    stations.update({"七里庄":qilz})
    ftddj      = Station("丰台东大街")
    stations.update({"丰台东大街":ftddj})
    ftnl       = Station("丰台南路")
    stations.update({"丰台南路":ftnl})
    keyl       = Station("科怡路")
    stations.update({"科怡路":keyl})
    ftkjy      = Station("丰台科技园")
    stations.update({"丰台科技园":ftkjy})
    guogz      = Station("郭公庄")
    stations.update({"郭公庄":guogz})

    # line 13
    dazs       = Station("大钟寺")
    stations.update({"大钟寺":dazs})
    wudk       = Station("五道口")
    stations.update({"五道口":wudk})
    shangdi    = Station("上地")
    stations.update({"上地":shangdi})
    xieq       = Station("西二旗")
    stations.update({"西二旗":xieq})
    longze     = Station("龙泽")
    stations.update({"龙泽":longze})
    huilg      = Station("回龙观")
    stations.update({"回龙观":huilg})
    beiyuan    = Station(" 北苑")
    stations.update({"北苑":beiyuan})
    wangjx     = Station("望京西")
    stations.update({"望京西":wangjx})
    guangxm    = Station("光熙门")
    stations.update({"光熙门":guangxm})
    liuf       = Station("柳芳")
    stations.update({"柳芳":liuf})

    # line 14
    zhanggz    = Station("张郭庄")
    stations.update({"张郭庄":zhanggz})
    yuanby     = Station("园博园")
    stations.update({"园博园":yuanby})
    dawy       = Station("大瓦窑")
    stations.update({"大瓦窑":dawy})
    guozz      = Station("郭庄子")
    stations.update({"郭庄子":guozz})
    dajing     = Station("大井")
    stations.update({"大井":dajing})
    taorq      = Station("陶然桥")
    stations.update({"陶然桥":taorq})
    ydmw       = Station("永定门外")
    stations.update({"永定门外":ydmw})
    jingtai    = Station("景泰")
    stations.update({"景泰":jingtai})
    fangz      = Station("方庄")
    stations.update({"方庄":fangz})
    bgdxm      = Station("北工大西门")
    stations.update({"北工大西门":bgdxm})
    pingly     = Station("平乐园")
    stations.update({"平乐园":pingly})
    cygy       = Station("朝阳公园")
    stations.update({"朝阳公园":cygy})
    zaoying    = Station("枣营")
    stations.update({"枣营":zaoying})
    dfbq       = Station("东风北桥")
    stations.update({"东风北桥":dfbq})
    jiangt     = Station("将台")
    stations.update({"将台":jiangt})
    gaojy      = Station("高家园")
    stations.update({"高家园":gaojy})
    wangjn     = Station("望京南")
    stations.update({"望京南":wangjn})
    futong     = Station("阜通")
    stations.update({"阜通":futong})
    wangjing   = Station("望京")
    stations.update({"望京":wangjing})
    donghq     = Station("东湖渠")
    stations.update({"东湖渠":donghq})
    laigy      = Station("来广营")
    stations.update({"来广营":laigy})
    shangz     = Station("善各庄")
    stations.update({"善各庄":shangz})

    # line 15
    qhdlxk     = Station("清华东路西口")
    stations.update({"清华东路西口":qhdlxk})
    liudk      = Station("六道口")
    stations.update({"六道口":liudk})
    beist      = Station("北沙滩")
    stations.update({"北沙滩":beist})
    anll       = Station("安立路")
    stations.update({"安立路":anll})
    guanz      = Station("关庄")
    stations.update({"关庄":guanz})
    wangjd     = Station("望京东")
    stations.update({"望京东":wangjd})
    cuigz      = Station("崔各庄")
    stations.update({"崔各庄":cuigz})
    maqy       = Station("马泉营")
    stations.update({"马泉营":maqy})
    sunhe      = Station("孙河")
    stations.update({"孙河":sunhe})
    guozhan    = Station("国展")
    stations.update({"国展":guozhan})
    hualk      = Station("花梨坎")
    stations.update({"花梨坎":hualk})
    housy      = Station("后沙峪")
    stations.update({"后沙峪":housy})
    nanfx      = Station("南法信")
    stations.update({"南法信":nanfx})
    shimen     = Station("石门")
    stations.update({"石门":shimen})
    shunyi     = Station("顺义")
    stations.update({"顺义":shunyi})
    fengbo     = Station("俸伯")
    stations.update({"俸伯":fengbo})

    # line BaTong

    # line ChangPing

    # line YiZhuang

    # line FangShan
    suzhuang   = Station("苏庄")
    stations.update({"苏庄":suzhuang})
    lxng       = Station("良乡南关")
    stations.update({"良乡南关":lxng})
    lxdxcx     = Station("良乡大学城西")
    stations.update({"良乡大学城西":lxdxcx})
    lxdxc      = Station("良乡大学城")
    stations.update({"良乡大学城":lxdxc})
    lxdxcb     = Station("良乡大学城北")
    stations.update({"良乡大学城北":lxdxcb})
    guangyc    = Station("广阳城")
    stations.update({"广阳城":guangyc})
    libf       = Station("篱笆房")
    stations.update({"篱笆房":libf})
    changy     = Station("长阳")
    stations.update({"长阳":changy})
    daotian    = Station("稻田")
    stations.update({"稻田":daotian})
    dabt       = Station("大葆台")
    stations.update({"大葆台":dabt})

    return stations

# Line 4 initialization
def line4_init(stations):
    line = Line(4, "4号", False)
    station = stations["天宫院"]
    station.set_line(line)
    line.insert(station)
    station = stations["生物医药基地"]
    station.set_line(line)
    line.insert(station)
    station = stations["义和庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["黄村火车站"]
    station.set_line(line)
    line.insert(station)
    station = stations["黄村西大街"]
    station.set_line(line)
    line.insert(station)
    station = stations["枣园"]
    station.set_line(line)
    line.insert(station)
    station = stations["高米店南"]
    station.set_line(line)
    line.insert(station)
    station = stations["高米店北"]
    station.set_line(line)
    line.insert(station)
    station = stations["西红门"]
    station.set_line(line)
    line.insert(station)
    station = stations["新宫"]
    station.set_line(line)
    line.insert(station)
    station = stations["公益西桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["角门西"]
    station.set_line(line)
    line.insert(station)
    station = stations["马家堡"]
    station.set_line(line)
    line.insert(station)
    station = stations["北京南站"]
    station.set_line(line)
    line.insert(station)
    station = stations["陶然亭"]
    station.set_line(line)
    line.insert(station)
    station = stations["菜市口"]
    station.set_line(line)
    line.insert(station)
    station = stations["宣武门"]
    station.set_line(line)
    line.insert(station)
    station = stations["西单"]
    station.set_line(line)
    line.insert(station)
    station = stations["灵境胡同"]
    station.set_line(line)
    line.insert(station)
    station = stations["西四"]
    station.set_line(line)
    line.insert(station)
    station = stations["平安里"]
    station.set_line(line)
    line.insert(station)
    station = stations["新街口"]
    station.set_line(line)
    line.insert(station)
    station = stations["西直门"]
    station.set_line(line)
    line.insert(station)
    station = stations["动物园"]
    station.set_line(line)
    line.insert(station)
    station = stations["国家图书馆"]
    station.set_line(line)
    line.insert(station)
    station = stations["魏公村"]
    station.set_line(line)
    line.insert(station)
    station = stations["人民大学"]
    station.set_line(line)
    line.insert(station)
    station = stations["海淀黄庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["中关村"]
    station.set_line(line)
    line.insert(station)
    station = stations["北京大学东门"]
    station.set_line(line)
    line.insert(station)
    station = stations["圆明园"]
    station.set_line(line)
    line.insert(station)
    station = stations["西苑"]
    station.set_line(line)
    line.insert(station)
    station = stations["北宫门"]
    station.set_line(line)
    line.insert(station)
    station = stations["安河桥北"]
    station.set_line(line)
    line.insert(station)

    return line

# Line 10 initalization
def line10_init(stations):
    line = Line(10, "10号", True)
    station = stations["角门西"]
    station.set_line(line)
    line.insert(station)
    station = stations["角门东"]
    station.set_line(line)
    line.insert(station)
    station = stations["大红门"]
    station.set_line(line)
    line.insert(station)
    station = stations["石榴庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["宋家庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["成寿寺"]
    station.set_line(line)
    line.insert(station)
    station = stations["分钟寺"]
    station.set_line(line)
    line.insert(station)
    station = stations["十里河"]
    station.set_line(line)
    line.insert(station)
    station = stations["潘家园"]
    station.set_line(line)
    line.insert(station)
    station = stations["劲松"]
    station.set_line(line)
    line.insert(station)
    station = stations["双井"]
    station.set_line(line)
    line.insert(station)
    station = stations["国贸"]
    station.set_line(line)
    line.insert(station)
    station = stations["金台夕照"]
    station.set_line(line)
    line.insert(station)
    station = stations["呼家楼"]
    station.set_line(line)
    line.insert(station)
    station = stations["团结湖"]
    station.set_line(line)
    line.insert(station)
    station = stations["农业展览馆"]
    station.set_line(line)
    line.insert(station)
    station = stations["亮马桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["三元桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["太阳宫"]
    station.set_line(line)
    line.insert(station)
    station = stations["芍药居"]
    station.set_line(line)
    line.insert(station)
    station = stations["惠新西街南口"]
    station.set_line(line)
    line.insert(station)
    station = stations["安贞门"]
    station.set_line(line)
    line.insert(station)
    station = stations["北土城"]
    station.set_line(line)
    line.insert(station)
    station = stations["牡丹园"]
    station.set_line(line)
    line.insert(station)
    station = stations["西土城"]
    station.set_line(line)
    line.insert(station)
    station = stations["知春路"]
    station.set_line(line)
    line.insert(station)
    station = stations["知春里"]
    station.set_line(line)
    line.insert(station)
    station = stations["海淀黄庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["苏州街"]
    station.set_line(line)
    line.insert(station)
    station = stations["巴沟"]
    station.set_line(line)
    line.insert(station)
    station = stations["火器营"]
    station.set_line(line)
    line.insert(station)
    station = stations["长春桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["车道沟"]
    station.set_line(line)
    line.insert(station)
    station = stations["慈寿寺"]
    station.set_line(line)
    line.insert(station)
    station = stations["西钓鱼台"]
    station.set_line(line)
    line.insert(station)
    station = stations["公主坟"]
    station.set_line(line)
    line.insert(station)
    station = stations["莲花桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["六里桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["西局"]
    station.set_line(line)
    line.insert(station)
    station = stations["泥洼"]
    station.set_line(line)
    line.insert(station)
    station = stations["丰台站"]
    station.set_line(line)
    line.insert(station)
    station = stations["首经贸"]
    station.set_line(line)
    line.insert(station)
    station = stations["纪家庙"]
    station.set_line(line)
    line.insert(station)
    station = stations["草桥"]
    station.set_line(line)
    line.insert(station)
    return line

def line1_init(stations):
    line = Line(1, "1号", False)
    station = stations["苹果园"]
    station.set_line(line)
    line.insert(station)
    station = stations["古城"]
    station.set_line(line)
    line.insert(station)
    station = stations["八角游乐园"]
    station.set_line(line)
    line.insert(station)
    station = stations["八宝山"]
    station.set_line(line)
    line.insert(station)
    station = stations["玉泉路"]
    station.set_line(line)
    line.insert(station)
    station = stations["五棵松"]
    station.set_line(line)
    line.insert(station)
    station = stations["万寿路"]
    station.set_line(line)
    line.insert(station)
    station = stations["公主坟"]
    station.set_line(line)
    line.insert(station)
    station = stations["军事博物馆"]
    station.set_line(line)
    line.insert(station)
    station = stations["木樨地"]
    station.set_line(line)
    line.insert(station)
    station = stations["南礼士路"]
    station.set_line(line)
    line.insert(station)
    station = stations["复兴门"]
    station.set_line(line)
    line.insert(station)
    station = stations["西单"]
    station.set_line(line)
    line.insert(station)
    station = stations["天安门西"]
    station.set_line(line)
    line.insert(station)
    station = stations["天安门东"]
    station.set_line(line)
    line.insert(station)
    station = stations["王府井"]
    station.set_line(line)
    line.insert(station)
    station = stations["东单"]
    station.set_line(line)
    line.insert(station)
    station = stations["建国门"]
    station.set_line(line)
    line.insert(station)
    station = stations["永安里"]
    station.set_line(line)
    line.insert(station)
    station = stations["国贸"]
    station.set_line(line)
    line.insert(station)
    station = stations["大望路"]
    station.set_line(line)
    line.insert(station)
    station = stations["四惠"]
    station.set_line(line)
    line.insert(station)
    station = stations["四惠东"]
    station.set_line(line)
    line.insert(station)

    return line

def line2_init(stations):
    line = Line(2, "2号", True)
    station = stations["宣武门"]
    station.set_line(line)
    line.insert(station)
    station = stations["和平门"]
    station.set_line(line)
    line.insert(station)
    station = stations["前门"]
    station.set_line(line)
    line.insert(station)
    station = stations["崇文门"]
    station.set_line(line)
    line.insert(station)
    station = stations["北京站"]
    station.set_line(line)
    line.insert(station)
    station = stations["建国门"]
    station.set_line(line)
    line.insert(station)
    station = stations["朝阳门"]
    station.set_line(line)
    line.insert(station)
    station = stations["东四十条"]
    station.set_line(line)
    line.insert(station)
    station = stations["东直门"]
    station.set_line(line)
    line.insert(station)
    station = stations["雍和宫"]
    station.set_line(line)
    line.insert(station)
    station = stations["安定门"]
    station.set_line(line)
    line.insert(station)
    station = stations["鼓楼大街"]
    station.set_line(line)
    line.insert(station)
    station = stations["积水潭"]
    station.set_line(line)
    line.insert(station)
    station = stations["西直门"]
    station.set_line(line)
    line.insert(station)
    station = stations["车公庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["阜成门"]
    station.set_line(line)
    line.insert(station)
    station = stations["复兴门"]
    station.set_line(line)
    line.insert(station)
    station = stations["长椿街"]
    station.set_line(line)
    line.insert(station)

    return line

def line5_init(stations):
    line = Line(5, "5号", False)
    station = stations["宋家庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["刘家窑"]
    station.set_line(line)
    line.insert(station)
    station = stations["蒲黄榆"]
    station.set_line(line)
    line.insert(station)
    station = stations["天坛东门"]
    station.set_line(line)
    line.insert(station)
    station = stations["磁器口"]
    station.set_line(line)
    line.insert(station)
    station = stations["崇文门"]
    station.set_line(line)
    line.insert(station)
    station = stations["东单"]
    station.set_line(line)
    line.insert(station)
    station = stations["灯市口"]
    station.set_line(line)
    line.insert(station)
    station = stations["东四"]
    station.set_line(line)
    line.insert(station)
    station = stations["张自忠路"]
    station.set_line(line)
    line.insert(station)
    station = stations["北新桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["雍和宫"]
    station.set_line(line)
    line.insert(station)
    station = stations["和平里北街"]
    station.set_line(line)
    line.insert(station)
    station = stations["和平西桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["惠新西街南口"]
    station.set_line(line)
    line.insert(station)
    station = stations["惠新西街北口"]
    station.set_line(line)
    line.insert(station)
    station = stations["大屯路东"]
    station.set_line(line)
    line.insert(station)
    station = stations["北苑路北"]
    station.set_line(line)
    line.insert(station)
    station = stations["立水桥南"]
    station.set_line(line)
    line.insert(station)
    station = stations["立水桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["天通苑南"]
    station.set_line(line)
    line.insert(station)
    station = stations["天通苑"]
    station.set_line(line)
    line.insert(station)
    station = stations["天通苑北"]
    station.set_line(line)
    line.insert(station)

    return line

def line6_init(stations):
    line = Line(6, "6号", False)
    station = stations["海淀五路居"]
    station.set_line(line)
    line.insert(station)
    station = stations["慈寿寺"]
    station.set_line(line)
    line.insert(station)
    station = stations["花园桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["白石桥南"]
    station.set_line(line)
    line.insert(station)
    station = stations["车公庄西"]
    station.set_line(line)
    line.insert(station)
    station = stations["车公庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["平安里"]
    station.set_line(line)
    line.insert(station)
    station = stations["北海北"]
    station.set_line(line)
    line.insert(station)
    station = stations["南锣鼓巷"]
    station.set_line(line)
    line.insert(station)
    station = stations["东四"]
    station.set_line(line)
    line.insert(station)
    station = stations["朝阳门"]
    station.set_line(line)
    line.insert(station)
    station = stations["东大桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["呼家楼"]
    station.set_line(line)
    line.insert(station)
    station = stations["金台路"]
    station.set_line(line)
    line.insert(station)
    station = stations["十里堡"]
    station.set_line(line)
    line.insert(station)
    station = stations["青年路"]
    station.set_line(line)
    line.insert(station)
    station = stations["褡裢坡"]
    station.set_line(line)
    line.insert(station)
    station = stations["黄渠"]
    station.set_line(line)
    line.insert(station)
    station = stations["常营"]
    station.set_line(line)
    line.insert(station)
    station = stations["草房"]
    station.set_line(line)
    line.insert(station)
    station = stations["物资学院路"]
    station.set_line(line)
    line.insert(station)
    station = stations["通州北关"]
    station.set_line(line)
    line.insert(station)
    station = stations["通运门"]
    station.set_line(line)
    line.insert(station)
    station = stations["北运河西"]
    station.set_line(line)
    line.insert(station)
    station = stations["北运河东"]
    station.set_line(line)
    line.insert(station)
    station = stations["郝家府"]
    station.set_line(line)
    line.insert(station)
    station = stations["东夏园"]
    station.set_line(line)
    line.insert(station)
    station = stations["潞城"]
    station.set_line(line)
    line.insert(station)

    return line

def line7_init(stations):
    line = Line(7, "7号", False)
    station = stations["北京西站"]
    station.set_line(line)
    line.insert(station)
    station = stations["湾子"]
    station.set_line(line)
    line.insert(station)
    station = stations["达官营"]
    station.set_line(line)
    line.insert(station)
    station = stations["广安门内"]
    station.set_line(line)
    line.insert(station)
    station = stations["菜市口"]
    station.set_line(line)
    line.insert(station)
    station = stations["虎坊桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["珠市口"]
    station.set_line(line)
    line.insert(station)
    station = stations["桥湾"]
    station.set_line(line)
    line.insert(station)
    station = stations["磁器口"]
    station.set_line(line)
    line.insert(station)
    station = stations["广渠门内"]
    station.set_line(line)
    line.insert(station)
    station = stations["广渠门外"]
    station.set_line(line)
    line.insert(station)
    station = stations["双井"]
    station.set_line(line)
    line.insert(station)
    station = stations["九龙山"]
    station.set_line(line)
    line.insert(station)
    station = stations["大郊亭"]
    station.set_line(line)
    line.insert(station)
    station = stations["百子湾"]
    station.set_line(line)
    line.insert(station)
    station = stations["化工"]
    station.set_line(line)
    line.insert(station)
    station = stations["南楼梓庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["欢乐谷景区"]
    station.set_line(line)
    line.insert(station)
    station = stations["垡头"]
    station.set_line(line)
    line.insert(station)
    station = stations["双合"]
    station.set_line(line)
    line.insert(station)
    station = stations["焦化厂"]
    station.set_line(line)
    line.insert(station)

    return line

def line8_init(stations):
    line = Line(8, "8号", False)
    station = stations["朱辛庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["育知路"]
    station.set_line(line)
    line.insert(station)
    station = stations["平西府"]
    station.set_line(line)
    line.insert(station)
    station = stations["回龙观东大街"]
    station.set_line(line)
    line.insert(station)
    station = stations["霍营"]
    station.set_line(line)
    line.insert(station)
    station = stations["育新"]
    station.set_line(line)
    line.insert(station)
    station = stations["西小口"]
    station.set_line(line)
    line.insert(station)
    station = stations["永泰庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["林萃桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["森林公园南门"]
    station.set_line(line)
    line.insert(station)
    station = stations["奥林匹克公园"]
    station.set_line(line)
    line.insert(station)
    station = stations["奥体中心"]
    station.set_line(line)
    line.insert(station)
    station = stations["北土城"]
    station.set_line(line)
    line.insert(station)
    station = stations["安华桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["安德里北街"]
    station.set_line(line)
    line.insert(station)
    station = stations["鼓楼大街"]
    station.set_line(line)
    line.insert(station)
    station = stations["什刹海"]
    station.set_line(line)
    line.insert(station)
    station = stations["南锣鼓巷"]
    station.set_line(line)
    line.insert(station)

    return line

def line9_init(stations):
    line = Line(9, "9号", False)
    station = stations["国家图书馆"]
    station.set_line(line)
    line.insert(station)
    station = stations["白石桥南"]
    station.set_line(line)
    line.insert(station)
    station = stations["白堆子"]
    station.set_line(line)
    line.insert(station)
    station = stations["军事博物馆"]
    station.set_line(line)
    line.insert(station)
    station = stations["北京西站"]
    station.set_line(line)
    line.insert(station)
    station = stations["六里桥东"]
    station.set_line(line)
    line.insert(station)
    station = stations["六里桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["七里庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["丰台东大街"]
    station.set_line(line)
    line.insert(station)
    station = stations["丰台南路"]
    station.set_line(line)
    line.insert(station)
    station = stations["科怡路"]
    station.set_line(line)
    line.insert(station)
    station = stations["丰台科技园"]
    station.set_line(line)
    line.insert(station)
    station = stations["郭公庄"]
    station.set_line(line)
    line.insert(station)

    return line

def line13_init(stations):
    line = Line(13, "13号", False)
    station = stations["西直门"]
    station.set_line(line)
    line.insert(station)
    station = stations["大钟寺"]
    station.set_line(line)
    line.insert(station)
    station = stations["知春路"]
    station.set_line(line)
    line.insert(station)
    station = stations["五道口"]
    station.set_line(line)
    line.insert(station)
    station = stations["上地"]
    station.set_line(line)
    line.insert(station)
    station = stations["西二旗"]
    station.set_line(line)
    line.insert(station)
    station = stations["龙泽"]
    station.set_line(line)
    line.insert(station)
    station = stations["回龙观"]
    station.set_line(line)
    line.insert(station)
    station = stations["霍营"]
    station.set_line(line)
    line.insert(station)
    station = stations["立水桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["北苑"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京西"]
    station.set_line(line)
    line.insert(station)
    station = stations["芍药居"]
    station.set_line(line)
    line.insert(station)
    station = stations["柳芳"]
    station.set_line(line)
    line.insert(station)
    station = stations["东直门"]
    station.set_line(line)
    line.insert(station)

    return line

def line14_init(stations):
    line = Line(14, "14号", False)
    station = stations["张郭庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["园博园"]
    station.set_line(line)
    line.insert(station)
    station = stations["郭庄子"]
    station.set_line(line)
    line.insert(station)
    station = stations["大井"]
    station.set_line(line)
    line.insert(station)
    station = stations["七里庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["西局"]
    station.set_line(line)
    line.insert(station)
    station = stations["北京南站"]
    station.set_line(line)
    line.insert(station)
    station = stations["陶然桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["永定门外"]
    station.set_line(line)
    line.insert(station)
    station = stations["景泰"]
    station.set_line(line)
    line.insert(station)
    station = stations["蒲黄榆"]
    station.set_line(line)
    line.insert(station)
    station = stations["方庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["十里河"]
    station.set_line(line)
    line.insert(station)
    station = stations["北工大西门"]
    station.set_line(line)
    line.insert(station)
    station = stations["平乐园"]
    station.set_line(line)
    line.insert(station)
    station = stations["九龙山"]
    station.set_line(line)
    line.insert(station)
    station = stations["大望路"]
    station.set_line(line)
    line.insert(station)
    station = stations["金台路"]
    station.set_line(line)
    line.insert(station)
    station = stations["朝阳公园"]
    station.set_line(line)
    line.insert(station)
    station = stations["枣营"]
    station.set_line(line)
    line.insert(station)
    station = stations["东风北桥"]
    station.set_line(line)
    line.insert(station)
    station = stations["将台"]
    station.set_line(line)
    line.insert(station)
    station = stations["高家园"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京南"]
    station.set_line(line)
    line.insert(station)
    station = stations["阜通"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京"]
    station.set_line(line)
    line.insert(station)
    station = stations["东湖渠"]
    station.set_line(line)
    line.insert(station)
    station = stations["来广营"]
    station.set_line(line)
    line.insert(station)
    station = stations["善各庄"]
    station.set_line(line)
    line.insert(station)

    return line

def line15_init(stations):
    line = Line(15, "15号", False)
    station = stations["清华东路西口"]
    station.set_line(line)
    line.insert(station)
    station = stations["六道口"]
    station.set_line(line)
    line.insert(station)
    station = stations["北沙滩"]
    station.set_line(line)
    line.insert(station)
    station = stations["奥林匹克公园"]
    station.set_line(line)
    line.insert(station)
    station = stations["安立路"]
    station.set_line(line)
    line.insert(station)
    station = stations["大屯路东"]
    station.set_line(line)
    line.insert(station)
    station = stations["关庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京西"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京"]
    station.set_line(line)
    line.insert(station)
    station = stations["望京东"]
    station.set_line(line)
    line.insert(station)
    station = stations["崔各庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["马泉营"]
    station.set_line(line)
    line.insert(station)
    station = stations["孙河"]
    station.set_line(line)
    line.insert(station)
    station = stations["国展"]
    station.set_line(line)
    line.insert(station)
    station = stations["花梨坎"]
    station.set_line(line)
    line.insert(station)
    station = stations["后沙峪"]
    station.set_line(line)
    line.insert(station)
    station = stations["南法信"]
    station.set_line(line)
    line.insert(station)
    station = stations["石门"]
    station.set_line(line)
    line.insert(station)
    station = stations["顺义"]
    station.set_line(line)
    line.insert(station)
    station = stations["俸伯"]
    station.set_line(line)
    line.insert(station)

    return line

# fangshan line
def line101_init(stations):
    line = Line(14, "房山", False)
    station = stations["苏庄"]
    station.set_line(line)
    line.insert(station)
    station = stations["良乡南关"]
    station.set_line(line)
    line.insert(station)
    station = stations["良乡大学城西"]
    station.set_line(line)
    line.insert(station)
    station = stations["良乡大学城"]
    station.set_line(line)
    line.insert(station)
    station = stations["良乡大学城北"]
    station.set_line(line)
    line.insert(station)
    station = stations["广阳城"]
    station.set_line(line)
    line.insert(station)
    station = stations["篱笆房"]
    station.set_line(line)
    line.insert(station)
    station = stations["长阳"]
    station.set_line(line)
    line.insert(station)
    station = stations["稻田"]
    station.set_line(line)
    line.insert(station)
    station = stations["大葆台"]
    station.set_line(line)
    line.insert(station)
    station = stations["郭公庄"]
    station.set_line(line)
    line.insert(station)

    return line

# Subway lines initialization
def lines_init(stations):
    lines = {}
    lines.update({4:line4_init(stations)})
    lines.update({10:line10_init(stations)})
    lines.update({1:line1_init(stations)})
    lines.update({2:line2_init(stations)})
    lines.update({5:line5_init(stations)})
    lines.update({6:line6_init(stations)})
    lines.update({7:line7_init(stations)})
    lines.update({8:line8_init(stations)})
    lines.update({9:line9_init(stations)})
    lines.update({13: line13_init(stations)})
    lines.update({14: line14_init(stations)})
    lines.update({15: line15_init(stations)})
    lines.update({101: line101_init(stations)})
    return lines

def get_station_by_name(name, stations):
    try:
        return stations[name]
    except KeyError:
        return None

def get_line_by_number(number, lines):
    return lines[number]

def get_line_overlap(stop1, stop2):
    for i in stop1.lines:
        if i in stop2.lines:
            yield i

def has_line_overlap(stop1, stop2):
    for i in stop1.lines:
        if i in stop2.lines:
            return True

    return False

def get_shortest_line(stop1, stop2):
    min = 0xFFFFFFFF
    target = None

    if has_line_overlap(stop1, stop2) == False:
        return target

    for line in get_line_overlap(stop1, stop2):
        distance = line.distance(stop1, stop2)
        if distance < min:
            target = line
            min = distance
    return target

# Find the shortest distance between two stations which might have line overlap
def compute_same_line(start, end):
    target = get_shortest_line(start, end)

    if target is not None:
        return target.distance(start, end)
    else:
        return 0

def shortest(temp, result):
    t_cnt = temp.compute_stops()
    r_cnt = result.compute_stops()
    if t_cnt < r_cnt:
        result.route = list(temp.route)
        return 1
    elif t_cnt == r_cnt:
        return 0
    else:
        return -1

def less_transfer(temp, result):
    if result.is_empty():
        result.route = list(temp.route)
        return

    if temp.transer_times() < result.transer_times():
        result.route = list(temp.route)
        return 1
    elif temp.transer_times() == result.transer_times():
        return 0
    else:
        return -1

def choose_route(temp, result, rule):
    if rule == "short":
        if shortest(temp, result) == 0:
            less_transfer(temp, result)
    elif rule == "less":
        if less_transfer(temp, result) == 0:
            shortest(temp, result)
    return

def clear_passed_all(temp):
    for i in stations:
        if stations[i] not in temp.route:
            stations[i].clear_passed()

# Core logic to find the shortest route between any two stations
def compute(start, end, lfrom, level, temp, result, rule):

    temp.push(start)
    if has_line_overlap(start,end):
        temp.push(end)
        #print temp.compute_stops(), temp.transer_times()
        choose_route(temp, result, rule)
        temp.pop()
        return

    if start.get_refcnt() > 1:
        return

    lines = [l for l in start.lines if l != lfrom]
    for line in lines:
        target = [stop for stop in line.transfer_stations() if stop.is_passed() == False]
        for stop in target:
            compute(stop, end, line, level+1, temp, result, rule)
            temp.pop()
            # Give chance to other level1 stop
            if level < 3:
                clear_passed_all(temp)

    return

def transfer_stop_list(slist, direction):
    list = []
    for stop in slist:
        for line in stop.lines:
            for t in line.transfer_stations():
                if t in slist:
                    continue

                if direction == 's' and t.sfrom is None:
                    t.set_sfrom(stop)
                elif direction == 'e' and t.efrom is None:
                    t.set_efrom(stop)

                list.append(t)
    slist.extend(list)
    return

def get_total_distance(stop):

    len = 0
    x = stop.sfrom
    y = stop
    while x is not None:
        len += compute_same_line(x, y)
        y = x
        x = x.sfrom

    x = stop.efrom
    y = stop
    while x is not None:
        len += compute_same_line(x, y)
        y = x
        x = x.efrom

    return len

def process_result(stop, result):

     x = stop.sfrom
     while x is not None:
         result.route.insert(0, x)
         x = x.sfrom

     result.route.append(stop)

     x = stop.efrom
     while x is not None:
         result.route.append(x)
         x = x.efrom

     return

def get_total_transfers(stop):
    cnt = 1
    x = stop.sfrom
    while x is not None:
        x = x.sfrom
        cnt += 1

    x = stop.efrom
    while x is not None:
        x = x.efrom
        cnt += 1

    return cnt

def choose_route2(target, candidate, rule):
    d1 = get_total_distance(candidate)
    t1 = get_total_transfers(candidate)
    d2 = get_total_distance(target)
    t2 = get_total_transfers(target)

    if rule == 'short':
        if d1 < d2:
            return candidate
        elif d1 > d2:
            return target
        else:
            if t1 < t2:
                return candidate
            else:
                return target
    elif rule == 'less':
        if t1 < t2:
            return candidate
        elif t1 > t2:
            return target
        else:
            if d1 < d2:
                return candidate
            else:
                return target
    else:
        return target


def compute2(start, end, result, rule):
    slist = [start]
    elist = [end]

    target = None

    while target is None:
        for stop in slist:
            if stop in elist:
                if target is None:
                    target = stop
                else:
                    #compare distance
                    target = choose_route2(target, stop, rule)
        # Find the best middle stop
        if target is not None:
            break

        #add stops to slist
        transfer_stop_list(slist,'s')
        transfer_stop_list(elist,'e')

    if target is not None:
        process_result(target, result)

    return

if __name__ == "__main__":
    stations = stations_init()
    lines    = lines_init(stations)

    result  = Route()
    temp    = Route()
    start   = get_station_by_name("达官营", stations)
    end     = get_station_by_name("奥体中心", stations)

    if start is not None and end is not None:
        compute(start, end, None, 0, temp, result, "short")
        result.show()
    print(result.output())

    result2  = Route()
    if start is not None and end is not None:
        compute2(start, end, result2, "less")
    print(result2.output())


