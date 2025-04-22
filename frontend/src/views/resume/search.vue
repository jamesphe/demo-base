<template>
  <basic-view title="简历检索">
    <div class="search-container">
      <!-- 快速筛选区 -->
      <div class="quick-search">
        <el-form :inline="true" :model="searchForm" size="small">
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.keyword"
              placeholder="姓名/技能/公司/职位"
              style="width: 200px;"
            />
          </el-form-item>
          <el-form-item label="工作年限">
            <el-select v-model="searchForm.experience" placeholder="不限" style="width: 120px;">
              <el-option label="不限" value="" />
              <el-option label="应届生" value="0" />
              <el-option label="1-3年" value="1-3" />
              <el-option label="3-5年" value="3-5" />
              <el-option label="5-10年" value="5-10" />
              <el-option label="10年以上" value="10+" />
            </el-select>
          </el-form-item>
          <el-form-item label="学历">
            <el-select v-model="searchForm.education" placeholder="不限" style="width: 120px;">
              <el-option label="不限" value="" />
              <el-option label="大专" value="college" />
              <el-option label="本科" value="bachelor" />
              <el-option label="硕士" value="master" />
              <el-option label="博士" value="doctor" />
            </el-select>
          </el-form-item>
          <el-form-item label="期望城市">
            <el-select
              v-model="searchForm.expectedLocation"
              filterable
              allow-create
              placeholder="请选择或输入"
              style="width: 160px;"
            >
              <el-option label="不限" value="" />
              <el-option label="北京" value="北京" />
              <el-option label="上海" value="上海" />
              <el-option label="广州" value="广州" />
              <el-option label="深圳" value="深圳" />
              <el-option label="杭州" value="杭州" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <i class="el-icon-search" />搜索
            </el-button>
            <el-button @click="resetForm">
              <i class="el-icon-refresh" />重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 高级筛选面板 -->
      <div class="search-panel">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item name="advanced">
            <template slot="title">
              <div class="collapse-header">
                <div class="header-left">
                  <i class="el-icon-arrow-right" />
                  <span class="title">高级筛选</span>
                  <el-tag size="small" type="info" class="condition-count">已选 {{ selectedConditionCount }} 项</el-tag>
                </div>
                <div class="header-right">
                  <el-button type="text" class="reset-btn" @click.stop="resetAdvancedForm">
                    <i class="el-icon-refresh" />重置高级条件
                  </el-button>
                </div>
              </div>
            </template>

            <el-form ref="searchForm" :model="searchForm" label-width="90px" size="small" class="search-form">
              <!-- 基础信息 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-user" />
                  </div>
                  <span class="header-title">基础信息</span>
                </div>
                <div class="section-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="年龄范围">
                        <el-input-number v-model="searchForm.minAge" :min="16" :max="100" size="small" class="age-input" placeholder="最小" />
                        <span class="separator">-</span>
                        <el-input-number v-model="searchForm.maxAge" :min="16" :max="100" size="small" class="age-input" placeholder="最大" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="性别">
                        <el-radio-group v-model="searchForm.gender">
                          <el-radio label="">不限</el-radio>
                          <el-radio label="M">男</el-radio>
                          <el-radio label="F">女</el-radio>
                        </el-radio-group>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="政治面貌">
                        <el-select v-model="searchForm.political" placeholder="不限" clearable>
                          <el-option label="不限" value="" />
                          <el-option label="中共党员" value="党员" />
                          <el-option label="共青团员" value="团员" />
                          <el-option label="群众" value="群众" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <!-- 教育背景 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-reading" />
                  </div>
                  <span class="header-title">教育背景</span>
                </div>
                <div class="section-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="毕业院校">
                        <el-input v-model="searchForm.school" placeholder="输入学校名称" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="专业">
                        <el-input v-model="searchForm.major" placeholder="输入专业名称" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <!-- 工作经验 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-office-building" />
                  </div>
                  <span class="header-title">工作经验</span>
                </div>
                <div class="section-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="当前职位">
                        <el-input v-model="searchForm.currentPosition" placeholder="输入职位" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="所在行业">
                        <el-input v-model="searchForm.industry" placeholder="输入行业" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <!-- 求职意向 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-aim" />
                  </div>
                  <span class="header-title">求职意向</span>
                </div>
                <div class="section-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="期望职位">
                        <el-input v-model="searchForm.expectedPosition" placeholder="输入职位" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="期望行业">
                        <el-input v-model="searchForm.expectedIndustry" placeholder="输入行业" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="期望薪资">
                        <el-input-number v-model="searchForm.minSalary" :min="0" size="small" class="salary-input" placeholder="最低" />
                        <span class="separator">-</span>
                        <el-input-number v-model="searchForm.maxSalary" :min="0" size="small" class="salary-input" placeholder="最高" />
                        <span class="unit">K</span>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="求职状态">
                        <el-select v-model="searchForm.jobStatus" placeholder="不限" clearable>
                          <el-option label="不限" value="" />
                          <el-option label="在职看机会" value="looking" />
                          <el-option label="离职待业" value="available" />
                          <el-option label="暂不找工作" value="unavailable" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <!-- 技能与资质 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-medal" />
                  </div>
                  <span class="header-title">技能与资质</span>
                </div>
                <div class="section-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item label="专业技能">
                        <el-select
                          v-model="searchForm.skills"
                          multiple
                          filterable
                          allow-create
                          default-first-option
                          placeholder="请选择或输入"
                          class="skill-select"
                        >
                          <el-option
                            v-for="item in skillOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="语言能力">
                        <el-select
                          v-model="searchForm.languages"
                          multiple
                          filterable
                          placeholder="请选择语言"
                        >
                          <el-option label="英语" value="english" />
                          <el-option label="日语" value="japanese" />
                          <el-option label="韩语" value="korean" />
                          <el-option label="法语" value="french" />
                          <el-option label="德语" value="german" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="证书">
                        <el-select
                          v-model="searchForm.certificates"
                          multiple
                          filterable
                          allow-create
                          default-first-option
                          placeholder="请选择或输入"
                        >
                          <el-option label="CPA" value="cpa" />
                          <el-option label="法律职业资格" value="legal" />
                          <el-option label="教师资格" value="teacher" />
                          <el-option label="注册建筑师" value="architect" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </div>

              <!-- 额外要求 -->
              <div class="search-section">
                <div class="section-header">
                  <div class="header-icon">
                    <i class="el-icon-more" />
                  </div>
                  <span class="header-title">额外要求</span>
                </div>
                <div class="section-content">
                  <el-form-item>
                    <el-input
                      v-model="searchForm.additionalRequirements"
                      type="textarea"
                      :rows="3"
                      placeholder="请输入其他额外要求，将通过智能匹配方式查找符合要求的简历..."
                    />
                  </el-form-item>
                </div>
              </div>

              <!-- 高级筛选按钮区 -->
              <div class="advanced-actions">
                <el-button type="text" @click="resetAdvancedForm">
                  <i class="el-icon-refresh" />重置高级条件
                </el-button>
                <el-button type="primary" @click="handleSearch">
                  <i class="el-icon-search" />开始筛查
                </el-button>
              </div>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 搜索结果 -->
      <div v-loading="loading" class="search-result">
        <div class="result-header">
          <span class="result-count">共找到 {{ total }} 份简历</span>
          <div class="view-controls">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="list">列表视图</el-radio-button>
              <el-radio-button label="card">卡片视图</el-radio-button>
            </el-radio-group>
            <el-select v-model="sortBy" size="small" style="margin-left: 10px">
              <el-option label="更新时间" value="updateTime" />
              <el-option label="相关度" value="relevance" />
              <el-option label="工作年限" value="experience" />
            </el-select>
          </div>
        </div>

        <!-- 列表视图 -->
        <template v-if="viewMode === 'list'">
          <el-table :data="resultList" style="width: 100%" :border="true" class="resume-table">
            <el-table-column label="候选人信息" min-width="240">
              <template slot-scope="{row}">
                <div class="candidate-info">
                  <div class="primary-info">
                    <div class="name-status">
                      <el-button type="text" class="name-button" @click="viewDetail(row)">
                        {{ row.name }}
                      </el-button>
                      <el-tag
                        size="small"
                        :type="getStatusType(row.status)"
                        effect="dark"
                        class="status-tag"
                      >
                        {{ getStatusText(row.status) }}
                      </el-tag>
                    </div>
                    <div class="tags">
                      <el-tag size="mini" :type="row.gender === 'F' ? 'danger' : 'primary'" class="gender-tag">
                        {{ row.gender === 'F' ? '女' : '男' }}
                      </el-tag>
                      <el-tag size="mini" type="success">{{ row.age }}岁</el-tag>
                      <el-tag size="mini" type="warning">{{ row.education }}</el-tag>
                    </div>
                  </div>
                  <div class="contact-info">
                    <i class="el-icon-phone" />{{ row.phone || '未提供' }}
                  </div>
                  <div class="contact-info">
                    <i class="el-icon-message" />{{ row.email || '未提供' }}
                  </div>
                  <div class="location-info">
                    <i class="el-icon-location" />{{ row.currentCity || '未提供' }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="工作经历" min-width="240">
              <template slot-scope="{row}">
                <div class="work-info">
                  <div class="current-job">
                    <span class="company">{{ row.currentCompany || '未提供' }}</span>
                    <span class="position">{{ row.currentPosition || '未提供' }}</span>
                  </div>
                  <div class="experience-tags">
                    <el-tag size="mini" type="info">{{ row.experience }}年经验</el-tag>
                    <el-tag size="mini" type="info">{{ row.currentSalary || '薪资未知' }}</el-tag>
                  </div>
                  <div v-if="row.skills && row.skills.length" class="skills">
                    <el-tag
                      v-for="skill in row.skills.slice(0, 3)"
                      :key="skill.name"
                      size="mini"
                      type="success"
                      class="skill-tag"
                    >
                      {{ skill.name }}
                    </el-tag>
                    <el-tag v-if="row.skills.length > 3" size="mini" type="info">
                      +{{ row.skills.length - 3 }}
                    </el-tag>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="求职意向" min-width="240">
              <template slot-scope="{row}">
                <div class="intention-info">
                  <div class="intention-main">
                    <div class="expected-job">
                      <i class="el-icon-aim" />
                      <span class="label">期望职位：</span>
                      <span class="value">{{ row.expectedPosition || '未提供' }}</span>
                    </div>
                    <div class="expected-location">
                      <i class="el-icon-map-location" />
                      <span class="label">期望城市：</span>
                      <span class="value">{{ row.expectedLocation || '未提供' }}</span>
                    </div>
                    <div class="expected-salary">
                      <i class="el-icon-money" />
                      <span class="label">期望薪资：</span>
                      <span class="value highlight">{{ row.expectedSalary || '未提供' }}</span>
                    </div>
                  </div>
                  <div class="status-info">
                    <el-tag
                      :type="row.status === 'pending' ? 'success' : 'warning'"
                      size="mini"
                      effect="dark"
                    >
                      {{ row.status === 'pending' ? '随时到岗' : row.status }}
                    </el-tag>
                    <span class="update-time">更新：{{ formatDate(row.updateTime) }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150" fixed="right">
              <template slot-scope="{row}">
                <div class="action-column">
                  <div class="action-buttons">
                    <el-tooltip content="查看简历" placement="top" effect="light">
                      <el-button type="primary" size="mini" plain circle @click="viewDetail(row)">
                        <i class="el-icon-view" />
                      </el-button>
                    </el-tooltip>

                    <el-tooltip content="预览原件" placement="top" effect="light">
                      <el-button type="warning" size="mini" plain circle @click="previewOriginalResume(row)">
                        <i class="el-icon-document" />
                      </el-button>
                    </el-tooltip>

                    <el-tooltip content="下载简历" placement="top" effect="light">
                      <el-button type="info" size="mini" plain circle @click="handleDownload(row)">
                        <i class="el-icon-download" />
                      </el-button>
                    </el-tooltip>

                    <el-tooltip :content="row.starred ? '取消收藏' : '收藏简历'" placement="top" effect="light">
                      <el-button
                        :type="row.starred ? 'warning' : 'info'"
                        size="mini"
                        plain
                        circle
                        @click="toggleStar(row)"
                      >
                        <i :class="row.starred ? 'el-icon-star-on' : 'el-icon-star-off'" />
                      </el-button>
                    </el-tooltip>
                  </div>
                  <div class="action-buttons" style="margin-top: 6px;">
                    <el-tooltip content="发送面试邀请" placement="top" effect="light">
                      <el-button type="success" size="mini" circle @click="sendInterviewInvite(row)">
                        <i class="el-icon-message" />
                      </el-button>
                    </el-tooltip>

                    <el-dropdown trigger="hover" @command="handleMoreActions($event, row)">
                      <el-button type="primary" size="mini" circle>
                        <i class="el-icon-more" />
                      </el-button>
                      <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item command="addToPool">
                          <i class="el-icon-folder-add" />加入人才库
                        </el-dropdown-item>
                        <el-dropdown-item command="addNote">
                          <i class="el-icon-edit-outline" />添加备注
                        </el-dropdown-item>
                        <el-dropdown-item command="sendEmail">
                          <i class="el-icon-message" />发送邮件
                        </el-dropdown-item>
                        <el-dropdown-item command="reject" divided>
                          <i class="el-icon-close" />不合适
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 卡片视图 -->
        <template v-else>
          <div class="resume-cards">
            <div v-for="item in resultList" :key="item.id" class="resume-card">
              <div class="card-header">
                <div class="header-left">
                  <span class="name" @click="viewDetail(item)">{{ item.name }}</span>
                  <span :class="['gender-tag', item.gender === 'F' ? 'female' : 'male']">
                    {{ item.gender === 'F' ? '女' : '男' }}
                  </span>
                  <span class="age-tag">{{ item.age }}岁</span>
                  <el-tag size="mini" :type="getStatusType(item.status)" effect="dark" class="status-mini-tag">
                    {{ getStatusText(item.status) }}
                  </el-tag>
                </div>
                <div class="header-right">
                  <span class="education-tag">{{ item.education }}</span>
                </div>
              </div>
              
              <div class="card-content">
                <div class="content-section">
                  <div class="section-title">
                    <i class="el-icon-office-building" />当前工作
                  </div>
                  <div class="company-info">
                    <div class="company">{{ item.currentCompany || '未提供' }}</div>
                    <div class="position">{{ item.currentPosition || '未提供' }}</div>
                  </div>
                  <div class="work-info">
                    <span><i class="el-icon-time" />{{ item.experience }}年经验</span>
                    <span><i class="el-icon-money" />{{ item.currentSalary || '未提供' }}</span>
                  </div>
                </div>
                
                <div class="content-section">
                  <div class="section-title">
                    <i class="el-icon-aim" />求职意向
                  </div>
                  <div class="intention-info">
                    <div class="info-item">
                      <i class="el-icon-user" />
                      {{ item.expectedPosition || '未提供' }}
                    </div>
                    <div class="info-item">
                      <i class="el-icon-location" />
                      {{ item.expectedLocation || '未提供' }}
                    </div>
                    <div class="info-item">
                      <i class="el-icon-money" />
                      {{ item.expectedSalary || '未提供' }}
                    </div>
                  </div>
                </div>
                
                <div class="contact-info">
                  <div class="contact-item">
                    <i class="el-icon-phone" />{{ item.phone || '未提供' }}
                  </div>
                  <div class="contact-item">
                    <i class="el-icon-message" />{{ item.email || '未提供' }}
                  </div>
                </div>
                
                <div class="status-bar">
                  <span class="update-time">更新于：{{ formatDate(item.updateTime) }}</span>
                  <span v-if="item.tags && item.tags.length > 0" class="candidate-tags">
                    <el-tag v-for="tag in item.tags.slice(0, 2)" :key="tag" size="mini" type="info">{{ tag }}</el-tag>
                  </span>
                </div>
              </div>
              
              <div class="card-footer">
                <el-tooltip content="查看详情" placement="top">
                  <el-button type="text" @click="viewDetail(item)">
                    <i class="el-icon-view" />
                  </el-button>
                </el-tooltip>
                
                <el-tooltip content="预览原件" placement="top">
                  <el-button type="text" @click="previewOriginalResume(item)">
                    <i class="el-icon-document" />
                  </el-button>
                </el-tooltip>
                
                <el-tooltip content="下载简历" placement="top">
                  <el-button type="text" @click="handleDownload(item)">
                    <i class="el-icon-download" />
                  </el-button>
                </el-tooltip>
                
                <el-tooltip :content="item.starred ? '取消收藏' : '收藏'" placement="top">
                  <el-button
                    type="text"
                    :class="{'starred': item.starred}"
                    @click="toggleStar(item)"
                  >
                    <i :class="item.starred ? 'el-icon-star-on' : 'el-icon-star-off'" />
                  </el-button>
                </el-tooltip>
                
                <el-tooltip content="更多操作" placement="top">
                  <el-dropdown trigger="click" @command="handleMoreActions($event, item)">
                    <el-button type="text">
                      <i class="el-icon-more" />
                    </el-button>
                    <el-dropdown-menu slot="dropdown">
                      <el-dropdown-item command="sendInterviewInvite">
                        <i class="el-icon-message" />发送面试邀请
                      </el-dropdown-item>
                      <el-dropdown-item command="addToPool">
                        <i class="el-icon-folder-add" />加入人才库
                      </el-dropdown-item>
                      <el-dropdown-item command="addNote">
                        <i class="el-icon-edit-outline" />添加备注
                      </el-dropdown-item>
                      <el-dropdown-item command="sendEmail">
                        <i class="el-icon-message" />发送邮件
                      </el-dropdown-item>
                      <el-dropdown-item command="reject" divided>
                        <i class="el-icon-close" />不合适
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </el-dropdown>
                </el-tooltip>
              </div>
            </div>
          </div>
        </template>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            :current-page="page.current"
            :page-sizes="[12, 24, 36, 48]"
            :page-size="page.size"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>

      <!-- 简历详情对话框 -->
      <el-dialog
        title="简历详情"
        :visible.sync="detailVisible"
        width="70%"
        :before-close="handleDetailClose"
        custom-class="resume-detail-dialog"
      >
        <resume-detail
          :detail="currentDetail"
          :loading="detailLoading"
        />
      </el-dialog>

      <!-- 原始简历预览对话框 -->
      <resume-preview
        :visible.sync="previewVisible"
        :resume-id="currentResumeId"
        :file-name="currentFileName"
        @close="handlePreviewClose"
      />
    </div>
  </basic-view>
</template>

<script>
import BasicView from '@/components/BasicView'
import ResumeDetail from '@/components/ResumeDetail'
import ResumePreview from '@/components/ResumePreview'
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'ResumeSearch',
  components: {
    BasicView,
    ResumeDetail,
    ResumePreview
  },
  data() {
    return {
      activeCollapse: [],
      searchForm: {
        minAge: null,
        maxAge: null,
        gender: '',
        political: '',
        education: '',
        school: '',
        major: '',
        experience: '',
        currentPosition: '',
        industry: '',
        expectedPosition: '',
        expectedIndustry: '',
        expectedLocation: '',
        minSalary: null,
        maxSalary: null,
        jobStatus: '',
        currentLocation: '',
        skills: [],
        languages: [],
        certificates: [],
        additionalRequirements: ''
      },
      skillOptions: [
        { value: 'java', label: 'Java' },
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' },
        { value: 'vue', label: 'Vue.js' },
        { value: 'react', label: 'React' },
        { value: 'node', label: 'Node.js' }
      ],
      viewMode: 'list',
      sortBy: 'updateTime',
      page: {
        current: 1,
        size: 12
      },
      detailVisible: false,
      previewVisible: false,
      currentResumeId: null,
      currentFileName: ''
    }
  },
  computed: {
    ...mapState('resume', ['loading']),
    ...mapGetters('resume', [
      'searchResult',
      'detailLoading',
      'currentDetail'
    ]),
    resultList() {
      return this.searchResult.items
    },
    total() {
      return this.searchResult.total
    },
    selectedConditionCount() {
      let count = 0
      const form = this.searchForm

      // 计算已选条件数量
      if (form.minAge || form.maxAge) count++
      if (form.gender) count++
      if (form.political) count++
      if (form.education) count++
      if (form.school) count++
      if (form.major) count++
      if (form.experience) count++
      if (form.currentPosition) count++
      if (form.industry) count++
      if (form.expectedPosition) count++
      if (form.expectedIndustry) count++
      if (form.expectedLocation) count++
      if (form.minSalary || form.maxSalary) count++
      if (form.jobStatus) count++
      if (form.currentLocation) count++
      if (form.skills && form.skills.length) count++
      if (form.languages && form.languages.length) count++
      if (form.certificates && form.certificates.length) count++
      if (form.additionalRequirements) count++

      return count
    }
  },
  created() {
    console.log('ResumeSearch组件已创建')
    this.handleSearch()
  },
  methods: {
    ...mapActions('resume', [
      'searchResumes',
      'downloadResume',
      'toggleResumeStar',
      'exportSearchResult',
      'getResumeDetail'
    ]),

    // 搜索
    async handleSearch() {
      console.log('开始执行搜索，当前页码:', this.page.current, '每页数量:', this.page.size)
      try {
        const params = {
          page: this.page.current,
          pageSize: this.page.size,
          keyword: this.searchForm.keyword,
          experience: this.searchForm.experience,
          education: this.searchForm.education,
          skills: this.searchForm.skills.join(','),
          source: this.searchForm.source,
          sort: this.sortBy,
          expectedLocation: this.searchForm.expectedLocation
        }
        // 处理日期范围
        if (this.searchForm.updateTime && this.searchForm.updateTime.length === 2) {
          params.start_date = this.searchForm.updateTime[0]
          params.end_date = this.searchForm.updateTime[1]
        }

        console.log('搜索参数:', params)
        await this.searchResumes(params)
        console.log('搜索完成，结果数量:', this.resultList.length)
      } catch (error) {
        console.error('搜索失败:', error)
        this.$message.error('搜索失败，请稍后重试')
      }
    },

    // 重置表单
    resetForm() {
      this.$refs.searchForm.resetFields()
      this.handleSearch()
    },

    // 重置高级筛选条件
    resetAdvancedForm() {
      // 保留快速筛选区的值
      const quickSearchValues = {
        keyword: this.searchForm.keyword,
        experience: this.searchForm.experience,
        education: this.searchForm.education,
        expectedLocation: this.searchForm.expectedLocation
      }
      // 重置整个表单
      this.$refs.searchForm.resetFields()
      // 恢复快速筛选区的值
      Object.assign(this.searchForm, quickSearchValues)
    },

    // 导出结果
    async handleExport() {
      try {
        const params = {
          keyword: this.searchForm.keyword,
          experience: this.searchForm.experience,
          education: this.searchForm.education,
          skills: this.searchForm.skills.join(','),
          source: this.searchForm.source,
          sort: this.sortBy
        }
        // 处理日期范围
        if (this.searchForm.updateTime && this.searchForm.updateTime.length === 2) {
          params.start_date = this.searchForm.updateTime[0]
          params.end_date = this.searchForm.updateTime[1]
        }

        await this.exportSearchResult(params)
        this.$message.success('导出成功')
      } catch (error) {
        this.$message.error('导出失败，请稍后重试')
      }
    },

    // 查看详情
    async viewDetail(row) {
      console.log('开始获取简历详情，行数据：', row)
      this.detailVisible = true
      try {
        const detail = await this.getResumeDetail(row.id)
        console.log('获取简历详情成功，当前详情数据：', detail)

        // 检查数据是否有效
        if (!detail) {
          throw new Error('获取简历详情失败：数据为空')
        }
      } catch (error) {
        console.error('获取简历详情失败:', error)
        this.$message.error('获取简历详情失败，请稍后重试')
        this.detailVisible = false
      }
    },

    // 关闭详情
    handleDetailClose() {
      console.log('关闭简历详情对话框')
      this.detailVisible = false
      // 清空当前详情数据
      this.$store.commit('resume/SET_CURRENT_DETAIL', null)
    },

    // 下载简历
    async handleDownload(row) {
      try {
        await this.downloadResume({ id: row.id, fileName: row.fileName })
        this.$message.success('下载成功')
      } catch (error) {
        this.$message.error('下载失败，请稍后重试')
      }
    },

    // 收藏/取消收藏
    async toggleStar(row) {
      try {
        await this.toggleResumeStar({ id: row.id, starred: !row.starred })
        this.$message.success(row.starred ? '已收藏' : '已取消收藏')
      } catch (error) {
        this.$message.error('操作失败，请稍后重试')
      }
    },

    // 格式化日期
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },

    // 分页大小改变
    handleSizeChange(val) {
      this.page.size = val
      this.handleSearch()
    },

    // 当前页改变
    handleCurrentChange(val) {
      this.page.current = val
      this.handleSearch()
    },

    // 根据技能等级返回标签类型
    getSkillTagType(level) {
      switch (level) {
        case '精通':
          return 'success'
        case '熟练':
          return 'primary'
        case '良好':
          return 'warning'
        case '一般':
          return 'info'
        default:
          return ''
      }
    },

    handleMoreActions(command, row) {
      switch (command) {
        case 'addToPool':
          this.addToTalentPool(row)
          break
        case 'addNote':
          this.addNote(row)
          break
        case 'sendEmail':
          this.sendEmail(row)
          break
        case 'reject':
          this.rejectCandidate(row)
          break
      }
    },

    // 根据状态返回标签类型
    getStatusType(status) {
      const statusMap = {
        pending: 'success',
        invited: 'warning',
        interviewed: 'primary', 
        rejected: 'danger',
        hired: 'info'
      }
      return statusMap[status] || 'info'
    },

    getStatusText(status) {
      const textMap = {
        pending: '待处理',
        invited: '已邀约',
        interviewed: '已面试',
        rejected: '不合适',
        hired: '已录用'
      }
      return textMap[status] || status
    },

    sendEmail(row) {
      this.$message({
        message: '邮件发送功能开发中...',
        type: 'info'
      })
    },

    rejectCandidate(row) {
      this.$confirm('确定将该候选人标记为"不合适"吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: 调用API更新状态
        this.$message({
          type: 'success',
          message: '已标记为不合适'
        })
      }).catch(() => {})
    },

    addNote(row) {
      this.$prompt('请输入备注内容', '添加备注', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入备注信息...'
      }).then(({ value }) => {
        this.$message({
          type: 'success',
          message: '备注已添加'
        })
      }).catch(() => {})
    },

    // 预览原始简历
    previewOriginalResume(row) {
      console.log('预览原始简历:', row)
      this.currentResumeId = row.id
      this.currentFileName = row.fileName || ''
      this.previewVisible = true
    },

    // 关闭预览
    handlePreviewClose() {
      this.previewVisible = false
      this.currentResumeId = null
      this.currentFileName = ''
    },

    tableSpanMethod({ row, column, rowIndex, columnIndex }) {
      // 这个方法可以用来控制表格单元格的合并
      // 这里返回默认值，不做特殊处理
      return {
        rowspan: 1,
        colspan: 1
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.search-container {
  padding: 20px;
  background-color: #f5f7fa;

  .quick-search {
    background-color: #fff;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);

    :deep(.el-form--inline) {
      .el-form-item {
        margin-right: 16px;
        margin-bottom: 0;

        &:last-child {
          margin-right: 0;
        }

        .el-form-item__label {
          color: #606266;
        }
      }
    }
  }

  .search-panel {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 20px;
    overflow: hidden;

    .collapse-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        i {
          font-size: 16px;
          color: #409EFF;
          transition: transform 0.3s;
        }

        .title {
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }

        .condition-count {
          font-size: 12px;
          padding: 2px 8px;
          border-radius: 4px;
          background-color: #f3f4f6;
          color: #6b7280;
          border: none;
        }
      }

      .header-right {
        .reset-btn {
          font-size: 13px;
          color: #6b7280;
          padding: 4px 12px;
          border-radius: 4px;
          transition: all 0.3s;

          &:hover {
            color: #409EFF;
            background-color: #ecf5ff;
          }

          i {
            margin-right: 4px;
            font-size: 14px;
          }
        }
      }
    }

    :deep(.el-collapse-item__header) {
      padding: 16px 24px;
      font-weight: 500;
      border-bottom: 1px solid #e5e7eb;

      &.is-active {
        .el-icon-arrow-right {
          transform: rotate(90deg);
        }
      }
    }

    .search-form {
      padding: 24px;

      .search-section {
        background-color: #f9fafb;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;

        &:last-of-type {
          margin-bottom: 0;
        }

        .section-header {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px dashed #e5e7eb;

          .header-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            margin-right: 8px;

            i {
              font-size: 16px;
            }
          }

          .header-title {
            font-size: 14px;
          }
        }

        .section-content {
          .el-row {
            margin-bottom: 12px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .el-form-item {
            margin-bottom: 0;

            :deep(.el-form-item__label) {
              padding-right: 8px;
              line-height: 32px;
            }

            :deep(.el-input__inner),
            :deep(.el-select .el-input__inner) {
              height: 32px;
              line-height: 32px;
            }

            :deep(.el-input-number) {
              line-height: 30px;
            }
          }
        }
      }

      .advanced-actions {
        padding: 16px;
        text-align: right;
        border-top: 1px solid #e5e7eb;
        margin-top: 16px;
        display: flex;
        justify-content: flex-end;
        gap: 12px;

        .el-button {
          &[type="text"] {
            margin-right: auto;
          }

          &[type="primary"] {
            min-width: 120px;
          }
        }
      }
    }
  }

  // 结果区域样式
  .result-header {
    background-color: #fff;
    padding: 16px 24px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

    .result-count {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }

    .view-controls {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }

  // 表格样式优化
  :deep(.el-table) {
    background-color: #fff;
    border-radius: 0 0 8px 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    table-layout: fixed;

    &::before {
      display: none;
    }

    :deep(.el-table__header) {
      th {
        background-color: #f5f7fa;
        color: #606266;
        font-weight: 600;
        padding: 10px 0;
      }
    }

    :deep(.el-table__body) {
      td {
        padding: 16px 8px;
      }
    }

    .el-table__body-wrapper {
      .el-table__row {
        td {
          padding: 16px 8px;
          transition: background-color 0.3s;
        }

        &:hover td {
          background-color: #f5f7fa;
        }
      }
    }

    // 单元格内容样式
    .cell {
      padding: 0 12px;
      line-height: 1.6;
    }
  }

  // 内容区块样式
  .basic-info,
  .work-info,
  .intention-info,
  .contact-info {
    .info-row {
      display: flex;
      align-items: center;
      margin-bottom: 8px;

      &:last-child {
        margin-bottom: 0;
      }

      .label {
        color: #909399;
        margin-right: 8px;
        font-size: 13px;
      }

      .value {
        color: #606266;
        font-size: 13px;
      }
    }
  }

  // 操作按钮样式
  .action-column {
    .action-buttons {
      display: flex;
      align-items: center;
      gap: 6px;
      justify-content: center;
      flex-wrap: wrap;

      .el-button {
        margin: 0;
        padding: 6px;
      }
    }
  }

  // 分页器样式
  .pagination-container {
    margin-top: 20px;
    padding: 16px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    display: flex;
    justify-content: flex-end;
  }

  // 卡片视图样式优化
  .resume-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 16px;
  }

  .resume-card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    height: 100%;

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
      border-color: #e6f2ff;
    }

    .card-header {
      padding: 14px 16px;
      border-bottom: 1px solid #f0f2f5;
      background: #f9fafc;
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;

        .name {
          font-size: 18px;
          font-weight: 600;
          color: #303133;
          cursor: pointer;
          transition: color 0.2s;
          max-width: 120px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;

          &:hover {
            color: #409EFF;
          }
        }

        .gender-tag {
          padding: 2px 8px;
          font-size: 13px;
          border-radius: 4px;
          line-height: 1.5;

          &.male {
            background-color: #e1f3ff;
            color: #409EFF;
          }

          &.female {
            background-color: #fde2e2;
            color: #f56c6c;
          }
        }

        .age-tag {
          padding: 2px 8px;
          font-size: 13px;
          background-color: #f0f2f5;
          color: #606266;
          border-radius: 4px;
          line-height: 1.5;
        }
      }

      .header-right {
        .education-tag {
          padding: 2px 8px;
          font-size: 13px;
          background-color: #f0f9eb;
          color: #67c23a;
          border-radius: 4px;
          font-weight: 500;
        }
      }
    }

    .card-content {
      padding: 14px 16px;
      flex: 1;
      display: flex;
      flex-direction: column;

      .content-section {
        margin-bottom: 12px;
        position: relative;

        &:last-child {
          margin-bottom: 0;
        }

        .section-title {
          font-size: 15px;
          font-weight: 600;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          font-weight: 500;

          i {
            margin-right: 4px;
            font-size: 16px;
            color: #909399;
          }
        }

        .company-info {
          margin-bottom: 6px;

          .company {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 2px;
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .position {
            color: #606266;
            font-size: 14px;
            display: block;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
        }

        .work-info {
          display: flex;
          align-items: center;
          gap: 12px;
          color: #909399;
          font-size: 14px;

          span {
            display: flex;
            align-items: center;

            i {
              margin-right: 4px;
              font-size: 16px;
            }
          }
        }

        .intention-info {
          display: grid;
          grid-template-columns: repeat(1, 1fr);
          gap: 6px;

          .info-item {
            display: flex;
            align-items: center;
            font-size: 14px;
            color: #606266;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;

            i {
              margin-right: 4px;
              color: #909399;
              font-size: 16px;
              flex-shrink: 0;
            }
          }
        }
      }

      .contact-info {
        display: flex;
        justify-content: space-between;
        padding-top: 12px;
        margin-top: 12px;
        border-top: 1px dashed #ebeef5;

        .contact-item {
          display: flex;
          align-items: center;
          font-size: 14px;
          color: #606266;
          max-width: 45%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;

          i {
            margin-right: 4px;
            color: #909399;
            font-size: 16px;
            flex-shrink: 0;
          }
        }
      }

      .status-bar {
        margin-top: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;

        .update-time {
          font-size: 13px;
          color: #909399;
        }

        .status-tag {
          font-size: 13px;
          font-weight: 500; 
          padding: 1px 8px;
          border-radius: 4px;
          line-height: 1.5;
        }

        .status-ready {
          background-color: #f0f9eb;
          color: #67c23a;
        }

        .status-processing {
          background-color: #ecf5ff;
          color: #409EFF;
        }
      }
    }

    .card-footer {
      padding: 10px 16px;
      border-top: 1px solid #f0f2f5;
      background: #f9fafc;
      display: flex;
      justify-content: space-around;
      gap: 8px;

      .el-button {
        padding: 0;
        font-size: 15px;
        min-width: fit-content;
        flex: 1;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;

        &.starred {
          color: #e6a23c;
        }

        i {
          margin-right: 4px;
          font-size: 16px;
        }
      }
    }
  }
}

