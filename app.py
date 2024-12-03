from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import database as db

app = Flask(__name__, static_folder='static')

# 配置OpenAI客户端
client = OpenAI(
    api_key="sk-5aR4NN53msPzKfSF1995F0D3673841F3A3Bf4131110375Bd",
    base_url="https://az.gptplus5.com/v1"  # 请替换为实际的base URL
)

# 用于跟踪总使用量
total_tokens = 0
total_cost = 0

# 初始化数据库
db.init_db()

@app.route('/')
def home():
    tags = db.get_all_tags()
    return render_template('chat.html', tags=tags)

@app.route('/create_tag', methods=['POST'])
def create_tag():
    name = request.json.get('name', f'对话 {len(db.get_all_tags()) + 1}')
    tag_id = db.create_tag(name)
    return jsonify({"tag_id": tag_id, "name": name})

@app.route('/get_history/<int:tag_id>')
def get_history(tag_id):
    history = db.get_conversation_history(tag_id)
    return jsonify({"history": history})

@app.route('/chat', methods=['POST'])
def chat():
    global total_tokens, total_cost
    try:
        message = request.json.get('message', '')
        tag_id = request.json.get('tag_id')
        
        # 获取历史记录
        conversation_history = db.get_conversation_history(tag_id)
        
        # 添加新的用户消息
        conversation_history.append({"role": "user", "content": message})
        db.add_message(tag_id, "user", message)
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
        )
        
        # 保存助手回复
        assistant_message = response.choices[0].message.content
        db.add_message(tag_id, "assistant", assistant_message)
        
        # 计算token使用情况
        tokens_used = response.usage.total_tokens
        total_tokens += tokens_used
        cost = (tokens_used / 1000) * 0.03
        total_cost += cost
        
        return jsonify({
            "reply": assistant_message,
            "tokens_used": tokens_used,
            "total_tokens": total_tokens,
            "cost": f"${cost:.4f}",
            "total_cost": f"${total_cost:.4f}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_tag/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    db.delete_tag(tag_id)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True) 