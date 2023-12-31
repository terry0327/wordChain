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
    groupNode = group_name + group_id

    # 提取命令和内容
    command, content = parse_command(message)

    # 根據命令執行相應的操作(!接龍、!刪除、!查看、!編輯)
    if command == '!接龍':
        # 获取当前Group节点的数据
        group_data = ref.child('Group').child(groupNode).get()
        
        # 检查group_data是否存在，如果不存在则创建一个新的字典
        if not group_data:
            group_data = {}

        # 获取当前Group节点下的所有消息数量
        message_count = len(group_data)

        # 构建新消息的键，使用字符串表示数字索引
        #new_message_key = str(message_count + 1)

        # 构建新消息的数据
        # new_message_data = {
        #     'groupName': group_name,
        #     'messages': content,
        #     'userId': user_id,
        #     'userName': user_name
        # }
        new_message_data = {
            'userName': user_name,
            'messages': content
        }

        # 更新数据，将新消息添加到Group节点中
        group_data[user_id] = new_message_data
        ref.child('Group').child(groupNode).set(group_data)
       
        # PUT操作示例：更新数据
        # ref.child('Group').child(group_id).update({
        #     'groupName': group_name,
        #     'userId': user_id,
        #     'userName': user_name,
        #     'messages': content
        # })
        response = query(groupNode)
    elif command == '!刪除':
        delete(groupNode)
        response = '已清除資料'
    elif command == '!查看':
        response = query(groupNode)
    elif command == '!編輯':
        edit(groupNode, user_id, content)
        response = query(groupNode)
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

# TODO
# 如果翔測試後能以userId獨立分開data
# 那就只需要調整query就好，現在是找多一個0的那層
def query(groupNode):
    report = '現在開始回報業績。\n'
    group_data_list = ref.child('Group').child(groupNode).get()
    if group_data_list is not None:
        print("group_data_list：" + str(group_data_list))
        for user_id, user_data in group_data_list.items():
           print("\nuser_id" + str(user_id) + "\nuser_data：" + str(user_data))
        #   user_id, user_data = list(user_data.items())[0]
           if isinstance(user_data, dict) and 'messages' in user_data:
                print(str(user_data["messages"]))
                report += "\n" + user_data["messages"]
    else:
        report = "資料庫中並無資料，請先使用指令 !接龍 新增資料"

    return report

def delete(groupNode):
    ref.child('Group').child(groupNode).delete()

# TODO：節點錯誤，他直接新增一個ID
# {
#   "Group": {
#     "接龍機器人開發C23da4fac70cbc6d9d8ff1d1b72900f47": {
#       "0": {
#         "U15e565fdb17db333bf2ccadc4f88db27": {
#           "messages": "1成交一間房子",
#           "userName": "林希哲"
#         }
#       },
#       "U15e565fdb17db333bf2ccadc4f88db27": {
#         "messages": "44444"
#       }
#     }
#   }
# }
def edit(groupNode, user_id, message):
    # user_data = ref.child('Group').child(groupNode).child(user_id).get()
    ref.child('Group').child(groupNode).child(user_id).update({
        'messages':message
    })

if __name__ == '__main__':
    app.run()