.starred {
  color: #E6A23C !important;
}

.no-data {
  text-align: center;
  padding: 20px;
}

.resume-table {
  :deep(.el-table__row) {
    &:hover {
      background-color: #f5f7fa;
    }
  }

  :deep(.el-table__header) {
    th {
      background-color: #f5f7fa;
      color: #606266;
      font-weight: 600;
      padding: 10px 0;
    }
  }

  :deep(.el-table__body) {
    td {
      padding: 16px 8px;
    }
  }

  .candidate-info {
    .primary-info {
      .name-status {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;

        .name-button {
          font-size: 15px;
          font-weight: 600;
          color: #2c3e50;

          &:hover {
            color: #409EFF;
          }
        }

        .status-tag {
          font-weight: normal;
        }
      }

      .tags {
        display: flex;
        gap: 5px;
        margin-bottom: 10px;
      }
    }

    .contact-info, .location-info {
      font-size: 13px;
      color: #606266;
      margin-top: 5px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;

      i {
        margin-right: 5px;
        color: #909399;
      }
    }
  }

  .work-info {
    .current-job {
      margin-bottom: 8px;

      .company {
        font-weight: 500;
        color: #2c3e50;
        margin-right: 8px;
        display: block;
        margin-bottom: 4px;
      }

      .position {
        color: #606266;
        display: block;
      }
    }

    .experience-tags {
      margin-bottom: 10px;
      display: flex;
      gap: 5px;
    }

    .skills {
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-top: 8px;

      .skill-tag {
        background-color: #f0f9eb;
        color: #67c23a;
        border-color: #e1f3d8;
      }
    }
  }

  .intention-info {
    .intention-main {
      > div {
        margin-bottom: 8px;
        display: flex;
        align-items: center;

        i {
          color: #909399;
          margin-right: 5px;
          width: 14px;
        }

        .label {
          color: #909399;
          margin-right: 5px;
          min-width: 70px;
        }

        .value {
          color: #2c3e50;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;

          &.highlight {
            color: #f56c6c;
            font-weight: 500;
          }
        }
      }
    }

    .status-info {
      margin-top: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .update-time {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .action-column {
    .action-buttons {
      display: flex;
      align-items: center;
      gap: 6px;
      justify-content: center;
      flex-wrap: wrap;

      .el-button {
        margin: 0;
        padding: 6px;
      }
    }
  }
}

.resume-detail-dialog {
  :deep(.el-dialog__body) {
    padding: 20px 30px;
  }
}

.status-tag {
  margin-left: 8px;
  font-size: 12px;
  padding: 0 8px;
  height: 24px;
  line-height: 22px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.status-ready {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-processing {
  background-color: #ecf5ff;
  color: #409EFF;
}

.status-mini-tag {
  font-size: 13px;
  padding: 1px 8px;
  height: 22px;
  line-height: 20px;
}

.candidate-tags {
  display: flex;
  gap: 4px;
  
  .el-tag {
    background-color: #f5f7fa;
    color: #909399;
    border-color: #e4e7ed;
    font-size: 13px;
  }
}
</style>
