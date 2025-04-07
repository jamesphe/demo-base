# 简历预览功能解决方案

## 一、需求概述

### 1.1 功能描述
- 支持多种格式简历文件的在线预览
- 提供简历内容的结构化展示
- 支持简历文件的下载功能
- 提供AI分析功能

### 1.2 支持的文件类型
- Word文档 (.doc, .docx)
- PDF文件 (.pdf) 
- 图片文件 (.jpg, .jpeg, .png)
- 文本文件 (.txt)

## 二、技术方案

### 2.1 整体架构
```
前端(Vue.js) <-> API接口层(FastAPI) <-> 文件存储系统
                                          <-> 数据库(PostgreSQL)
```

### 2.2 核心接口设计

#### 2.2.1 文件下载接口
```python
GET /api/resume/download/{resume_id}
请求参数:
- resume_id: 简历ID

响应:
- 文件流
- 错误信息(404/500等)
```


### 2.3 数据模型
```python
class Resume(Base):
    id: int
    resume_id: str
    batch_id: int
    file_name: str
    file_path: str
    file_type: str
    content: str
    parsed_data: dict
    processing_status: str
    created_at: datetime
```

## 三、具体实现

### 3.1 前端实现

#### 3.1.1 预览组件
```javascript
// 预览功能实现
async function previewResume(resume) {
    try {
        this.showPreviewModal = true;
        this.previewLoading = true;
        
        const resumeId = resume.resume_id || resume.id;
        const fileName = resume.file_name?.toLowerCase();
        const fileUrl = `/api/resume/download/${resumeId}`;
        
        // 根据文件类型处理预览
        switch(getFileType(fileName)) {
            case 'docx':
                this.previewContent = await handleWordPreview(fileUrl);
                break;
            case 'pdf':
                this.previewContent = createPDFPreview(fileUrl);
                break;
            case 'image':
                this.previewContent = createImagePreview(fileUrl);
                break;
            case 'text':
                this.previewContent = await handleTextPreview(fileUrl);
                break;
        }
    } catch (error) {
        this.handlePreviewError(error);
    } finally {
        this.previewLoading = false;
    }
}
```

#### 3.1.2 UI模板
```html
<div x-data="previewModal" class="modal">
    <!-- 预览模态框 -->
    <div class="modal-content">
        <!-- 头部 -->
        <div class="modal-header">
            <h3>文档预览</h3>
            <button @click="close">×</button>
        </div>
        
        <!-- 加载状态 -->
        <div x-show="loading" class="loading-spinner"></div>
        
        <!-- 预览内容 -->
        <div x-show="!loading" 
             class="preview-container"
             x-html="content">
        </div>
    </div>
</div>
```

### 3.2 后端实现

#### 3.2.1 文件下载处理
```python
@router.get("/resume/download/{resume_id}")
async def download_resume(resume_id: int, db: AsyncSession):
    try:
        # 获取简历信息
        resume = await get_resume(resume_id, db)
        if not resume:
            raise HTTPException(status_code=404)
            
        # 处理文件名和类型
        filename = process_filename(resume)
        media_type = get_media_type(filename)
        
        # 返回文件
        return FileResponse(
            path=resume.file_path,
            filename=filename,
            media_type=media_type
        )
    except Exception as e:
        handle_download_error(e)
```

#### 3.2.2 文件类型处理
```python
def get_media_type(filename: str) -> str:
    """获取文件的媒体类型"""
    media_types = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'doc': 'application/msword',
        'txt': 'text/plain',
        'jpg': 'image/jpeg',
        'png': 'image/png'
    }
    ext = filename.lower().split('.')[-1]
    return media_types.get(ext, 'application/octet-stream')
```

## 四、安全性设计

### 4.1 访问控制
```python
def validate_file_access(resume_id: int, user: User) -> bool:
    """验证用户访问权限"""
    # 检查用户权限
    if not has_permission(user, 'resume:view'):
        return False
        
    # 检查文件所属关系
    resume = get_resume(resume_id)
    return resume.batch_id in user.accessible_batches
```

### 4.2 文件验证
```python
def validate_file(filename: str, content: bytes) -> bool:
    """验证文件"""
    # 检查文件类型
    if not is_allowed_file_type(filename):
        return False
        
    # 检查文件大小
    if len(content) > settings.MAX_FILE_SIZE:
        return False
        
    # 检查文件内容
    if not is_valid_content(filename, content):
        return False
        
    return True
```

## 五、性能优化

### 5.1 大文件处理
```python
async def stream_file(file_path: str):
    """分块处理大文件"""
    chunk_size = 8192
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(chunk_size):
            yield chunk
```

### 5.2 缓存策略
```python
def configure_caching(response: Response, resume: Resume):
    """配置缓存策略"""
    etag = generate_etag(resume)
    response.headers.update({
        'Cache-Control': 'public, max-age=3600',
        'ETag': etag
    })
```

## 六、错误处理

### 6.1 错误类型定义
```python
class PreviewError(Exception):
    """预览错误基类"""
    pass

class FileNotFoundError(PreviewError):
    """文件不存在错误"""
    pass

class FileTypeError(PreviewError):
    """文件类型错误"""
    pass
```

### 6.2 错误处理逻辑
```python
def handle_preview_error(error: Exception) -> dict:
    """处理预览错误"""
    error_mapping = {
        FileNotFoundError: {
            'code': 404,
            'message': '文件不存在或已被删除'
        },
        FileTypeError: {
            'code': 400,
            'message': '不支持的文件类型'
        }
    }
    
    error_info = error_mapping.get(type(error), {
        'code': 500,
        'message': '服务器内部错误'
    })
    
    return error_info
```

## 七、部署说明

### 7.1 环境要求
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Redis (可选,用于缓存)

### 7.2 依赖安装
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
npm install
```

### 7.3 配置说明
```python
# config.py
UPLOAD_DIR = '/path/to/uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.png'}
```

## 八、测试计划

### 8.1 单元测试
```python
def test_file_preview():
    """测试文件预览功能"""
    # 测试各种文件类型
    test_files = {
        'test.pdf': 'application/pdf',
        'test.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'test.txt': 'text/plain'
    }
    
    for filename, expected_type in test_files.items():
        media_type = get_media_type(filename)
        assert media_type == expected_type
```

### 8.2 集成测试
```python
async def test_preview_workflow():
    """测试完整预览流程"""
    # 创建测试数据
    resume = await create_test_resume()
    
    # 测试下载
    response = await client.get(f"/api/resume/download/{resume.id}")
    assert response.status_code == 200
    
    # 测试预览
    response = await client.get(f"/api/resume/preview/{resume.id}")
    assert response.status_code == 200
```

## 九、维护计划

1. 日志监控
2. 性能监控
3. 错误追踪
4. 定期备份
5. 版本更新

## 十、后续优化建议

1. 添加更多文件格式支持
2. 优化预览加载速度
3. 增加预览缓存机制
4. 提供批量预览功能
5. 优化移动端适配
