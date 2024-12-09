import ijson
import re
from datetime import datetime
from bs4 import BeautifulSoup
import json
import requests
import pandas as pd
import ijson
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import pandas as pd


def get_path_after_org(url):
    org_index = url.find('org')
    if org_index != -1:
        path_after_org = url[org_index + 3:]
        return path_after_org
    else:
        return ""

def get_players_data(htm_l):
    soup = BeautifulSoup(htm_l, 'html.parser')

    # 查找所有表格行（<tr>元素）
    rows = soup.find_all('tr')

    # 遍历每行，并提取选手信息
    players_info = []
    playerlst = set()
    for row in rows:
        try:
            # 提取玩家姓名（这里简化了，只取smartphone-only的div作为示例）
            player_name_div = row.find('div', class_='smartphone-only statsPlayerName')
            player_name = player_name_div.get_text(strip=True) if player_name_div else 'Unknown'

            # 提取KD比率
            kd_td = row.find('td', class_='kd')
            kd = kd_td.get_text(strip=True) if kd_td else 'N/A'  # 如果没找到，则设置为'N/A'

            # 提取加减分（胜负差）
            plus_minus_td = row.find('td', class_='plus-minus')
            plus_minus = (plus_minus_td.find('span').get_text(strip=True) if plus_minus_td and plus_minus_td.find('span')
                        else '0')  # 如果没找到span，则默认为'0'；如果没找到td，则此代码不会执行到get_text
            plus_minus = (plus_minus_td.find('span').get_text(strip=True) if plus_minus_td and plus_minus_td.find('span') else '0')
            # 提取ADR
            adr = row.find('td', class_='adr').get_text(strip=True) if row.find('td', class_='adr') else 'N/A'

            # 提取KAST
            kast = row.find('td', class_='kast').get_text(strip=True) if row.find('td', class_='kast') else 'N/A'

            # 提取评分
            rating = row.find('td', class_='rating').get_text(strip=True) if row.find('td', class_='rating') else 'N/A'
            
            # 将选手信息添加到列表中
            if player_name != 'Unknown' and player_name not in playerlst:
                playerlst.add(player_name)
                players_info.append(f"The kd,adr,kast and rating of player {player_name} are {kd},{adr},{kast} and {rating} respectively. ")
        except Exception as e:
            # 如果在处理某一行时发生任何异常，打印错误消息并继续处理下一行
            pass
    res_txt = ""
    for i in players_info:
        res_txt+=i
    return res_txt

def players_info(html_content):
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    player_tds = soup.find_all('td', class_='player')
 
    # 遍历每个<td>元素，并尝试提取玩家名称、团队序号和href
    players_info = []
    for player_td in player_tds:
        player_link = player_td.find('a')
        if player_link is not None:
            player_div = player_link.find('div', class_='flagAlign')
            if player_div is not None:
                player_name_div = player_div.find('div', class_='text-ellipsis')
                if player_name_div is not None:
                    # 提取玩家名称
                    player_name = player_name_div.get_text(strip=True)
                    
                    # 提取团队序号
                    team_ordinal = player_div.get('data-team-ordinal')
                    
                    # 提取href
                    player_href = player_link.get('href')
                    
                    # 将玩家信息添加到列表中
                    players_info.append({
                        'name': player_name,
                        'team_ordinal': team_ordinal,
                        'href': player_href
                    })
                else:
                    # 处理没有找到玩家名称的情况
                    pass
            else:
                # 处理没有找到flagAlign div的情况
                pass
        else:
            pass
    return players_info


