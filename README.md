# LLM-WEBUI

一个简洁的大语言模型 Web 界面，支持多种模型和实时对话。

## 新增功能

### 流式响应
- 实现打字机效果，实时显示 AI 回复
- 使用 Server-Sent Events (SSE) 进行实时通信
- 支持长对话，自动保留最近 15 轮对话历史

### 对话管理
- 支持多个独立对话
- 自动保存对话历史
- 实时统计 token 使用量和成本

### 用户体验优化
- 实时显示对话内容
- 支持多种模型切换
- 优雅的错误处理
- 响应式设计

## 技术栈

- 后端：Flask + SQLite
- 前端：TailwindCSS + AlpineJS
- API：OpenAI 兼容接口

## 使用方法

1. 安装依赖：

```bash
pip install -r requirements.txt
npm install
```

2. 启动项目

```bash
npm run build-css  # 构建样式
python app.py      # 启动服务
```

3. 开始聊天！

## 🎯 开发相关

- 配置文件: `config.yaml`
- 样式源文件: `static/css/input.css`
- 主界面: `templates/chat.html`

## 🤝 贡献代码

欢迎提 PR！无论是新功能还是 bug 修复，又或者是文档改进，我们都非常感谢！

## 📝 开源协议

MIT License - 随便用，不用负责！

---

> 🌟 如果觉得有帮助，别忘了给个星星！
> 
> 🐛 遇到问题？提 Issue 让我们一起解决！
