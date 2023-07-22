import json
# Line Message Api
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# 初始化Firebase Admin SDK
cred = credentials.Certificate("./linebot-1eae2-firebase-adminsdk-rcme0-68fa3f8a88.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://linebot-1eae2-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# 获取数据库引用
ref = db.reference('/')

# 示例：从数据库读取数据
# data = ref.get()
# print(data)

app = Flask(__name__)
line_bot_api = LineBotApi('6pOxv7ybUtKoBOLmpQNH7KGsQphTg/HGVYeFA04V7bMnNJIwA7JDPtjNOLBoDCFlpq2Bh17EaBtsM+az7kjfP72X1bwiz0x+GdVdTm2Vo2Vgq4MaoY3IOcBB6jCKIugiBXXEDPjLrbR0fDksmDpkKgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f10df6fc344a062c11cb7fc69daaa912')

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    # GroupId, GroupName, userId, userName, Message  
    group_id = event.source.group_id
    group_name = line_bot_api.get_group_summary(group_id).group_name
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name

    # 提取命令和内容
    command, content = parse_command(message)

    # 根据命令执行相应的操作
    if command == '!接龍':
        # 获取当前Group节点的数据
        group_data = ref.child('Group').child(group_id).get()
        
        # 检查group_data是否存在，如果不存在则创建一个新的字典
        if not group_data:
            group_data = []

        # 获取当前Group节点下的所有消息数量
        message_count = len(group_data)

        # 构建新消息的键，使用字符串表示数字索引
        #new_message_key = str(message_count + 1)

        # 构建新消息的数据
        new_message_data = {
            'groupName': group_name,
            'messages': content,
            'userId': user_id,
            'userName': user_name
        }

        # 更新数据，将新消息添加到Group节点中
        group_data.append(new_message_data)
        ref.child('Group').child(group_id).set(group_data)
       
        # PUT操作示例：更新数据
        # ref.child('Group').child(group_id).update({
        #     'groupName': group_name,
        #     'userId': user_id,
        #     'userName': user_name,
        #     'messages': content
        # })
        response = story_continuation(group_id)

    # else:
    #     response = "不支持的命令"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

def parse_command(message):
    parts = message.split(' ', 1)
    command = parts[0]
    content = parts[1] if len(parts) > 1 else ''
    return command, content

def story_continuation(groupId):
    report = '現在開始回報業績。\n'
    group_data_list = ref.child('Group').child(groupId).get()

    if len(group_data_list):
        # for group_data in group_data_list:
        #     if 'messages' in group_data:
        # report += "\n" + group_data.get("messages")
        print("type(group_data_list)：" + type(group_data_list) + "\ngroup_data_list：" + group_data_list)
        report += "\n" + group_data_list
    else:
        report = "資料庫中並無此筆資料，請洽開發人員"
    # if message == "":
    #     story = '現在開始回報業績。\n'
    # else:
    #     story += '\n'
    # story += content

    return report

if __name__ == '__main__':
    app.run()