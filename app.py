from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text

    # 提取命令和内容
    command, content = parse_command(message)

    # 根据命令执行相应的操作
    if command == '!接龍':
        response = story_continuation(content)
    else:
        response = "不支持的命令"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

def parse_command(message):
    parts = message.split(' ', 1)
    command = parts[0]
    content = parts[1] if len(parts) > 1 else ''
    return command, content

def story_continuation(content):
    # 在这里根据内容进行故事接龙的逻辑处理
    # 您可以将新的内容添加到现有故事中
    # 并返回更新后的故事
    # 示例逻辑：
    story = '很久很久以前，有一只小猫。'
    return story + ' ' + content

if __name__ == '__main__':
    app.run()