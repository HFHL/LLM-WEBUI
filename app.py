from flask import Flask, render_template, request, jsonify, Response
from openai import OpenAI
import database as db
import yaml
import openai
import os
import datetime
import json

app = Flask(__name__, static_folder='static')
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        
        # 使用当前的API key
        api_key = db.get_api_key()
        
        # 配置OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=model_config['base_url']
        )
        
        # 获取历史记录（最近30条消息，即15轮对话）
        conversation_history = db.get_conversation_history(tag_id, limit=30)
        
        # 添加新的用户消息
        conversation_history.append({"role": "user", "content": message})
        db.add_message(tag_id, "user", message)

        def generate():
            collected_messages = []
            # 调用OpenAI API with stream=True
            response = client.chat.completions.create(
                model=model_key,
                messages=conversation_history,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_messages.append(content)
                    yield f"data: {content}\n\n"
            
            # 在流结束时保存完整的回复
            full_response = ''.join(collected_messages)
            db.add_message(tag_id, "assistant", full_response)
            
            # 更新使用统计
            tokens_used = len(full_response.split()) * 1.3  # 估算token数
            cost = (tokens_used / 1000) * 0.03
            db.update_tag_usage(tag_id, int(tokens_used), cost)
            
            # 获取总使用量
            total_usage = db.get_total_usage()
            
            # 发送最终的统计信息
            yield f"data: [DONE]\n\n"
            
            # 修复 f-string 语法
            stats = {
                'tokens_used': int(tokens_used),
                'cost': f'${cost:.4f}',
                'total_tokens': total_usage['tokens'],
                'total_cost': f'${total_usage["cost"]:.4f}'
            }
            yield f"data: {json.dumps(stats)}\n\n"

        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete_tag/<int:tag_id>', methods=['POST'])
def delete_tag(tag_id):
    db.delete_tag(tag_id)
    return jsonify({"status": "success"})

@app.route('/create_tag', methods=['POST'])
def create_tag():
    try:
        # 生成一个基于时间的对话名称
        name = datetime.datetime.now().strftime("对话 %Y-%m-%d %H:%M")
        
        # 创建新的对话标签
        tag_id = db.create_tag(name)
        
        return jsonify({
            "status": "success",
            "tag_id": tag_id,
            "name": name
        })
    except Exception as e:
        print(f"Error creating tag: {str(e)}")  # 添加日志
        return jsonify({"error": str(e)}), 500

@app.route('/get_history/<int:tag_id>')
def get_history(tag_id):
    try:
        # 获取对话历史
        history = db.get_conversation_history(tag_id)
        # 获取使用统计
        usage = db.get_tag_usage(tag_id)
        
        return jsonify({
            "history": history,
            "usage": usage
        })
    except Exception as e:
        print(f"Error getting history: {str(e)}")  # 添加日志
        return jsonify({"error": str(e)}), 500

@app.route('/chat/stream')
def chat_stream():
    try:
        message = request.args.get('message', '')
        tag_id = request.args.get('tag_id')
        model_key = request.args.get('model', 'gpt4o')
        
        # 获取模型配置
        model_config = config['models'].get(model_key, config['models']['gpt4o'])
        
        # 使用当前的API key
        api_key = db.get_api_key()
        
        # 配置OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=model_config['base_url']
        )
        
        # 获取历史记录（最近30条消息，即15轮对话）
        conversation_history = db.get_conversation_history(tag_id, limit=30)
        
        # 添加新的用户消息
        conversation_history.append({"role": "user", "content": message})
        db.add_message(tag_id, "user", message)

        def generate():
            collected_messages = []
            # 调用OpenAI API with stream=True
            response = client.chat.completions.create(
                model=model_key,
                messages=conversation_history,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_messages.append(content)
                    yield f"data: {content}\n\n"
            
            # 在流结束时保存完整的回复
            full_response = ''.join(collected_messages)
            db.add_message(tag_id, "assistant", full_response)
            
            # 更新使用统计
            tokens_used = len(full_response.split()) * 1.3  # 估算token数
            cost = (tokens_used / 1000) * 0.03
            db.update_tag_usage(tag_id, int(tokens_used), cost)
            
            # 获取总使用量
            total_usage = db.get_total_usage()
            
            # 发送最终的统计信息
            yield f"data: [DONE]\n\n"
            
            # 发送统计信息
            stats = {
                'tokens_used': int(tokens_used),
                'cost': f'${cost:.4f}',
                'total_tokens': total_usage['tokens'],
                'total_cost': f'${total_usage["cost"]:.4f}'
            }
            yield f"data: {json.dumps(stats)}\n\n"

        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"Error in chat stream: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('X-Accel-Buffering', 'no')
    return response

if __name__ == '__main__':
    app.run(debug=True) 