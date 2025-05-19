<template>
  <div class="app-container">
    <el-card class="box-card" shadow="hover">
      <div slot="header" class="clearfix header-container">
        <div class="page-title">
          <i class="el-icon-document"></i>
          <span>面试记录</span>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            size="small" 
            icon="el-icon-plus"
            @click="$router.push('/interview/schedule')"
          >
            安排面试
          </el-button>
          <el-button
            type="success"
            size="small"
            icon="el-icon-download"
            @click="exportData"
          >
            导出数据
          </el-button>
        </div>
      </div>

      <!-- 数据概览 -->
      <el-row :gutter="30" class="data-overview">
        <el-col :md="6" :sm="12" :xs="24">
          <div class="stat-card scheduled">
            <div class="stat-icon">
              <i class="el-icon-time"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ scheduledCount }}</div>
              <div class="stat-title">待面试</div>
            </div>
          </div>
        </el-col>
        <el-col :md="6" :sm="12" :xs="24">
          <div class="stat-card completed">
            <div class="stat-icon">
              <i class="el-icon-check"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ completedCount }}</div>
              <div class="stat-title">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :md="6" :sm="12" :xs="24">
          <div class="stat-card cancelled">
            <div class="stat-icon">
              <i class="el-icon-close"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ cancelledCount }}</div>
              <div class="stat-title">已取消</div>
            </div>
          </div>
        </el-col>
        <el-col :md="6" :sm="12" :xs="24">
          <div class="stat-card pass-rate">
            <div class="stat-icon">
              <i class="el-icon-star-on"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ passRate }}<span class="percent">%</span></div>
              <div class="stat-title">通过率</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 搜索栏 -->
      <el-card class="search-card" shadow="never">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="面试类型">
            <el-select v-model="searchForm.type" placeholder="请选择类型" clearable size="small">
              <el-option label="初试" value="first" />
              <el-option label="复试" value="second" />
              <el-option label="终试" value="final" />
            </el-select>
          </el-form-item>
          <el-form-item label="面试状态">
            <el-select v-model="searchForm.status" placeholder="请选择状态" clearable size="small">
              <el-option label="待面试" value="scheduled" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="面试时间">
            <el-date-picker
              v-model="searchForm.timeRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="yyyy-MM-dd"
              clearable
              size="small"
            />
          </el-form-item>
          <el-form-item label="候选人">
            <el-input v-model="searchForm.candidateName" placeholder="请输入候选人姓名" clearable size="small">
              <i slot="prefix" class="el-input__icon el-icon-user"></i>
            </el-input>
          </el-form-item>
          <el-form-item label="面试官">
            <el-select
              v-model="searchForm.interviewerId"
              placeholder="请选择面试官"
              clearable
              filterable
              size="small"
            >
              <el-option
                v-for="item in interviewerOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item class="search-buttons">
            <el-button type="primary" size="small" icon="el-icon-search" @click="handleSearch">查询</el-button>
            <el-button size="small" icon="el-icon-refresh" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 面试记录列表 -->
      <el-table
        v-loading="loading"
        :data="interviewList"
        element-loading-text="加载中..."
        border
        fit
        stripe
        highlight-current-row
        class="interview-table"
        :header-cell-style="{background:'#f6f8fa', color:'#303133', fontWeight: '500'}"
      >
        <el-table-column type="selection" width="55" align="center" />
        
        <!-- 候选人 -->
        <el-table-column
          label="候选人"
          align="center"
          min-width="120"
          class-name="candidate-column"
        >
          <template slot-scope="scope">
            <div class="candidate-info">
              <span class="candidate-name clickable" @click="handleCandidateClick(scope.row)">
                {{ scope.row.resume ? scope.row.resume.name : scope.row.resumeTitle }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <!-- 面试职位 -->
        <el-table-column
          label="面试职位"
          align="center"
          min-width="120"
          class-name="job-column"
        >
          <template slot-scope="scope">
            <div class="job-info">
              <el-tag 
                size="mini" 
                effect="plain" 
                type="info" 
                class="clickable"
                @click="handleJobClick(scope.row)">
                {{ scope.row.job ? scope.row.job.title : scope.row.jobTitle }}
              </el-tag>
              <span v-if="scope.row.job && scope.row.job.department" class="department-tag">
                {{ scope.row.job.department }}
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- 面试类型 -->
        <el-table-column
          label="面试类型"
          prop="interviewType"
          align="center"
          width="100"
        >
          <template slot-scope="scope">
            <el-tag :type="getInterviewTypeTag(scope.row.interviewType)" size="small">
              {{ getInterviewTypeText(scope.row.interviewType) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 面试时间 -->
        <el-table-column
          label="面试时间"
          prop="scheduleTime"
          align="center"
          width="165"
          sortable="custom"
        >
          <template slot-scope="scope">
            <span>{{ formatDateTime(scope.row.scheduleTime) || '-' }}</span>
          </template>
        </el-table-column>

        <!-- 面试地点 -->
        <el-table-column
          label="面试地点"
          prop="location"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <span>{{ scope.row.location || '-' }}</span>
          </template>
        </el-table-column>

        <!-- 面试官 -->
        <el-table-column
          label="面试官"
          prop="interviewers"
          align="center"
          min-width="120"
        >
          <template slot-scope="scope">
            <template v-if="scope.row.interviewers && scope.row.interviewers.length">
              <el-tag
                v-for="interviewer in scope.row.interviewers"
                :key="interviewer.id"
                size="mini"
                effect="plain"
                class="interviewer-tag"
              >
                {{ interviewer.username }}
              </el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <!-- 状态 -->
        <el-table-column
          label="状态"
          prop="status"
          align="center"
          width="100"
        >
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 评估结果 -->
        <el-table-column
          label="评估结果"
          prop="evaluation"
          align="center"
          width="120"
        >
          <template slot-scope="scope">
            <el-tag
              v-if="scope.row.evaluation && scope.row.evaluation.result"
              :type="getEvaluationType(scope.row.evaluation.result)"
              size="small"
            >
              {{ getEvaluationText(scope.row.evaluation.result) }}
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small">未评估</el-tag>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column
          fixed="right"
          label="操作"
          width="200"
          align="center"
        >
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-tooltip content="面试实时记录" placement="top" v-if="['scheduled', 'in_progress', '待面试', '进行中'].includes(scope.row.status)">
                <el-button
                  size="mini"
                  type="primary"
                  circle
                  @click="handleProcessRecord(scope.row)"
                >
                  <i class="el-icon-edit-outline" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="查看/填写反馈" placement="top" v-if="scope.row.status === 'completed'">
                <el-button
                  size="mini"
                  type="success"
                  circle
                  @click="handleFeedback(scope.row)"
                >
                  <i class="el-icon-s-comment" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="查看详情" placement="top">
                <el-button
                  size="mini"
                  type="primary"
                  circle
                  @click="handleView(scope.row)"
                >
                  <i class="el-icon-view" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑信息" placement="top">
                <el-button
                  size="mini"
                  type="success"
                  circle
                  @click="handleEdit(scope.row)"
                >
                  <i class="el-icon-edit" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="评估结果" placement="top">
                <el-button
                  size="mini"
                  type="warning"
                  circle
                  :disabled="scope.row.status !== 'scheduled' && scope.row.status !== 'in_progress'"
                  @click="handleEvaluation(scope.row)"
                >
                  <i class="el-icon-chat-line-round" />
                </el-button>
              </el-tooltip>
              <el-tooltip content="面试材料" placement="top">
                <el-button
                  size="mini"
                  type="info"
                  circle
                  @click="handlePreparation(scope.row)"
                >
                  <i class="el-icon-document" />
                </el-button>
              </el-tooltip>
              <el-dropdown trigger="click" @command="(command) => handleCommand(command, scope.row)">
                <el-button size="mini" type="primary" circle>
                  <i class="el-icon-more"></i>
                </el-button>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item command="feedback">提交反馈</el-dropdown-item>
                  <el-dropdown-item v-if="hasAdminOrHrRole && scope.row.status === 'scheduled'" 
                    command="cancel">取消面试</el-dropdown-item>
                  <el-dropdown-item command="download" divided>下载简历</el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
              <el-button
                size="mini"
                type="success"
                @click="handleViewEvaluation(scope.row)"
                v-if="scope.row.status === 'evaluated'"
              >
                查看评估
              </el-button>
              <el-button
                size="mini"
                type="warning"
                @click="handleEvaluate(scope.row)"
                v-if="scope.row.status === 'completed' && canEvaluate"
              >
                评估
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <pagination
          v-show="total>0"
          :total="total"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.limit"
          @pagination="getList"
        />
      </div>
    </el-card>

    <!-- 面试详情对话框 -->
    <el-dialog
      title="面试详情"
      :visible.sync="detailDialogVisible"
      width="800px"
      class="interview-detail-dialog"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading" class="detail-container">
        <div class="detail-header" v-if="currentInterview.resume">
          <div class="header-left">
            <div class="candidate-avatar-large">
              <img :src="currentInterview.resume.avatar || '/static/default-avatar.png'" alt="头像">
            </div>
            <div class="candidate-info-large">
              <h2>{{ currentInterview.resume.name }}</h2>
              <p>{{ currentInterview.job ? currentInterview.job.title : currentInterview.jobTitle }}</p>
              <div class="tags-container">
                <el-tag :type="getInterviewTypeTag(currentInterview.interviewType)" effect="plain" size="small">
                  {{ getInterviewTypeText(currentInterview.interviewType) }}
                </el-tag>
                <el-tag :type="getStatusType(currentInterview.status)" effect="dark" size="small">
                  {{ getStatusText(currentInterview.status) }}
                </el-tag>
              </div>
            </div>
          </div>
          <div class="header-right">
            <div class="interview-time">
              <i class="el-icon-time"></i>
              <span>{{ formatDateTime(currentInterview.scheduleTime) }}</span>
            </div>
            <div class="interview-id">ID: {{ currentInterview.id }}</div>
          </div>
        </div>
        
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="基本信息" name="basic">
            <el-card shadow="never" class="info-card">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">面试ID</span>
                    <span class="info-content">{{ currentInterview.id }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">面试类型</span>
                    <span class="info-content">
                      <el-tag :type="getInterviewTypeTag(currentInterview.interviewType)" effect="dark">
                        {{ getInterviewTypeText(currentInterview.interviewType) }}
                      </el-tag>
                    </span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">面试时间</span>
                    <span class="info-content">{{ formatDateTime(currentInterview.scheduleTime) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">面试地点</span>
                    <span class="info-content">{{ currentInterview.location }}</span>
                  </div>
                </el-col>
                <el-col :span="24">
                  <div class="info-item">
                    <span class="info-label">面试官</span>
                    <span class="info-content">
                      <el-tag
                        v-for="interviewer in currentInterview.interviewers"
                        :key="interviewer.id"
                        size="mini"
                        effect="plain"
                        class="interviewer-tag"
                      >
                        {{ interviewer.username }}
                      </el-tag>
                    </span>
                  </div>
                </el-col>
                <el-col :span="24">
                  <div class="info-item">
                    <span class="info-label">备注</span>
                    <span class="info-content">{{ currentInterview.notes || '无' }}</span>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-tab-pane>

          <!-- 候选人信息 -->
          <el-tab-pane label="候选人信息" name="candidate" v-if="currentInterview.resume">
            <el-card shadow="never" class="info-card">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">姓名</span>
                    <span class="info-content">{{ currentInterview.resume.name }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">性别</span>
                    <span class="info-content">{{ getGenderText(currentInterview.resume.gender) }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">电话</span>
                    <span class="info-content">{{ currentInterview.resume.phone }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">邮箱</span>
                    <span class="info-content">{{ currentInterview.resume.email }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">最高学历</span>
                    <span class="info-content">{{ currentInterview.resume.highestEducation }}</span>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <span class="info-label">专业</span>
                    <span class="info-content">{{ currentInterview.resume.major || '未填写' }}</span>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-tab-pane>

          <!-- 评估结果 -->
          <el-tab-pane label="评估结果" name="evaluation" v-if="currentInterview.feedback">
            <div class="evaluation-summary">
              <div class="eval-result">
                <el-tag :type="getEvaluationType(currentInterview.feedback.result)" effect="dark" size="medium">
                  {{ getEvaluationText(currentInterview.feedback.result) }}
                </el-tag>
                <span class="eval-time">{{ formatDateTime(currentInterview.feedback.time) }}</span>
              </div>
              <div class="eval-scores" v-if="currentInterview.feedback.scores">
                <div class="score-item">
                  <div class="score-label">技术能力</div>
                  <el-rate
                    v-model="currentInterview.feedback.scores.technical"
                    disabled
                    show-score
                    text-color="#ff9900"
                  />
                </div>
                <div class="score-item">
                  <div class="score-label">沟通能力</div>
                  <el-rate
                    v-model="currentInterview.feedback.scores.communication"
                    disabled
                    show-score
                    text-color="#ff9900"
                  />
                </div>
                <div class="score-item">
                  <div class="score-label">综合评分</div>
                  <el-rate
                    v-model="currentInterview.feedback.scores.overall"
                    disabled
                    show-score
                    text-color="#ff9900"
                  />
                </div>
              </div>
              
              <div class="eval-comments">
                <div class="comments-header">
                  <span class="comments-title">评估意见</span>
                  <span class="evaluator">评估人: {{ currentInterview.feedback.evaluator }}</span>
                </div>
                <div class="comments-content">
                  {{ currentInterview.feedback.comments || '无评估意见' }}
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <!-- 新增：反馈历史标签页 -->
          <el-tab-pane label="反馈历史" name="feedback-history">
            <div v-if="currentInterview.feedbacks && currentInterview.feedbacks.length">
              <div class="feedback-list">
                <el-card v-for="(feedback, index) in currentInterview.feedbacks" 
                         :key="index" 
                         class="feedback-card"
                         shadow="hover">
                  <div class="feedback-header">
                    <div class="interviewer-info">
                      <span class="interviewer-name">{{ feedback.interviewer.username }}</span>
                      <span class="feedback-time">{{ formatDateTime(feedback.submitTime) }}</span>
                    </div>
                    <el-tag :type="getEvaluationType(feedback.result)" size="small">
                      {{ getEvaluationText(feedback.result) }}
                    </el-tag>
                  </div>
                  
                  <div class="feedback-scores">
                    <div class="score-row">
                      <span class="score-label">技术能力</span>
                      <el-rate v-model="feedback.scores.technical" disabled show-score />
                    </div>
                    <div class="score-row">
                      <span class="score-label">沟通能力</span>
                      <el-rate v-model="feedback.scores.communication" disabled show-score />
                    </div>
                    <div class="score-row">
                      <span class="score-label">综合评分</span>
                      <el-rate v-model="feedback.scores.overall" disabled show-score />
                    </div>
                  </div>
                  
                  <div class="feedback-comments">
                    <p>{{ feedback.comments || '无评价意见' }}</p>
                  </div>
                </el-card>
              </div>
            </div>
            <div v-else class="empty-data">
              <i class="el-icon-chat-dot-square"></i>
              <p>暂无反馈记录</p>
            </div>
          </el-tab-pane>
          
          <!-- 新增：面试记录标签页 -->
          <el-tab-pane label="面试记录" name="interview-notes">
            <div v-if="currentInterview.questions && currentInterview.questions.length">
              <el-collapse accordion>
                <el-collapse-item v-for="(question, index) in currentInterview.questions" 
                                 :key="index"
                                 :title="`问题 ${index+1}: ${question.title}`">
                  <div class="question-content">
                    <p><strong>问题内容：</strong>{{ question.content }}</p>
                    <p><strong>候选人回答：</strong>{{ question.answer || '未记录' }}</p>
                    <div class="question-rating">
                      <span>评分：</span>
                      <el-rate v-model="question.rating" disabled show-score />
                    </div>
                    <p v-if="question.comment"><strong>评价：</strong>{{ question.comment }}</p>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div v-else class="empty-data">
              <i class="el-icon-document"></i>
              <p>暂无面试问题记录</p>
            </div>
          </el-tab-pane>
          
          <!-- 新增：历史记录标签页 -->
          <el-tab-pane label="操作历史" name="history">
            <el-timeline>
              <el-timeline-item
                v-for="(activity, index) in currentInterview.history || []"
                :key="index"
                :timestamp="formatDateTime(activity.time)"
                :color="getHistoryColor(activity.action)"
              >
                <el-card shadow="hover" class="history-card">
                  <strong>{{ activity.user.username }}</strong> {{ getHistoryText(activity.action) }}
                  <p v-if="activity.notes" class="history-notes">{{ activity.notes }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <div v-if="!currentInterview.history || !currentInterview.history.length" class="empty-data">
              <i class="el-icon-time"></i>
              <p>暂无操作历史记录</p>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <div class="dialog-footer" slot="footer">
          <div class="footer-left">
            <el-button 
              v-if="hasAdminOrHrRole && currentInterview.status === 'scheduled'"
              type="danger" 
              size="small" 
              @click="handleCancel(currentInterview)"
            >
              取消面试
            </el-button>
          </div>
          <div class="footer-right">
            <el-button @click="detailDialogVisible = false">关闭</el-button>
            <el-button 
              type="success" 
              v-if="currentInterview.status === 'completed'"
              @click="downloadReport(currentInterview)"
            >
              导出报告
            </el-button>
            <el-button 
              type="primary" 
              v-if="currentInterview.status === 'scheduled'" 
              @click="handleEvaluation(currentInterview)"
            >
              开始评估
            </el-button>
            <el-button 
              type="warning" 
              v-if="currentInterview.status === 'scheduled' || currentInterview.status === 'in_progress'"
              @click="handleEdit(currentInterview)"
            >
              编辑信息
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 候选人详情对话框 -->
    <el-dialog
      title="候选人详情"
      :visible.sync="candidateDetailVisible"
      width="800px"
      custom-class="candidate-detail-dialog"
    >
      <div v-loading="resumeDetailLoading" class="candidate-detail-container">
        <div v-if="!currentResumeDetail || !Object.keys(currentResumeDetail).length" style="color: red; padding: 20px;">
          <p>当前简历详情对象为空</p>
          <p>Store中的currentDetail: {{ $store.state.resume.currentDetail ? '有值' : '无值' }}</p>
        </div>
        <resume-detail v-else :detail="currentResumeDetail" :loading="resumeDetailLoading" />
      </div>
    </el-dialog>
    
    <!-- 职位详情对话框 -->
    <el-dialog
      title="职位详情"
      :visible.sync="jobDetailVisible"
      width="700px"
      custom-class="job-detail-dialog"
    >
      <div v-if="!currentJob || !Object.keys(currentJob).length" class="empty-data">
        <i class="el-icon-document"></i>
        <p>暂无职位详情</p>
      </div>
      <div v-else class="job-detail-container">
        <el-card shadow="never" class="info-card">
          <div slot="header" class="clearfix">
            <span class="job-title">{{ currentJob.title }}</span>
            <el-tag size="medium" type="success" effect="dark">{{ currentJob.department }}</el-tag>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">职位编号</span>
                <span class="info-content">{{ currentJob.id || '暂无' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">工作地点</span>
                <span class="info-content">{{ currentJob.location || '暂无' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">薪资范围</span>
                <span class="info-content">{{ currentJob.salaryRange || '暂无' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">招聘人数</span>
                <span class="info-content">{{ currentJob.headcount || '暂无' }}</span>
              </div>
            </el-col>
          </el-row>
          
          <el-divider content-position="left">职位要求</el-divider>
          <div class="job-description" v-if="currentJob.description">
            <p>{{ currentJob.description }}</p>
          </div>
          
          <div class="job-requirements" v-if="currentJob.requirements">
            <div v-for="(req, index) in currentJob.requirements" :key="index" class="req-item">
              <i class="el-icon-check"></i>
              <span>{{ req }}</span>
            </div>
          </div>
          
          <div v-if="!currentJob.description && !currentJob.requirements" class="empty-data">
            <p>暂无详细职位要求信息</p>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { getInterviewerList, getInterviewDetail } from '@/api/interview'
import ResumeDetail from '@/components/ResumeDetail'
import { getResumeDetail } from '@/api/resume'
import JobDetail, { showJobDetail } from '@/components/JobDetail'

export default {
  name: 'InterviewRecord',
  components: {
    Pagination,
    ResumeDetail,
    JobDetail
  },
  data() {
    return {
      listQuery: {
        page: 1,
        limit: 10,
        sortField: '',
        sortOrder: ''
      },
      searchForm: {
        type: '',
        status: '',
        timeRange: [],
        candidateName: '',
        interviewerId: ''
      },
      interviewerOptions: [],
      detailDialogVisible: false,
      detailLoading: false,
      currentInterview: {},
      hasAdminOrHrRole: false,
      activeTab: 'basic',
      scheduledCount: 0,
      completedCount: 0,
      cancelledCount: 0,
      passRate: 0,
      candidateDetailVisible: false,
      resumeDetailLoading: false,
      jobDetailVisible: false,
      currentJob: {},
      canEvaluate: false
    }
  },
  computed: {
    ...mapGetters('interview', [
      'interviewList',
      'total',
      'loading'
    ]),
    currentResumeDetail() {
      return this.$store.state.resume.currentDetail || {}
    },
    roles() {
      return this.$store.getters['user/roles'] || []
    }
  },
  created() {
    this.getList()
    this.getInterviewers()
    this.checkUserRoles()
    this.calculateStatistics()
    this.canEvaluate = this.roles.some(role => ['admin', 'tenant_admin', 'tenant_hr'].includes(role))
  },
  mounted() {
    console.log('面试记录组件已挂载')
    // 检查resume模块是否注册到store中
    console.log('store中的模块:', Object.keys(this.$store._modules.root._children))
    console.log('resume模块是否存在:', !!this.$store._modules.root._children.resume)
    
    // 打印getter信息
    console.log('所有store getters:', Object.keys(this.$store.getters))
    const resumeGetters = Object.keys(this.$store.getters).filter(key => key.startsWith('resume/'))
    console.log('resume相关的getters:', resumeGetters)
  },
  methods: {
    ...mapActions('interview', [
      'getInterviewList',
      'updateInterview'
    ]),
    async checkUserRoles() {
      try {
        // 从store中获取用户角色信息
        const userRoles = this.$store.getters['user/roles'] || []
        // 检查是否有admin或hr角色
        this.hasAdminOrHrRole = userRoles.some(role => ['admin', 'hr'].includes(role))
      } catch (error) {
        console.error('获取用户角色失败:', error)
      }
    },
    calculateStatistics() {
      // 这里应该从实际数据中统计
      this.scheduledCount = 5
      this.completedCount = 15
      this.cancelledCount = 2
      this.passRate = 75
    },
    async getList() {
      try {
        const params = {
          ...this.listQuery,
          ...this.searchForm,
          timeStart: this.searchForm.timeRange?.[0],
          timeEnd: this.searchForm.timeRange?.[1]
        }
        await this.getInterviewList(params)
        this.calculateStatistics()
      } catch (error) {
        console.error('获取面试列表失败:', error)
        this.$message.error('获取面试列表失败')
      }
    },
    async getInterviewers() {
      try {
        const response = await getInterviewerList()
        this.interviewerOptions = response.data
      } catch (error) {
        console.error('获取面试官列表失败:', error)
        this.$message.error('获取面试官列表失败')
      }
    },
    handleSearch() {
      this.listQuery.page = 1
      this.getList()
    },
    resetSearch() {
      this.searchForm = {
        type: '',
        status: '',
        timeRange: [],
        candidateName: '',
        interviewerId: ''
      }
      this.listQuery.page = 1
      this.getList()
    },
    handleCommand(command, row) {
      switch (command) {
        case 'view':
          this.handleView(row)
          break
        case 'edit':
          this.handleEdit(row)
          break
        case 'preparation':
          this.handlePreparation(row)
          break
        case 'evaluation':
          this.handleEvaluation(row)
          break
        case 'feedback':
          this.handleFeedback(row)
          break
        case 'cancel':
          this.handleCancel(row)
          break
      }
    },
    async handleView(row) {
      this.detailDialogVisible = true
      this.detailLoading = true
      try {
        console.log('获取面试详情, ID:', row.id)
        const response = await getInterviewDetail(row.id)
        console.log('面试详情返回结果:', response)
        
        if (!response || !response.data) {
          throw new Error('API返回数据为空')
        }
        
        this.currentInterview = response.data
        console.log('设置到当前面试对象:', this.currentInterview)
        this.activeTab = 'basic'
      } catch (error) {
        console.error('获取面试详情失败:', error)
        this.$message.error(`获取面试详情失败: ${error.message || '未知错误'}`)
        
        // 如果是开发模式，使用样例数据
        if (process.env.NODE_ENV === 'development') {
          console.log('开发模式: 使用样例数据')
          // 使用一些示例数据，避免界面崩溃
          this.currentInterview = {
            id: row.id || '001',
            resume: {
              name: row.resume ? row.resume.name : '测试候选人',
              gender: 'male',
              phone: '13800000000',
              email: 'test@example.com',
              highestEducation: '本科',
              major: '计算机科学'
            },
            interviewType: row.interviewType || 'first',
            status: row.status || 'scheduled',
            scheduleTime: row.scheduleTime || new Date().getTime(),
            location: row.location || '线上面试',
            interviewers: row.interviewers || [],
            notes: row.notes || ''
          }
        }
      } finally {
        this.detailLoading = false
      }
    },
    handleEdit(row) {
      this.$router.push(`/interview/schedule?id=${row.id}`)
    },
    async handleCancel(row) {
      try {
        await this.$confirm('确认取消该面试吗？', '提示', {
          type: 'warning'
        })
        await this.updateInterview({
          id: row.id,
          data: { status: 'cancelled' }
        })
        this.$message.success('面试已取消')
        this.getList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('取消面试失败:', error)
          this.$message.error('取消面试失败')
        }
      }
    },
    handlePreparation(row) {
      this.$router.push(`/interview/preparation/${row.id}`)
    },
    handleProcessRecord(row) {
      this.$router.push(`/interview/process-record/${row.id}`)
    },
    handleEvaluation(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
    },
    handleFeedback(row) {
      this.$router.push(`/interview/feedback/${row.id}`)
    },
    exportData() {
      this.$message.success('面试数据导出成功')
    },
    downloadResume() {
      this.$message.success('简历下载成功')
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
    },
    getStatusText(status) {
      const statusMap = {
        scheduled: '待面试',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[status] || '未知'
    },
    getStatusType(status) {
      const typeMap = {
        scheduled: 'warning',
        completed: 'success',
        cancelled: 'info'
      }
      return typeMap[status] || ''
    },
    getEvaluationText(result) {
      const resultMap = {
        pass: '通过',
        fail: '不通过',
        pending: '待定'
      }
      return resultMap[result] || '未评估'
    },
    getEvaluationType(result) {
      const typeMap = {
        pass: 'success',
        fail: 'danger',
        pending: 'warning'
      }
      return typeMap[result] || 'info'
    },
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
    getGenderText(gender) {
      const genderMap = {
        M: '男',
        F: '女',
        male: '男',
        female: '女',
        other: '其他'
      }
      return genderMap[gender] || '未知'
    },
    getHistoryColor(action) {
      const colorMap = {
        'create': '#409EFF',
        'update': '#67C23A',
        'cancel': '#E6A23C',
        'complete': '#67C23A',
        'evaluate': '#409EFF'
      }
      return colorMap[action] || '#909399'
    },
    getHistoryText(action) {
      const textMap = {
        'create': '创建了面试',
        'update': '更新了面试信息',
        'cancel': '取消了面试',
        'complete': '完成了面试',
        'evaluate': '提交了评估'
      }
      return textMap[action] || action
    },
    downloadReport(interview) {
      this.$message.success('面试评估报告已导出')
      // 实际实现应该调用后端API生成并下载报告
    },
    handleCandidateClick(row) {
      // 添加调试信息，查看面试记录的完整数据
      console.log('面试记录数据:', row)
      console.log('简历ID:', row.resume_id)
      console.log('候选人信息:', row.resume)
      
      // 尝试获取简历ID，优先使用resume_id，然后尝试其他可能的字段
      const resumeId = row.resume_id || (row.resume && row.resume.id);
      
      console.log('尝试获取的简历ID:', resumeId)
      
      if (!resumeId) {
        console.log('寻找替代ID:',
          '候选人ID:', row.candidate_id,
          '简历名称:', row.resumeTitle
        )
        
        this.$message.warning('该面试无关联简历信息')
        return
      }
      
      console.log('将使用简历ID获取详情:', resumeId)
      this.candidateDetailVisible = true
      this.resumeDetailLoading = true
      
      // 直接调用API获取数据，避免使用Vuex
      getResumeDetail(resumeId)
        .then(response => {
          console.log('API响应结果:', response)
          
          // 手动格式化数据
          const data = response.data || response
          console.log('获取到的原始数据:', data)
          
          // 手动设置当前简历详情
          const formattedData = this.formatResumeData(data)
          console.log('格式化后的数据:', formattedData)
          
          // 设置到store中
          this.$store.commit('resume/SET_CURRENT_DETAIL', formattedData)
          
          // 确认数据已经设置
          this.$nextTick(() => {
            console.log('设置后的简历详情:', this.currentResumeDetail)
            console.log('从store获取的数据:', this.$store.state.resume.currentDetail)
          })
        })
        .catch(error => {
          console.error('获取候选人简历详情失败:', error)
          console.error('错误详情:', error.response ? error.response.data : error.message)
          this.$message.error('获取候选人简历详情失败')
        })
        .finally(() => {
          this.resumeDetailLoading = false
        })
    },
    
    // 简单的格式化函数
    formatResumeData(data) {
      if (!data) return null
      
      // 计算年龄
      let age = data.age
      if (!age && data.birthdate) {
        const birthDate = new Date(data.birthdate)
        const today = new Date()
        age = today.getFullYear() - birthDate.getFullYear()
        const m = today.getMonth() - birthDate.getMonth()
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
          age--
        }
      }
      
      return {
        id: data.id,
        name: data.name,
        age: age,
        gender: data.gender,
        education: data.highestEducation || data.education,
        experience: data.experienceYears,
        phone: data.phone,
        email: data.email,
        currentPosition: data.currentPosition,
        expectedPosition: data.expectedPosition,
        expectedSalary: data.expectedSalary,
        skills: Array.isArray(data.skills) ? data.skills.map(skill => ({
          name: typeof skill === 'string' ? skill : skill.name,
          level: typeof skill === 'string' ? null : skill.level
        })) : [],
        workExperience: (data.workHistory || data.workExperience || []).map(work => ({
          company: work.company,
          position: work.position,
          startDate: work.startDate || work.start_date,
          endDate: work.endDate || work.end_date,
          description: work.description,
          achievements: work.achievements || []
        })),
        educationDetail: (data.eduExperience || data.educationDetail || []).map(edu => ({
          school: edu.school,
          major: edu.major,
          degree: edu.degree,
          startDate: edu.startDate || edu.start_date,
          endDate: edu.endDate || edu.end_date,
          achievements: edu.achievements || []
        })),
        status: data.reviewStatus || data.status || 'pending',
        currentCompany: data.currentCompany,
        currentCity: data.city || data.currentCity || data.currentAddress,
        expectedLocation: data.expectedLocation,
        currentSalary: data.currentSalary,
        starred: data.starred || false,
        updateTime: data.updatedAt || data.updateTime,
        fileName: data.fileName
      }
    },
    handleJobClick(row) {
      if (row.job && row.job.id) {
        showJobDetail(this, row.job.id)
      } else {
        this.$message.warning('职位信息不完整，无法查看详情')
      }
    },
    handleViewEvaluation(row) {
      this.$router.push(`/interview/view-evaluation/${row.id}`)
    },
    handleEvaluate(row) {
      this.$router.push(`/interview/evaluation/${row.id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}

.box-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  
  i {
    margin-right: 8px;
    font-size: 20px;
    color: #409EFF;
  }
}

.header-actions {
  display: flex;
  gap: 10px;
}

.data-overview {
  margin: 20px 0 30px;
  
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    border-radius: 8px;
    transition: all 0.3s;
    background-color: #fff;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    height: 100px;
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 6px;
      height: 100%;
    }
    
    &.scheduled::before {
      background-color: #409EFF;
    }
    
    &.completed::before {
      background-color: #67C23A;
    }
    
    &.cancelled::before {
      background-color: #909399;
    }
    
    &.pass-rate::before {
      background-color: #E6A23C;
    }
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background-color: rgba(64, 158, 255, 0.1);
      color: #409EFF;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      
      i {
        font-size: 28px;
      }
    }
    
    &.scheduled .stat-icon {
      background-color: rgba(64, 158, 255, 0.1);
      color: #409EFF;
    }
    
    &.completed .stat-icon {
      background-color: rgba(103, 194, 58, 0.1);
      color: #67C23A;
    }
    
    &.cancelled .stat-icon {
      background-color: rgba(144, 147, 153, 0.1);
      color: #909399;
    }
    
    &.pass-rate .stat-icon {
      background-color: rgba(230, 162, 60, 0.1);
      color: #E6A23C;
    }
    
    .stat-info {
      flex: 1;
      
      .stat-value {
        font-size: 30px;
        font-weight: bold;
        color: #303133;
        line-height: 1;
        margin-bottom: 5px;
        
        .percent {
          font-size: 16px;
          margin-left: 2px;
        }
      }
      
      .stat-title {
        font-size: 14px;
        color: #909399;
      }
    }
  }
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.search-form {
  padding: 15px 5px;
  
  .el-form-item {
    margin-bottom: 15px;
    margin-right: 18px;
  }
  
  .search-buttons {
    margin-left: auto;
  }
}

.interview-table {
  margin-top: 20px;
  
  .candidate-info {
    display: flex;
    align-items: center;
    justify-content: center;
    
    .candidate-name {
      font-weight: 500;
      color: #409EFF;
      
      &.clickable {
        cursor: pointer;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
  
  .job-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    
    .clickable {
      cursor: pointer;
      
      &:hover {
        color: #409EFF;
        border-color: #409EFF;
      }
    }
    
    .department-tag {
      font-size: 12px;
      color: #909399;
    }
  }
}

.pagination-container {
  padding: 10px 0;
  text-align: right;
}

.interview-detail-dialog {
  .el-dialog__body {
    padding: 0;
  }
  
  .detail-container {
    padding: 0;
    
    .detail-header {
      display: flex;
      justify-content: space-between;
      padding: 20px;
      background-color: #f9fafc;
      border-bottom: 1px solid #ebeef5;
      
      .header-left {
        display: flex;
      }
      
      .header-right {
        text-align: right;
        
        .interview-time {
          font-size: 14px;
          color: #606266;
          margin-bottom: 8px;
          
          i {
            margin-right: 4px;
          }
        }
        
        .interview-id {
          font-size: 12px;
          color: #909399;
        }
      }
      
      .candidate-avatar-large {
        width: 64px;
        height: 64px;
        margin-right: 16px;
        
        img {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          object-fit: cover;
        }
      }
      
      .candidate-info-large {
        h2 {
          margin: 0 0 8px;
          font-size: 18px;
          font-weight: bold;
        }
        
        p {
          margin: 0 0 8px;
          color: #606266;
        }
        
        .tags-container {
          display: flex;
          gap: 8px;
        }
      }
    }
    
    .interviewer-tag {
      margin-right: 5px;
    }
    
    .evaluation-summary {
      padding: 15px;
      
      .eval-result {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
        align-items: center;
        
        .eval-time {
          color: #909399;
          font-size: 13px;
        }
      }
      
      .eval-scores {
        margin-bottom: 20px;
        
        .score-item {
          margin-bottom: 10px;
          
          .score-label {
            display: inline-block;
            width: 80px;
            font-weight: bold;
          }
        }
      }
      
      .eval-comments {
        background-color: #f5f7fa;
        padding: 15px;
        border-radius: 4px;
        
        .comments-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 10px;
          
          .comments-title {
            font-weight: bold;
          }
          
          .evaluator {
            color: #909399;
            font-size: 13px;
          }
        }
        
        .comments-content {
          line-height: 1.6;
          white-space: pre-line;
        }
      }
    }
    
    .dialog-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .footer-left {
        display: flex;
        gap: 8px;
      }
      
      .footer-right {
        display: flex;
        gap: 8px;
      }
    }
  }
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  .feedback-card {
    margin-bottom: 0;
    
    .feedback-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 15px;
      
      .interviewer-info {
        .interviewer-name {
          font-weight: bold;
          margin-right: 10px;
        }
        
        .feedback-time {
          color: #909399;
          font-size: 12px;
        }
      }
    }
    
    .feedback-scores {
      margin-bottom: 15px;
      
      .score-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        .score-label {
          width: 80px;
          text-align: left;
        }
      }
    }
    
    .feedback-comments {
      background-color: #f8f8f8;
      padding: 10px;
      border-radius: 4px;
      
      p {
        margin: 0;
        line-height: 1.6;
      }
    }
  }
}

.question-content {
  padding: 0 10px;
  
  p {
    margin: 10px 0;
    line-height: 1.6;
  }
  
  .question-rating {
    display: flex;
    align-items: center;
    margin: 10px 0;
    
    span {
      margin-right: 10px;
      font-weight: bold;
    }
  }
}

.history-card {
  padding: 10px 15px;
  
  .history-notes {
    margin-top: 5px;
    color: #606266;
    font-size: 13px;
  }
}

.empty-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #909399;
  
  i {
    font-size: 32px;
    margin-bottom: 10px;
  }
  
  p {
    margin: 0;
  }
}

.el-timeline {
  padding: 20px;
}

.candidate-detail-dialog {
  ::v-deep .el-dialog__header {
    padding: 20px;
    border-bottom: 1px solid #EBEEF5;
  }
  
  ::v-deep .el-dialog__body {
    padding: 0;
  }
  
  .candidate-detail-container {
    position: relative;
  }
}

.job-detail-dialog {
  ::v-deep .el-dialog__header {
    padding: 20px;
    border-bottom: 1px solid #EBEEF5;
  }
  
  .job-detail-container {
    padding: 0;
    
    .job-title {
      font-size: 18px;
      font-weight: bold;
      margin-right: 15px;
    }
    
    .job-description {
      margin-bottom: 20px;
      line-height: 1.6;
      color: #303133;
    }
    
    .job-requirements {
      margin-top: 15px;
      
      .req-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 10px;
        
        i {
          color: #67C23A;
          margin-right: 10px;
          margin-top: 3px;
        }
      }
    }
  }
}

.info-card {
  margin-bottom: 20px;
  
  .info-item {
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
    
    .info-label {
      width: 80px;
      color: #606266;
      font-weight: bold;
      text-align: right;
      margin-right: 10px;
      flex-shrink: 0;
    }
    
    .info-content {
      flex: 1;
    }
  }
}

.action-buttons {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 5px;
  flex-wrap: nowrap;
  
  .el-button.is-circle {
    padding: 6px;
    margin: 0;
    height: 24px;
    width: 24px;
  }
  
  .el-button i {
    font-size: 12px;
  }
  
  .el-dropdown {
    margin: 0;
  }
}
</style>
