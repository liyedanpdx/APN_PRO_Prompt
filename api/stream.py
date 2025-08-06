"""
统一流式响应封装模块
支持多种 LLM 提供商的流式输出统一处理，方便前端集成
"""

import json
from typing import Dict, Any, Optional, Generator, Iterator
from enum import Enum
import time


class StreamType(Enum):
    """流式响应类型枚举"""
    OPENAI_LIKE = "openai_like"  # OpenAI, Gemini, Perplexity
    REQUESTS = "requests"        # Groq, Ali (SSE format)


class ChunkData:
    """标准化的流式数据块"""
    
    def __init__(
        self,
        content: Optional[str] = None,
        chunk_type: str = "content",
        finish_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        self.content = content or ""
        self.type = chunk_type
        self.finish_reason = finish_reason
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "content": self.content,
            "type": self.type,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class UniversalStream:
    """统一流式处理器"""
    
    def __init__(
        self, 
        provider_stream, 
        stream_type: StreamType,
        provider_name: str = "unknown"
    ):
        self.provider_stream = provider_stream
        self.stream_type = stream_type
        self.provider_name = provider_name
        self.finished = False
        self.total_content = ""
        self.chunk_count = 0
        
    def __iter__(self):
        return self
    
    def __next__(self) -> ChunkData:
        """统一的流式数据迭代"""
        if self.finished:
            raise StopIteration
            
        try:
            if self.stream_type == StreamType.OPENAI_LIKE:
                chunk_data = self._handle_openai_chunk()
                # 检查是否结束
                if chunk_data.finish_reason is not None:
                    self.finished = True
                return chunk_data
            elif self.stream_type == StreamType.REQUESTS:
                return self._handle_requests_chunk()
            else:
                raise ValueError(f"Unsupported stream type: {self.stream_type}")
                
        except StopIteration:
            self.finished = True
            raise
        except Exception as e:
            self.finished = True
            error_chunk = ChunkData(
                chunk_type="error",
                error=str(e),
                metadata={"provider": self.provider_name}
            )
            return error_chunk
    
    def _handle_openai_chunk(self) -> ChunkData:
        """处理 OpenAI 风格的流式数据"""
        chunk = next(self.provider_stream)
        
        content = ""
        finish_reason = None
        metadata = {}
        
        # 提取内容
        if hasattr(chunk, 'choices') and chunk.choices:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                self.total_content += content
                self.chunk_count += 1
            
            finish_reason = chunk.choices[0].finish_reason
        
        # 提取元数据（Perplexity 特有）
        if hasattr(chunk, 'usage') and chunk.usage:
            metadata['usage'] = {
                'prompt_tokens': getattr(chunk.usage, 'prompt_tokens', None),
                'completion_tokens': getattr(chunk.usage, 'completion_tokens', None),
                'total_tokens': getattr(chunk.usage, 'total_tokens', None)
            }
            
        if hasattr(chunk, 'search_results') and chunk.search_results:
            metadata['search_results'] = chunk.search_results
        
        return ChunkData(
            content=content,
            finish_reason=finish_reason,
            metadata=metadata
        )
    
    def _handle_requests_chunk(self) -> ChunkData:
        """处理 requests SSE 风格的流式数据"""
        for line in self.provider_stream.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]  # 去掉 'data: ' 前缀
                    if data_str.strip() == '[DONE]':
                        raise StopIteration
                    
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and data['choices']:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            finish_reason = data['choices'][0].get('finish_reason')
                            
                            if content:
                                self.total_content += content
                                self.chunk_count += 1
                                
                            return ChunkData(
                                content=content,
                                finish_reason=finish_reason
                            )
                    except json.JSONDecodeError:
                        continue
        
        raise StopIteration


