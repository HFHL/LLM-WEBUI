from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import database as db
import yaml

app = Flask(__name__, static_folder='static')

# 读取配置文件
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# 初始化数据库
db.init_db()

@app.route('/')
def home():
    tags = db.get_all_tags()
    models = config.get('models', {})
    api_key = db.get_api_key()  # 新增：获取API key
    return render_template('chat.html', tags=tags, models=models, api_key=api_key)

@app.route('/update_api_key', methods=['POST'])
def update_api_key():
    api_key = request.json.get('api_key')
    db.update_api_key(api_key)  # 新增：更新API key
    return jsonify({"status": "success"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message', '')
        tag_id = request.json.get('tag_id')
        model_key = request.json.get('model', 'gpt4o')
        
        # 获取模型配置
        model_config = config['models'].get(model_key, config['models']['gpt4o'])
        
        # 打印模型信息
        print(f"\nSelected Model: {model_config['name']}")
        print(f"Base URL: {model_config['base_url']}\n")
        
        # 使用当前的API key
        api_key = db.get_api_key()
        
        # 配置OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=model_config['base_url']
        )
        
        # 获取历史记录
        conversation_history = db.get_conversation_history(tag_id)
        
        # 添加新的用户消息
        conversation_history.append({"role": "user", "content": message})
        db.add_message(tag_id, "user", message)
        
        # 调用OpenAI API
        response = client.chat.completions.create(
            model=model_key,
            messages=conversation_history
        )
        
        # 保存助手回复
        assistant_message = response.choices[0].message.content
        db.add_message(tag_id, "assistant", assistant_message)
        
        # 计算并更新该对话的token使用情况
        tokens_used = response.usage.total_tokens
        cost = (tokens_used / 1000) * 0.03
        db.update_tag_usage(tag_id, tokens_used, cost)  # 新增：更新特定对话的使用统计
        
        # 获取总使用量
        total_usage = db.get_total_usage()  # 新增：获取所有对话的总使用量
        
        return jsonify({
            "reply": assistant_message,
            "tokens_used": tokens_used,
            "cost": f"${cost:.4f}",
            "total_tokens": total_usage['tokens'],
            "total_cost": f"${total_usage['cost']:.4f}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_tag/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    db.delete_tag(tag_id)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True) 