def get_html(htm_l):
    res = {}
    soup = BeautifulSoup(htm_l, 'html.parser')
    teams = soup.find_all('div', class_=['team1-gradient', 'team2-gradient'])
    team_win =[]
    for team in teams:
        team_name = team.find('div', class_='teamName').get_text(strip=True)
        result = team.find('div', class_=['won', 'lost']).get_text(strip=True)
        team_win.append([team_name,result])
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    json_string = script_tag.text.strip()
    json_data = json.loads(json_string)
    time_and_event_element = soup.find('div', class_='timeAndEvent')
 
    # 查找时间元素并提取时间文本
    time_element = time_and_event_element.find('div', class_='time')
    time_text = time_element.get_text(strip=True)
    time_obj = datetime.strptime(time_text, '%H:%M')  # 解析时间
    
    # 查找日期元素并提取日期文本
    date_element = time_and_event_element.find('div', class_='date')
    date_text = date_element.get_text(strip=True)
    month_name_to_number = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    # 使用正则表达式提取日期和月份
    match = re.match(r'(\d+)(st|nd|rd|th) of (\w+) (\d+)', date_text)
    if match:
        day = int(match.group(1))  # 日
        # 忽略后缀(st, nd, rd, th)
        month_name = match.group(3)  # 月
        year = int(match.group(4))  # 年
        month = month_name_to_number[month_name]  # 将月份名称转换为数字
    
        # 创建datetime对象（注意：这里假设时间是当天的本地时间，可能需要根据实际情况调整时区）
        # 由于我们没有时区信息，且HTML中的时间已经是24小时制，我们直接使用时间部分
        # 如果HTML中的时间是UTC或其他时区，您可能需要相应地调整
        full_datetime_obj = datetime(year, month, day, time_obj.hour, time_obj.minute, time_obj.second)
    
        # 打印完整的datetime对象
        res['time'] = full_datetime_obj
    # 提取比赛信息
    match_info_div = soup.find('div', class_='padding preformatted-text')
    if match_info_div:
        match_info = match_info_div.get_text(strip=True, separator=' ').replace('\n', ' ')
        res['Match Info'] = match_info
    
    # 提取picked后的文本
    picked_texts = []
    veto_box = soup.find('div', class_='standard-box veto-box').find_next_sibling('div', class_='standard-box veto-box')
    if veto_box:
        padding_div = veto_box.find('div', class_='padding')
        if padding_div:
            for child_div in padding_div.find_all('div'):
                if "picked" in child_div.get_text(strip=True):
                    picked_texts.append(child_div.get_text(strip=True).split("picked")[-1].strip())
                if "was left over" in child_div.get_text(strip=True):
                    picked_texts.append(child_div.get_text(strip=True).split("was left over")[0].strip().split(' ')[-1].strip())
    
    res['Picked Maps'] = picked_texts
    res['Match_name'] = json_data['name']
    res['Team1_name'] = json_data['competitor'][0]['name']
    res['Team1_name_url'] = get_path_after_org(json_data['competitor'][0]['url'])
    res['Team2_name'] = json_data['competitor'][1]['name']
    res['Team2_name_url'] = get_path_after_org(json_data['competitor'][1]['url'])
    playerinfo = players_info(htm_l)
    namelst = []
    namelst1 = []
    res_txt=''
    for i in playerinfo:
        namelst1.append(i['name'])
        if int(i['team_ordinal'])==1:
            namelst.append(f"{i['name']} is a member of Team {res['Team1_name']}. ")
        else:
            namelst.append(f"{i['name']} is a member of Team {res['Team2_name']}. ")              
    for i in namelst:
        res_txt+=str(i)
    namelst1.append(res['Team1_name'])
    namelst1.append(res['Team2_name'])
    mapstr=""
    for k in res['Picked Maps']:
        mapstr+=str(k)
        mapstr+=","
    res['map_txt']=mapstr
    str2 = f"The match was a {res['Match Info']} series that took place in {res['time']}.The match consisted of {len(res['Picked Maps'])} maps, {res['map_txt']} and the name of the match was {res['Match_name']} and the competing teams were {res['Team1_name']} and {res['Team2_name']}."
    resstr = str2+res_txt
    matchtime = res['time']
    
    if team_win[0][1]>team_win[1][1]:
        winlosestr=f"Team {team_win[0][0]} won! "
        loselosestr=f"Team {team_win[1][0]} lost. "
        matchwinner = team_win[0][0]
        matchloser = team_win[1][0]
    else:
        winlosestr=f"Team {team_win[1][0]} won! "
        loselosestr=f"Team {team_win[0][0]} lost. "
        matchwinner = team_win[1][0]
        matchloser = team_win[0][0]
    resstr=loselosestr+resstr
    resstr=winlosestr+resstr
    return [resstr,namelst1,matchtime.timestamp(),[matchwinner,matchloser]]