class StreamResponse:
    """流式响应封装器"""
    
    def __init__(self, universal_stream: UniversalStream):
        self.stream = universal_stream
        
    def to_sse(self) -> Generator[str, None, None]:
        """转换为 Server-Sent Events 格式"""
        try:
            for chunk in self.stream:
                # 发送有内容的块
                if chunk.content or chunk.error:
                    yield f"data: {chunk.to_json()}\n\n"
                
                # 如果遇到结束标志，发送最终块并结束
                if chunk.finish_reason is not None:
                    final_chunk = ChunkData(
                        chunk_type="finish",
                        finish_reason=chunk.finish_reason,
                        metadata={
                            "total_chunks": getattr(self.stream, 'chunk_count', 0),
                            "total_content_length": len(getattr(self.stream, 'total_content', '')),
                            "provider": getattr(self.stream, 'provider_name', 'unknown')
                        }
                    )
                    yield f"data: {final_chunk.to_json()}\n\n"
                    break
            
        except StopIteration:
            pass
        finally:
            # 始终发送结束标志
            yield "data: [DONE]\n\n"
    
    def to_websocket(self) -> Generator[str, None, None]:
        """转换为 WebSocket 格式"""
        try:
            for chunk in self.stream:
                if chunk.content or chunk.error or chunk.finish_reason:
                    yield chunk.to_json()
                    
        except StopIteration as e:
            if hasattr(e, 'value') and e.value:
                yield e.value.to_json()
    
    def collect_full_response(self) -> Dict[str, Any]:
        """收集完整响应（非流式模式）"""
        full_content = ""
        final_metadata = {}
        chunk_count = 0
        
        try:
            for chunk in self.stream:
                if chunk.content:
                    full_content += chunk.content
                    chunk_count += 1
                if chunk.metadata:
                    final_metadata.update(chunk.metadata)
                if chunk.error:
                    return {
                        "success": False,
                        "error": chunk.error,
                        "content": full_content,
                        "metadata": final_metadata
                    }
                    
        except StopIteration as e:
            if hasattr(e, 'value') and e.value:
                final_metadata.update(e.value.metadata)
        
        return {
            "success": True,
            "content": full_content,
            "metadata": final_metadata,
            "chunk_count": chunk_count
        }


def create_stream_response(provider_stream, provider_name: str) -> StreamResponse:
    """
    工厂函数：创建统一的流式响应
    
    Args:
        provider_stream: 原始提供商流对象
        provider_name: 提供商名称 ("openai", "gemini", "perplexity", "groq", "ali")
    
    Returns:
        StreamResponse: 统一的流式响应对象
    """
    # 根据提供商判断流类型
    if provider_name.lower() in ["openai", "gemini", "perplexity"]:
        stream_type = StreamType.OPENAI_LIKE
    else:
        stream_type = StreamType.REQUESTS
    
    universal_stream = UniversalStream(provider_stream, stream_type, provider_name)
    return StreamResponse(universal_stream)


# 简单的使用示例和测试
if __name__ == "__main__":
    print("🌊 流式响应封装模块")
    print("=" * 50)
    
    # 模拟创建流式响应的示例
    print("📝 示例用法：")
    print("""
    # 基础用法
    from api.llm import LLMClient
    from api.stream import create_stream_response
    
    llm = LLMClient()
    raw_stream = llm.stream_llm("openai", "gpt-4", messages)
    stream_response = create_stream_response(raw_stream, "openai")
    
    # SSE 格式 (用于前端)
    for sse_data in stream_response.to_sse():
        print(sse_data, end='')
    
    # 收集完整响应
    full_response = stream_response.collect_full_response()
    print(full_response['content'])
    
    # WebSocket 格式
    for ws_data in stream_response.to_websocket():
        websocket.send(ws_data)
    """)
    
    print("\n✅ 模块加载成功！")
    print("🎯 支持的功能：")
    print("  - 统一多种 LLM 提供商的流式输出")
    print("  - SSE (Server-Sent Events) 格式转换")
    print("  - WebSocket 格式转换")
    print("  - 完整响应收集")
    print("  - 错误处理和元数据提取")