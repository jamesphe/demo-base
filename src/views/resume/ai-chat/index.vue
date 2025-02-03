<template>
  <div class="ai-chat-container">
    <!-- 左侧对话列表 -->
    <div class="chat-list">
      <div class="list-header">
        <el-button type="primary" icon="el-icon-plus" @click="createNewChat">新建对话</el-button>
      </div>
      <div class="chat-history">
        <div
          v-for="chat in chatList"
          :key="chat.id"
          :class="['chat-item', { active: currentChatId === chat.id }]"
          @click="switchChat(chat.id)"
        >
          <div class="chat-icon">
            <i class="el-icon-chat-dot-round"></i>
          </div>
          <div class="chat-info">
            <span class="chat-title">{{ chat.title || '新对话' }}</span>
            <span class="chat-time">{{ formatTime(chat.createTime) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧对话区域 -->
    <div class="chat-main">
      <div class="chat-messages" ref="messageContainer">
        <!-- 欢迎消息 -->
        <div v-if="currentMessages.length === 0" class="welcome-message">
          <i class="el-icon-s-opportunity"></i>
          <h2>AI 简历助手</h2>
          <p>您可以这样描述需求：</p>
          <div class="example-queries">
            <div class="query-item" @click="useExample('5年Java开发经验，精通Spring Cloud，有微服务架构经验')">
              <i class="el-icon-chat-line-round"></i>
              <span>5年Java开发经验，精通Spring Cloud，有微服务架构经验</span>
            </div>
            <div class="query-item" @click="useExample('前端开发工程师，熟悉Vue和React，有3年以上经验')">
              <i class="el-icon-chat-line-round"></i>
              <span>前端开发工程师，熟悉Vue和React，有3年以上经验</span>
            </div>
            <div class="query-item" @click="useExample('Python开发，有机器学习经验，硕士及以上学历')">
              <i class="el-icon-chat-line-round"></i>
              <span>Python开发，有机器学习经验，硕士及以上学历</span>
            </div>
          </div>
        </div>

        <!-- 对话消息 -->
        <div v-for="message in currentMessages" :key="message.id" :class="['message', message.role]">
          <div class="message-header">
            <i :class="message.role === 'user' ? 'el-icon-user' : 'el-icon-service'"></i>
            <span>{{ message.role === 'user' ? '我' : 'AI助手' }}</span>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>
          <div class="message-content">{{ message.content }}</div>
          <!-- 简历卡片 -->
          <div v-if="message.resumes && message.resumes.length" class="resume-cards">
            <el-card
              v-for="resume in message.resumes"
              :key="resume.id"
              class="resume-card"
              :class="getMatchClass(resume.matchScore)"
              shadow="hover"
            >
              <div class="resume-header">
                <div class="resume-info">
                  <h4>{{ resume.name }}</h4>
                  <div class="title-container">
                    <span class="title">{{ resume.title }}</span>
                    <el-tag size="small" effect="plain">{{ resume.experience }}年经验</el-tag>
                    <el-tag size="small" effect="plain" type="success">{{ resume.education }}</el-tag>
                  </div>
                </div>
                <div class="match-score" v-if="resume.matchScore">
                  <el-tag :type="getScoreType(resume.matchScore)" effect="dark">
                    匹配度: {{ getScoreText(resume.matchScore) }}
                  </el-tag>
                </div>
              </div>
              <div class="skills-container">
                <el-tag
                  v-for="skill in resume.skills"
                  :key="skill"
                  size="small"
                  effect="plain"
                  class="skill-tag"
                >
                  {{ skill }}
                </el-tag>
              </div>
              <div class="resume-actions">
                <el-button type="primary" size="small" plain @click="viewResume(resume.id)">
                  <i class="el-icon-view"></i> 查看详情
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          :maxlength="500"
          show-word-limit
          resize="none"
          placeholder="描述您需要的候选人特征（如：5年Java开发经验，精通Spring Boot...）"
          @keyup.enter.ctrl="sendMessage"
        >
          <template #append>
            <div class="input-tip">按 Ctrl + Enter 发送</div>
          </template>
        </el-input>
        <div class="button-container">
          <el-button type="primary" :loading="loading" @click="sendMessage">
            <i class="el-icon-s-promotion"></i> 发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { formatDateTime } from '@/utils/date'
import { getResumesByAIChat, getChatHistory, saveChat } from '@/api/resume'

export default {
  name: 'AiChat',
  
  data() {
    return {
      currentChatId: null,
      chatList: [],
      currentMessages: [],
      inputMessage: '',
      loading: false
    }
  },

  methods: {
    // 创建新对话
    async createNewChat() {
      const newChat = {
        id: Date.now(),
        title: '新对话',
        createTime: new Date(),
        messages: []
      }
      this.chatList.unshift(newChat)
      this.currentChatId = newChat.id
      this.currentMessages = []
      this.inputMessage = ''
    },

    // 切换对话
    switchChat(chatId) {
      this.currentChatId = chatId
      const chat = this.chatList.find(c => c.id === chatId)
      this.currentMessages = chat.messages
      this.scrollToBottom()
    },

    // 发送消息
    async sendMessage() {
      if (!this.inputMessage.trim()) return
      
      this.loading = true
      try {
        // 添加用户消息
        const userMessage = {
          id: Date.now(),
          role: 'user',
          content: this.inputMessage,
          timestamp: new Date()
        }
        this.currentMessages.push(userMessage)
        
        // 调用AI服务获取回复
        const { data } = await getResumesByAIChat(this.inputMessage)
        
        // 添加AI回复
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: data.reply,
          resumes: data.resumes,
          timestamp: new Date()
        }
        this.currentMessages.push(aiMessage)
        
        // 更新当前对话
        const currentChat = this.chatList.find(c => c.id === this.currentChatId)
        if (currentChat) {
          currentChat.messages = this.currentMessages
          // 如果是第一条消息，更新对话标题
          if (currentChat.messages.length === 2) {
            currentChat.title = userMessage.content.slice(0, 20) + (userMessage.content.length > 20 ? '...' : '')
          }
          // 保存对话记录
          await saveChat(currentChat)
        }
        
        this.inputMessage = ''
        await this.scrollToBottom()
      } catch (error) {
        this.$message.error('发送消息失败：' + error.message)
      } finally {
        this.loading = false
      }
    },

    // 查看简历详情
    viewResume(resumeId) {
      this.$router.push({
        name: 'ResumeDetail',
        params: { id: resumeId }
      })
    },

    // 格式化时间
    formatTime(time) {
      return formatDateTime(time)
    },

    // 滚动到底部
    async scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messageContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    // 加载历史对话记录
    async loadChatHistory() {
      try {
        const { data } = await getChatHistory()
        this.chatList = data
        if (this.chatList.length > 0) {
          this.switchChat(this.chatList[0].id)
        } else {
          this.createNewChat()
        }
      } catch (error) {
        this.$message.error('加载历史对话失败：' + error.message)
        this.createNewChat()
      }
    },

    getScoreType(score) {
      if (score >= 25) return 'success'
      if (score >= 15) return 'warning'
      return 'info'
    },
    
    getScoreText(score) {
      if (score >= 25) return '高度匹配'
      if (score >= 15) return '较好匹配'
      return '部分匹配'
    },

    getMatchClass(score) {
      if (score >= 25) return 'high-match'
      if (score >= 15) return 'medium-match'
      return 'low-match'
    },
    
    useExample(query) {
      this.inputMessage = query
      this.sendMessage()
    }
  },

  mounted() {
    this.loadChatHistory()
  }
}
</script>

<style lang="scss" scoped>
.ai-chat-container {
  display: flex;
  height: calc(100vh - 84px);
  background: #f5f7fa;
  
  .chat-list {
    width: 280px;
    background: #fff;
    border-right: 1px solid #e6e6e6;
    display: flex;
    flex-direction: column;
    box-shadow: 2px 0 8px rgba(0,0,0,0.05);
    
    .list-header {
      padding: 16px;
      border-bottom: 1px solid #e6e6e6;
      text-align: center;
      
      .el-button {
        width: 100%;
      }
    }
    
    .chat-history {
      flex: 1;
      overflow-y: auto;
      
      .chat-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        cursor: pointer;
        border-bottom: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        
        &:hover {
          background: #f5f7fa;
        }
        
        &.active {
          background: #ecf5ff;
          border-right: 3px solid #409EFF;
        }
        
        .chat-icon {
          margin-right: 12px;
          color: #409EFF;
        }
        
        .chat-info {
          flex: 1;
          overflow: hidden;
          
          .chat-title {
            display: block;
            font-size: 14px;
            margin-bottom: 4px;
            color: #303133;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
          
          .chat-time {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }
  }
  
  .chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
    margin: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    
    .chat-messages {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      
      .welcome-message {
        text-align: center;
        padding: 40px 20px;
        color: #606266;
        
        i {
          font-size: 48px;
          color: #409EFF;
          margin-bottom: 20px;
        }
        
        h2 {
          margin-bottom: 20px;
          color: #303133;
        }
        
        .example-queries {
          max-width: 600px;
          margin: 20px auto;
          
          .query-item {
            margin: 12px 0;
            padding: 12px 16px;
            background: #f5f7fa;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            
            &:hover {
              background: #ecf5ff;
              transform: translateY(-2px);
            }
            
            i {
              font-size: 16px;
              margin-right: 8px;
              margin-bottom: 0;
            }
          }
        }
      }
      
      .message {
        margin-bottom: 24px;
        
        .message-header {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
          
          i {
            margin-right: 8px;
            font-size: 16px;
          }
          
          .message-time {
            margin-left: auto;
            font-size: 12px;
            color: #909399;
          }
        }
        
        &.user {
          .message-header {
            color: #409EFF;
          }
          
          .message-content {
            background: #ecf5ff;
            border-radius: 0 8px 8px 8px;
          }
        }
        
        &.assistant {
          .message-header {
            color: #67c23a;
          }
          
          .message-content {
            background: #f0f9eb;
            border-radius: 8px 0 8px 8px;
          }
        }
        
        .message-content {
          padding: 12px 16px;
          line-height: 1.6;
          white-space: pre-wrap;
        }
        
        .resume-cards {
          margin-top: 16px;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 16px;
          
          .resume-card {
            transition: all 0.3s ease;
            
            &:hover {
              transform: translateY(-2px);
            }
            
            &.high-match {
              border-left: 4px solid #67c23a;
            }
            
            &.medium-match {
              border-left: 4px solid #e6a23c;
            }
            
            &.low-match {
              border-left: 4px solid #909399;
            }
            
            .resume-header {
              margin-bottom: 12px;
              
              .resume-info {
                h4 {
                  margin: 0 0 8px 0;
                  color: #303133;
                }
                
                .title-container {
                  display: flex;
                  align-items: center;
                  flex-wrap: wrap;
                  gap: 8px;
                  
                  .title {
                    color: #606266;
                  }
                }
              }
              
              .match-score {
                margin-top: 8px;
              }
            }
            
            .skills-container {
              margin: 12px 0;
              
              .skill-tag {
                margin: 0 8px 8px 0;
              }
            }
            
            .resume-actions {
              margin-top: 12px;
              text-align: right;
            }
          }
        }
      }
    }
    
    .chat-input {
      padding: 16px;
      border-top: 1px solid #e6e6e6;
      background: #fff;
      border-radius: 0 0 8px 8px;
      
      .input-tip {
        padding: 4px 8px;
        color: #909399;
        font-size: 12px;
      }
      
      .button-container {
        margin-top: 12px;
        text-align: right;
        
        .el-button {
          padding: 12px 24px;
        }
      }
    }
  }
}
</style> 