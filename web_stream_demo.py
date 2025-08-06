#!/usr/bin/env python3
"""
Web 流式响应演示
使用 Flask 展示如何将流式封装集成到 Web 应用中
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, request, Response, render_template_string, jsonify
    from flask_cors import CORS
except ImportError:
    print("❌ 需要安装 Flask 和 flask-cors:")
    print("   pip install flask flask-cors")
    sys.exit(1)

from api.llm import LLMClient
from api.stream import create_stream_response


app = Flask(__name__)
CORS(app)  # 允许跨域请求


# 简单的前端页面模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM 流式响应演示</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        #messages { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin: 10px 0; }
        .message { margin: 5px 0; padding: 5px; background: #f5f5f5; border-radius: 3px; }
        .user { background: #e3f2fd; }
        .assistant { background: #f3e5f5; }
        .error { background: #ffebee; color: #c62828; }
        input, select, button { margin: 5px; padding: 8px; }
        #userInput { width: 60%; }
        #sendBtn { background: #4caf50; color: white; border: none; cursor: pointer; }
        #sendBtn:disabled { background: #cccccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 LLM 流式响应演示</h1>
        
        <div>
            <select id="provider">
                <option value="openai">OpenAI</option>
                <option value="gemini">Gemini</option>
                <option value="perplexity">Perplexity</option>
                <option value="groq">Groq</option>
            </select>
            
            <select id="model">
                <option value="gpt-4-1106-preview">GPT-4 Turbo</option>
                <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
                <option value="sonar-pro">Perplexity Sonar Pro</option>
                <option value="llama-3.1-70b-versatile">Llama 3.1 70B</option>
            </select>
        </div>
        
        <div>
            <input type="text" id="userInput" placeholder="输入您的问题..." />
            <button id="sendBtn" onclick="sendMessage()">发送</button>
        </div>
        
        <div id="messages"></div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // 提供商和模型的映射
        const providerModels = {
            'openai': ['gpt-4-1106-preview', 'gpt-3.5-turbo'],
            'gemini': ['gemini-2.5-flash-lite', 'gemini-1.5-pro'],
            'perplexity': ['sonar-pro', 'llama-3.1-sonar-small-128k-online'],
            'groq': ['llama-3.1-70b-versatile', 'llama-3.1-8b-instant']
        };
        
        // 更新模型选项
        document.getElementById('provider').addEventListener('change', function() {
            const provider = this.value;
            const modelSelect = document.getElementById('model');
            modelSelect.innerHTML = '';
            
            providerModels[provider].forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        });
        
        function addMessage(content, isUser, isError = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'} ${isError ? 'error' : ''}`;
            messageDiv.textContent = content;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            const provider = document.getElementById('provider').value;
            const model = document.getElementById('model').value;
            
            addMessage(message, true);
            userInput.value = '';
            sendBtn.disabled = true;
            
            // 创建一个占位消息用于显示流式内容
            const assistantDiv = document.createElement('div');
            assistantDiv.className = 'message assistant';
            assistantDiv.textContent = '思考中...';
            messagesDiv.appendChild(assistantDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // 建立 SSE 连接
            const eventSource = new EventSource(`/stream?message=${encodeURIComponent(message)}&provider=${provider}&model=${model}`);
            
            let content = '';
            
            eventSource.onmessage = function(event) {
                if (event.data === '[DONE]') {
                    eventSource.close();
                    sendBtn.disabled = false;
                    return;
                }
                
                try {
                    const data = JSON.parse(event.data);
                    console.log('收到数据:', data); // 调试日志
                    
                    if (data.error) {
                        assistantDiv.className += ' error';
                        assistantDiv.textContent = `错误: ${data.error}`;
                        eventSource.close();
                        sendBtn.disabled = false;
                    } else if (data.content) {
                        content += data.content;
                        assistantDiv.textContent = content;
                    } else if (data.type === 'finish') {
                        // 处理结束信息
                        console.log('流式响应完成:', data.metadata);
                        // 不关闭连接，等待 [DONE]
                    }
                    
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                } catch (e) {
                    console.error('解析响应失败:', e, event.data);
                }
            };
            
            eventSource.onerror = function(event) {
                console.error('SSE 连接错误:', event);
                eventSource.close();
                if (content.length === 0) {
                    assistantDiv.className += ' error';
                    assistantDiv.textContent = '连接错误，请重试';
                }
                sendBtn.disabled = false;
            };
            
            // 添加超时处理
            const timeoutId = setTimeout(() => {
                if (eventSource.readyState !== EventSource.CLOSED) {
                    console.log('请求超时，关闭连接');
                    eventSource.close();
                    if (content.length === 0) {
                        assistantDiv.className += ' error';
                        assistantDiv.textContent = '请求超时，请重试';
                    }
                    sendBtn.disabled = false;
                }
            }, 30000); // 30秒超时
            
            // 清理定时器
            const originalClose = eventSource.close.bind(eventSource);
            eventSource.close = function() {
                clearTimeout(timeoutId);
                originalClose();
            };
        }
        
        // 回车键发送消息
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !sendBtn.disabled) {
                sendMessage();
            }
        });
        
        // 初始化模型选项
        document.getElementById('provider').dispatchEvent(new Event('change'));
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/stream')
def stream_chat():
    """流式聊天端点"""
    message = request.args.get('message', '')
    provider = request.args.get('provider', 'openai')
    model = request.args.get('model', 'gpt-4-1106-preview')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    def generate_stream():
        """生成器函数，用于 SSE 响应"""
        try:
            llm = LLMClient()
            
            # 获取原始流
            raw_stream = llm.stream_llm(
                provider=provider,
                model=model,
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
                max_tokens=500
            )
            
            # 创建统一流式响应
            stream_response = create_stream_response(raw_stream, provider)
            
            # 转换为 SSE 格式并发送
            sent_content = False
            for sse_chunk in stream_response.to_sse():
                if 'data:' in sse_chunk and sse_chunk.strip() != 'data: [DONE]':
                    sent_content = True
                yield sse_chunk
            
            # 如果没有发送任何内容，发送一个空响应
            if not sent_content:
                empty_response = json.dumps({
                    "content": "抱歉，没有收到响应内容。",
                    "type": "content"
                })
                yield f"data: {empty_response}\n\n"
                yield "data: [DONE]\n\n"
                
        except Exception as e:
            # 发送错误信息
            error_data = json.dumps({
                "error": f"服务器错误: {str(e)}",
                "type": "error"
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"
    
    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API 端点：非流式聊天"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    message = data['message']
    provider = data.get('provider', 'openai')
    model = data.get('model', 'gpt-4-1106-preview')
    
    try:
        llm = LLMClient()
        
        # 获取原始流
        raw_stream = llm.stream_llm(
            provider=provider,
            model=model,
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=500
        )
        
        # 创建统一流式响应并收集完整响应
        stream_response = create_stream_response(raw_stream, provider)
        full_response = stream_response.collect_full_response()
        
        return jsonify(full_response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/providers')
def get_providers():
    """获取支持的提供商和模型列表"""
    return jsonify({
        "providers": {
            "openai": ["gpt-4-1106-preview", "gpt-3.5-turbo"],
            "gemini": ["gemini-2.5-flash-lite", "gemini-1.5-pro"],
            "perplexity": ["sonar-pro", "llama-3.1-sonar-small-128k-online"],
            "groq": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
        }
    })


if __name__ == '__main__':
    print("🌊 启动 Web 流式响应演示")
    print("=" * 50)
    print("📱 访问地址: http://localhost:5000")
    print("🔗 API 端点:")
    print("   GET  /              - 主页（演示界面）")
    print("   GET  /stream        - SSE 流式聊天")
    print("   POST /api/chat      - 非流式 API")
    print("   GET  /api/providers - 获取支持的提供商")
    print("=" * 50)
    print("💡 使用说明:")
    print("   1. 在浏览器中打开 http://localhost:5000")
    print("   2. 选择 LLM 提供商和模型")
    print("   3. 输入问题并发送")
    print("   4. 观察流式响应效果")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)