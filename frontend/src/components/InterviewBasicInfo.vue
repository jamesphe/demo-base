<template>
  <el-card v-if="interview && interview.candidateName" class="candidate-profile-card">
    <div class="candidate-profile-header">
      <div class="candidate-avatar">
        <el-avatar :size="64" icon="el-icon-user-solid"></el-avatar>
      </div>
      <div class="candidate-main-info">
        <h2 class="candidate-name">{{ interview.candidateName }}</h2>
        <div class="candidate-position">
          <i class="el-icon-suitcase"></i> {{ interview.candidatePosition }}
        </div>
        <div class="interview-type">
          <el-tag :type="getInterviewTypeTag(interview.type)" effect="dark" size="medium">
            {{ getInterviewTypeText(interview.type) }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <el-divider content-position="center">面试详情</el-divider>
    
    <div class="candidate-details">
      <div class="detail-item">
        <div class="detail-icon">
          <i class="el-icon-time"></i>
        </div>
        <div class="detail-content">
          <div class="detail-label">面试时间</div>
          <div class="detail-value">{{ formatDateTime(interview.time) }}</div>
        </div>
      </div>
      
      <div class="detail-item">
        <div class="detail-icon">
          <i class="el-icon-location"></i>
        </div>
        <div class="detail-content">
          <div class="detail-label">面试地点</div>
          <div class="detail-value">{{ interview.location }}</div>
        </div>
      </div>
      
      <div class="detail-item interviewers-container">
        <div class="detail-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="detail-content">
          <div class="detail-label">面试官</div>
          <div class="interviewers-list">
            <el-tag
              v-for="interviewer in interview.interviewers"
              :key="interviewer.id"
              size="small"
              class="interviewer-tag"
              :type="interviewer.id === (currentUser && currentUser.id ? currentUser.id : '') ? 'success' : ''"
              effect="plain"
            >
              {{ interviewer.name || interviewer.username }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
    
    <div class="candidate-actions">
      <slot name="actions">
        <el-button type="primary" size="small" icon="el-icon-phone" @click="$emit('show-contact-info')" plain>
          查看候选人联系方式
        </el-button>
        <el-button type="info" size="small" icon="el-icon-document" @click="$emit('view-resume')" plain>
          查看简历
        </el-button>
      </slot>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'InterviewBasicInfo',
  props: {
    interview: {
      type: Object,
      required: true,
      default: () => ({})
    },
    currentUser: {
      type: Object,
      default: null
    }
  },
  methods: {
    formatDateTime(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getInterviewTypeText(type) {
      const typeMap = {
        first: '初试',
        second: '复试',
        final: '终试'
      }
      return typeMap[type] || '面试'
    },
    getInterviewTypeTag(type) {
      const tagMap = {
        first: 'primary',
        second: 'success',
        final: 'warning'
      }
      return tagMap[type] || 'info'
    }
  }
}
</script>

<style lang="scss" scoped>
.candidate-profile-card {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  background-color: #ffffff;
  border: none;
  
  &:hover {
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.15);
    transform: translateY(-3px);
  }
  
  ::v-deep .el-card__body {
    padding: 0;
  }
}

.candidate-profile-header {
  display: flex;
  align-items: center;
  padding: 28px;
  background: linear-gradient(120deg, #1a73e8 0%, #3b9fe6 100%);
  color: white;
  position: relative;
  overflow: hidden;
  
  &:before {
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 200%;
    background: rgba(255, 255, 255, 0.1);
    transform: rotate(25deg);
    pointer-events: none;
  }
  
  .candidate-avatar {
    margin-right: 28px;
    position: relative;
    z-index: 1;
    
    ::v-deep .el-avatar {
      border: 4px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      transition: all 0.3s;
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
      }
    }
  }
  
  .candidate-main-info {
    position: relative;
    z-index: 1;
    
    .candidate-name {
      margin-bottom: 10px;
      font-size: 24px;
      font-weight: 600;
      color: white;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .candidate-position {
      margin-bottom: 14px;
      font-size: 16px;
      color: rgba(255, 255, 255, 0.95);
      font-weight: 500;
      display: flex;
      align-items: center;
      
      i {
        margin-right: 8px;
      }
    }
    
    .interview-type {
      margin-top: 10px;
      
      ::v-deep .el-tag {
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 6px 12px;
        font-weight: 500;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
      }
    }
  }
}

.el-divider {
  margin: 0;
  
  ::v-deep .el-divider__text {
    background-color: #f5f7fa;
    padding: 8px 20px;
    font-weight: 600;
    color: #606266;
    border-radius: 20px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    font-size: 15px;
  }
}

.candidate-details {
  margin: 24px;
  
  .detail-item {
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    transition: all 0.3s;
    padding: 12px;
    border-radius: 8px;
    
    &:hover {
      background-color: #f9fafc;
      transform: translateX(5px);
    }
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .detail-icon {
      margin-right: 16px;
      color: #409eff;
      background-color: rgba(64, 158, 255, 0.1);
      border-radius: 50%;
      padding: 10px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transition: all 0.3s;
      
      &:hover {
        transform: rotate(15deg);
        background-color: rgba(64, 158, 255, 0.2);
      }
    }
    
    .detail-content {
      flex: 1;
      
      .detail-label {
        margin-bottom: 6px;
        font-size: 14px;
        color: #909399;
        font-weight: 500;
      }
      
      .detail-value {
        font-size: 15px;
        color: #303133;
        font-weight: 500;
      }
    }
  }
}

.interviewers-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .interviewer-tag {
    margin: 3px;
    border-radius: 20px;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.candidate-actions {
  display: flex;
  justify-content: flex-end;
  background-color: #f5f7fa;
  padding: 16px 24px;
  gap: 12px;
  border-top: 1px solid #ebeef5;
  
  .el-button {
    transition: all 0.3s ease;
    border-radius: 8px;
    padding: 10px 20px;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    i {
      margin-right: 6px;
      font-size: 16px;
    }
  }
}

@media screen and (max-width: 768px) {
  .candidate-profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    
    .candidate-avatar {
      margin-right: 0;
      margin-bottom: 16px;
    }
    
    .candidate-main-info {
      .candidate-position {
        justify-content: center;
      }
    }
  }
}
</style> 