def get_match_comment(htm_l):

    soup = BeautifulSoup(htm_l, 'html.parser')
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    json_string = script_tag.text.strip()
    json_data = json.loads(json_string)
    urllst = [get_path_after_org(json_data['competitor'][0]['url']).split('/')[-1],get_path_after_org(json_data['competitor'][1]['url']).split('/')[-1]]
    # 查找所有的帖子容器
    post_containers = soup.find_all('div', class_='post', id=True)
    
    # 创建一个列表来存储帖子信息
    posts = []
    for post_container in post_containers:
        post_content_div = post_container.find('div', class_='forum-middle')
        post_content = post_content_div.get_text(strip=True) if post_content_div else '内容缺失'
        time_span = post_container.find('span', class_='time')
        time_text = time_span.get('data-unix') if time_span else None
        time_obj = datetime.fromtimestamp(int(time_text) / 1000) if time_text else None
        if not time_obj:
            time_obj = None  
        posts.append({
            'content': post_content,
            'time': time_obj,
            'url':urllst
        })
    valid_posts = [post for post in posts if post['time'] is not None]
    sorted_posts = sorted(valid_posts, key=lambda x: x['time'])
    return sorted_posts
def get_eval_match(inp):
    res_str = get_html(inp)[0]+get_players_data(inp)
    return pd.DataFrame([{'time':get_html(inp)[2],'content':res_str,'url':get_html(inp)[1],'team':get_html(inp)[3]}])




n1=0
dt_object1 = datetime(2000, 1, 1, 1, 0, 0).timestamp()
df_match = pd.DataFrame([{'time':dt_object1,'content':'hi','url':[],'team':'hi'}])
with open('D:/HuaweiMoveData/Users/Flam1ngo/Desktop/小黑盒/csgo比赛预测/match_data.json', 'r', encoding='utf-8') as f:
    parser = ijson.parse(f)
    for prefix, event, value in parser:
        if prefix=="RECORDS.item.html":
            b=f"Prefix: {prefix}, Event: {event},Val:{value}"
            get_html(b)
            pause_df1 = get_eval_match(b)
            df_match = pd.concat([pause_df1, df_match], axis=0, ignore_index=True)
        n1+=1
        print(n1)


df_match_clean = df_match.iloc[:-1]
df_match_clean.to_json('output.json', orient='records', lines=True)




def read_zhengwen(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    date_div = soup.find('div', class_='date')

    if date_div:
        unix_timestamp = int(date_div['data-unix']) / 1000  # 将毫秒转换为秒
        datetime_obj = datetime.fromtimestamp(unix_timestamp)
    res = []
    # 查找所有具有特定类名的<p>标签
    paragraphs = soup.find_all('p', class_='news-block')
    # 遍历每个段落并提取信息
    for paragraph_index, paragraph in enumerate(paragraphs):
        cont = paragraph.get_text()
        # 查找段落中的所有超链接并提取URL
        links = paragraph.find_all('a')
        urllst = []
        for link_index, link in enumerate(links):
            link_url = link['href'].split('/')[-1]
            urllst.append(link_url)
        if urllst != []:
            res.append({'time' : datetime_obj.timestamp(),'content' :cont,'url' : urllst})
    
    return pd.DataFrame(res)


def read_pinglun(htm):
    soup = BeautifulSoup(htm, 'html.parser')
    
    # 初始化一个空列表来存储评论
    comments = []
    
    # 查找所有具有forum-middle类的div元素（评论内容）
    # 和它们紧接着的forum-bottombar类中的time元素（评论时间）
    # 注意：这里假设每个forum-middle后面紧跟着一个forum-bottombar
    for forum_middle in soup.find_all('div', class_='forum-middle'):
        # 提取评论内容
        content = forum_middle.get_text(strip=True)
        
        # 查找紧接着的forum-bottombar中的time元素
        # 这里使用find_next_sibling来定位紧接着的同级元素
        forum_bottombar = forum_middle.find_next_sibling('div', class_='forum-bottombar')
        if forum_bottombar:
            time_span = forum_bottombar.find('span', class_='time')
            if time_span:
                # 提取时间字符串
                time_text = time_span.get_text(strip=True)
                
                # 提取UNIX时间戳并转换为datetime对象
                unix_timestamp = int(time_span['data-unix']) / 1000  # 毫秒转秒
                dt_object = datetime.fromtimestamp(unix_timestamp)
                # 注意：这里我们假设时间戳是UTC时间，并根据需要进行了时区转换。
                # 如果原始时间是其他时区，您可能需要进行相应的时区调整。
                
                # 将评论内容和时间添加到字典中
                comment_dict = {'time': dt_object, 'content': content}
                
                # 将字典添加到评论列表中
                comments.append(comment_dict)
    sorted_posts = sorted(comments, key=lambda x: x['time'])

    return sorted_posts

n=0
dt_object = datetime(2000, 1, 1, 1, 0, 0).timestamp()
df_news = pd.DataFrame([{'time':dt_object,'content':'hi','url':[]}])
with open('D:/HuaweiMoveData/Users/Flam1ngo/Desktop/小黑盒/csgo比赛预测/news.json', 'r', encoding='utf-8') as f:
    parser = ijson.parse(f)
    for prefix, event, value in parser:
        if prefix=="RECORDS.item.html":
            b=f"Prefix: {prefix}, Event: {event},Val:{value}"
            pause_df = read_zhengwen(b)
            df_news = pd.concat([pause_df, df_news], axis=0, ignore_index=True)
        n+=1
        print(n)

df_main = df_match_clean.copy(deep=True)
df_news_copy = df_news.copy(deep=True)
for index, row in df_main.iterrows():
    timeend = int(df_match_clean.iloc[index]['time'])
    timestart = int(df_match_clean.iloc[index]['time'])-3*2592000000
    urllst = df_match_clean.iloc[index]['url']
    winteam = df_match_clean.iloc[index]['team'][0]
    loseteam = df_match_clean.iloc[index]['team'][1]

    timeend1 = int(df_news_copy.iloc[index]['time'])
    timestart1 = int(df_news_copy.iloc[index]['time'])-3*2592000000
    urllst1 = df_news_copy.iloc[index]['url']

    df1 = df_match_clean[df_match_clean['time']>=timestart]
    df2 = df1[df1['time']<(timeend-100)]
    df_win = df2[df2['team'].apply(lambda x: winteam in x)]
    df_lose = df2[df2['team'].apply(lambda x: loseteam in x)]

    df5 = df_news_copy[df_news_copy['time']>=timestart]
    df6 = df5[df5['time']<(timeend-100)]
    df_win1 = df6[df6['url'].apply(lambda x: winteam in x)]
    df_lose1 = df6[df6['url'].apply(lambda x: loseteam in x)]
    try:
        winlst = df_win['content'].tolist()  # 尝试访问可能不存在的列
    except AttributeError:
        winlst = []
    try:
        loselst = df_lose['content'].tolist()  # 尝试访问可能不存在的列
    except AttributeError:
        loselst = []
    try:
        winlst1 = df_win1['content'].tolist()  # 尝试访问可能不存在的列
    except AttributeError:
        winlst1 = []
    try:
        loselst1 = df_lose1['content'].tolist()  # 尝试访问可能不存在的列
    except AttributeError:
        loselst1 = []


    reswin = ""
    reslose = ""
    for i in winlst:
        reswin +=str(i)
    for i in loselst:
        reslose +=str(i)
    for i in winlst1:
        reswin +=str(i)
    for i in loselst1:
        reslose +=str(i)
    resstr = reswin+reslose
    df_main.at[index, 'content'] = resstr






# def get_eval_match(inp):
#     res_str = get_html(inp)[0]+get_players_data(inp)
#     return pd.DataFrame([{'time':get_html(inp)[2],'content':res_str,'url':get_html(inp)[1],'team':get_html(inp)[3]}])


