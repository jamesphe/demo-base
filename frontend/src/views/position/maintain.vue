<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <el-card class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="职位名称">
          <el-input
            v-model="listQuery.keyword"
            placeholder="请输入职位名称"
            clearable
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
        </el-form-item>
        <el-form-item label="职位类型">
          <el-select v-model="listQuery.type" placeholder="请选择" clearable class="filter-item">
            <el-option label="全职" value="fulltime">
              <span style="float: left">全职</span>
            </el-option>
            <el-option label="兼职" value="parttime">
              <span style="float: left">兼职</span>
            </el-option>
            <el-option label="实习" value="intern">
              <span style="float: left">实习</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="listQuery.status" placeholder="请选择" clearable class="filter-item">
            <el-option label="招聘中" value="active">
              <el-tag type="success">招聘中</el-tag>
            </el-option>
            <el-option label="已暂停" value="paused">
              <el-tag type="warning">已暂停</el-tag>
            </el-option>
            <el-option label="已结束" value="closed">
              <el-tag type="info">已结束</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleFilter">搜索</el-button>
          <el-button plain icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-container">
      <div slot="header" class="clearfix">
        <span class="card-title">职位列表</span>
        <el-button
          class="filter-item"
          style="float: right; margin-left: 10px"
          type="primary"
          icon="el-icon-plus"
          @click="handleCreate"
        >
          新增职位
        </el-button>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
        fit
        highlight-current-row
        style="width: 100%"
      >
        <el-table-column
          v-if="isAdmin"
          label="所属租户"
          width="150"
          align="center"
          show-overflow-tooltip
        >
          <template slot-scope="{row}">
            <el-tooltip
              :content="row.tenantId ? `租户ID: ${row.tenantId}` : ''"
              placement="top"
            >
              <el-tag size="mini" type="info">
                {{ row.tenantName || '-' }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column
          label="职位名称"
          prop="title"
          min-width="160"
          show-overflow-tooltip
        >
          <template slot-scope="{row}">
            <el-link type="primary" @click="handleEdit(row)">{{ row.title }}</el-link>
          </template>
        </el-table-column>

        <el-table-column
          label="部门"
          prop="department"
          width="110"
          align="center"
          show-overflow-tooltip
        />

        <el-table-column
          label="工作地点"
          prop="location"
          width="160"
          align="center"
          show-overflow-tooltip
        />

        <el-table-column
          label="职位类型"
          width="85"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag :type="row.jobType === 'fulltime' ? 'primary' : row.jobType === 'parttime' ? 'success' : 'warning'">
              {{ row.jobType === 'fulltime' ? '全职' : row.jobType === 'parttime' ? '兼职' : '实习' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="薪资范围"
          width="110"
          align="center"
        >
          <template slot-scope="{row}">
            <span class="salary-text">{{ row.salaryMin }}-{{ row.salaryMax }}K/{{ row.salaryType === '年薪' ? '年' : '月' }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="经验要求"
          width="90"
          align="center"
          show-overflow-tooltip
        >
          <template slot-scope="{row}">
            <span>{{ row.experienceRequired }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="学历要求"
          width="90"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag size="mini" type="info">
              {{ getEducationText(row.educationRequired) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="邮件同步"
          width="90"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag :type="row.emailSyncEnabled ? 'success' : 'info'" size="mini">
              {{ row.emailSyncEnabled ? '已开启' : '已关闭' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="接收邮箱"
          min-width="150"
          align="center"
          show-overflow-tooltip
        >
          <template slot-scope="{row}">
            <div v-if="row.emailSyncEnabled && row.receivingEmail">
              <el-tag size="mini" type="primary">{{ row.receivingEmail }}</el-tag>
              <div class="email-department">{{ getEmailDepartment(row.receivingEmail) }}</div>
              <div class="email-sync-time" v-if="getEmailLastSyncTime(row.receivingEmail)">
                <i class="el-icon-time"></i> 上次同步: {{ getEmailLastSyncTime(row.receivingEmail) }}
              </div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column
          label="筛选关键字"
          min-width="120"
          align="center"
          show-overflow-tooltip
        >
          <template slot-scope="{row}">
            <div v-if="getPositionKeywords(row).length > 0">
              <el-tag 
                size="mini" 
                type="warning" 
                v-for="(keyword, index) in getPositionKeywords(row)" 
                :key="index"
                class="keyword-list-tag"
                v-show="index < 3"
              >
                {{ keyword }}
              </el-tag>
              <el-tag size="mini" type="info" v-if="getPositionKeywords(row).length > 3">
                +{{ getPositionKeywords(row).length - 3 }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column
          label="状态"
          width="80"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column
          label="发布时间"
          width="135"
          align="center"
        >
          <template slot-scope="{row}">
            <span>{{ formatTime(row.createdAt) }}</span>
          </template>
        </el-table-column>

        <el-table-column
          label="操作"
          align="center"
          width="350"
          fixed="right"
        >
          <template slot-scope="{row}">
            <el-button-group>
              <el-button
                v-if="row.status !== 'closed'"
                size="mini"
                type="primary"
                icon="el-icon-edit"
                @click="handleEdit(row)"
              >
                编辑
              </el-button>
              <el-button
                v-if="row.status === 'active' || row.status === 'published'"
                size="mini"
                type="warning"
                icon="el-icon-video-pause"
                @click="handleUpdateStatus(row, 'paused')"
              >
                暂停
              </el-button>
              <el-button
                v-if="row.status === 'paused'"
                size="mini"
                type="success"
                icon="el-icon-video-play"
                @click="handleUpdateStatus(row, 'active')"
              >
                恢复
              </el-button>
              <el-button
                v-if="row.status !== 'closed'"
                size="mini"
                type="info"
                icon="el-icon-circle-close"
                @click="handleUpdateStatus(row, 'closed')"
              >
                结束
              </el-button>
              <el-button
                size="mini"
                type="danger"
                icon="el-icon-delete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        @pagination="getList"
      />
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="65%" @close="resetForm">
      <el-form ref="form" :model="positionForm" :rules="rules" label-width="120px" class="position-form">
        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>基本信息</span>
            <small class="text-muted">请填写职位基本信息</small>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="职位名称" prop="title">
                <el-input v-model="positionForm.title" placeholder="请输入职位名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位类型" prop="type">
                <el-select v-model="positionForm.type" placeholder="请选择职位类型" style="width: 100%">
                  <el-option label="全职" value="fulltime" />
                  <el-option label="兼职" value="parttime" />
                  <el-option label="实习" value="intern" />
                  <el-option label="外包" value="outsource" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="所属部门" prop="department">
                <el-input v-model="positionForm.department" placeholder="请输入所属部门" @change="onDepartmentChange" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="招聘人数" prop="headcount">
                <el-input-number v-model="positionForm.headcount" :min="1" :max="999" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="工作地点" prop="location">
            <el-input
              v-model="positionForm.location"
              placeholder="请输入工作地点，如: 北京市朝阳区望京SOHO"
              :maxlength="255"
              show-word-limit
            />
          </el-form-item>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>薪资福利</span>
            <small class="text-muted">请设置薪资范围和福利待遇</small>
          </div>

          <el-form-item label="薪资范围" prop="salary" class="salary-range">
            <el-col :span="8">
              <el-input-number
                v-model="positionForm.salaryMin"
                :min="1"
                :step="1"
                controls-position="right"
                placeholder="最低薪资"
              />
            </el-col>
            <el-col :span="1" class="salary-separator">
              <span>至</span>
            </el-col>
            <el-col :span="8">
              <el-input-number
                v-model="positionForm.salaryMax"
                :min="positionForm.salaryMin || 1"
                :step="1"
                controls-position="right"
                placeholder="最高薪资"
              />
            </el-col>
            <el-col :span="6" :offset="1">
              <el-select v-model="positionForm.salaryType" style="width: 100%">
                <el-option label="月薪" value="month" />
                <el-option label="年薪" value="year" />
                <el-option label="面议" value="negotiate" />
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="福利待遇" prop="benefits">
            <el-checkbox-group v-model="positionForm.benefits" class="benefit-group">
              <el-checkbox v-for="(label, value) in getBenefitMap()" :key="value" :label="value">
                {{ label }}
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>要求与职责</span>
            <small class="text-muted">请详细描述职位要求与职责</small>
          </div>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学历要求" prop="educationRequired">
                <el-select v-model="positionForm.educationRequired" style="width: 100%">
                  <el-option label="不限" value="none" />
                  <el-option label="大专" value="college" />
                  <el-option label="本科" value="bachelor" />
                  <el-option label="硕士" value="master" />
                  <el-option label="博士" value="phd" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="工作经验" prop="experienceRequired">
                <el-select v-model="positionForm.experienceRequired" style="width: 100%">
                  <el-option label="经验不限" value="none" />
                  <el-option label="应届生" value="fresh" />
                  <el-option label="1年以下" value="0-1" />
                  <el-option label="1-3年" value="1-3" />
                  <el-option label="3-5年" value="3-5" />
                  <el-option label="5-10年" value="5-10" />
                  <el-option label="10年以上" value="10+" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="职位描述" prop="description">
            <el-input
              v-model="positionForm.description"
              type="textarea"
              :rows="6"
              placeholder="请详细描述该职位的主要工作内容、职责范围等"
            />
          </el-form-item>

          <el-form-item label="任职要求" prop="requirements">
            <el-input
              v-model="positionForm.requirements"
              type="textarea"
              :rows="6"
              placeholder="请详细描述该职位的任职要求，如专业技能、语言要求、性格特征等"
            />
          </el-form-item>

          <el-form-item label="加分项" prop="preferences">
            <el-input
              v-model="positionForm.preferences"
              type="textarea"
              :rows="4"
              placeholder="请描述该职位的加分项，如特定技能、证书、项目经验等"
            />
          </el-form-item>
        </el-card>

        <el-card class="box-card">
          <div slot="header" class="card-header">
            <span>邮件设置</span>
            <small class="text-muted">设置接收简历的邮件规则</small>
            <el-button 
              v-if="isAdmin"
              type="text" 
              size="mini" 
              style="float: right; padding: 3px 0;" 
              @click="goToEmailSettings"
            >
              <i class="el-icon-setting"></i> 管理邮箱设置
            </el-button>
          </div>

          <el-form-item label="简历筛选关键字" prop="emailKeywords">
            <el-input
              v-model="keywordInput"
              placeholder="请输入关键字后按回车添加，多个关键字用逗号分隔"
              @keyup.enter.native="addKeyword"
              class="keyword-input"
            >
              <el-button slot="append" icon="el-icon-plus" @click="addKeyword">添加</el-button>
            </el-input>
            <div class="keyword-tags">
              <el-tag
                v-for="(tag, index) in keywordList"
                :key="index"
                closable
                @close="removeKeyword(index)"
                class="keyword-tag"
              >
                {{ tag }}
              </el-tag>
              <div v-if="keywordList.length === 0" class="no-keywords">
                暂无关键字，请添加
              </div>
            </div>
            <div class="form-tip">系统将自动筛选包含以上关键字的简历邮件，未包含关键字的邮件将被过滤</div>
          </el-form-item>

          <el-form-item label="邮箱同步设置" prop="emailSyncEnabled">
            <el-switch
              v-model="positionForm.emailSyncEnabled"
              active-text="开启邮箱同步"
              inactive-text="关闭邮箱同步"
              @change="handleSyncChange"
            />
            <div class="form-tip">
              开启后，系统会根据关键字定期从选定邮箱中筛选简历并自动同步到招聘系统中。
              <template v-if="isAdmin">如需配置更多邮箱，请前往<el-link type="primary" @click="goToEmailSettings">邮箱设置</el-link>页面。</template>
            </div>
          </el-form-item>

          <el-form-item label="接收邮箱" prop="receivingEmail" v-if="positionForm.emailSyncEnabled" :rules="emailRules.receivingEmail">
            <el-select 
              v-model="positionForm.receivingEmail" 
              placeholder="请选择接收简历的邮箱"
              style="width: 100%"
            >
              <el-option
                v-for="item in syncEmailOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              >
                <span style="float: left">{{ item.label }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ item.department }}</span>
              </el-option>
            </el-select>
            <div class="form-tip">
              <template v-if="syncEmailOptions.length === 0">
                <i class="el-icon-warning"></i> 未找到可用的同步邮箱，请先在系统设置中配置邮箱。
              </template>
              <template v-else>
                职位相关的简历将发送至此邮箱，请从系统已设置的同步邮箱中选择
              </template>
            </div>
            <div class="email-status" v-if="positionForm.receivingEmail">
              <el-alert
                :title="getEmailStatusTitle(positionForm.receivingEmail)"
                :type="getEmailStatusType(positionForm.receivingEmail)"
                :closable="false"
                size="mini"
                show-icon
              ></el-alert>
            </div>
          </el-form-item>
        </el-card>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleSavePosition">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'
import { mapState, mapActions } from 'vuex'

export default {
  name: 'PositionMaintain',
  components: { Pagination },
  filters: {
    parseTime
  },
  data() {
    return {
      listQuery: {
        page: 1,
        limit: 10,
        keyword: undefined,
        type: undefined,
        status: undefined
      },
      dialogVisible: false,
      dialogTitle: '',
      positionForm: {
        id: undefined,
        title: '',
        type: '',
        department: '',
        location: '',
        salaryMin: '',
        salaryMax: '',
        salaryType: 'month',
        description: '',
        requirements: '',
        preferences: '',
        experienceRequired: '',
        educationRequired: '',
        headcount: 1,
        benefits: [],
        emailKeywords: '',
        emailSyncEnabled: false,
        receivingEmail: ''
      },
      cityOptions: [
        {
          value: '北京',
          label: '北京',
          children: [
            { value: '朝阳区', label: '朝阳区' },
            { value: '海淀区', label: '海淀区' },
            { value: '东城区', label: '东城区' },
            { value: '西城区', label: '西城区' }
          ]
        },
        {
          value: '上海',
          label: '上海',
          children: [
            { value: '浦东新区', label: '浦东新区' },
            { value: '徐汇区', label: '徐汇区' },
            { value: '黄浦区', label: '黄浦区' }
          ]
        }
        // 可以继续添加更多城市
      ],
      rules: {
        title: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
        type: [{ required: true, message: '请选择职位类型', trigger: 'change' }],
        department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
        location: [{ required: true, message: '请输入工作地点', trigger: 'blur' }],
        description: [{ required: true, message: '请输入职位描述', trigger: 'blur' }],
        requirements: [{ required: true, message: '请输入任职要求', trigger: 'blur' }],
        experienceRequired: [{ required: true, message: '请选择工作经验', trigger: 'change' }],
        educationRequired: [{ required: true, message: '请选择学历要求', trigger: 'change' }],
        headcount: [{ required: true, message: '请输入招聘人数', trigger: 'blur' }],
        salaryMin: [{ required: true, message: '请输入最低薪资', trigger: 'blur' }],
        salaryMax: [{ required: true, message: '请输入最高薪资', trigger: 'blur' }]
      },
      emailRules: {
        receivingEmail: [
          { required: true, message: '请输入接收邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ]
      },
      isAdmin: false,
      keywordInput: '',
      keywordList: [],
      syncEmailOptions: [],
    }
  },
  computed: {
    ...mapState('position', {
      list: state => state.positions,
      total: state => state.total,
      listLoading: state => state.loading
    })
  },
  created() {
    this.isAdmin = this.$store.getters.roles.includes('admin')
    this.fetchList()
    this.fetchSyncEmailOptions()
  },
  methods: {
    ...mapActions('position', [
      'getList',
      'updatePosition',
      'deletePosition',
      'updatePositionStatus',
      'createPosition'
    ]),
    ...mapActions('resume-sync-email', [
      'getEmailList'
    ]),
    getStatusType(status) {
      const statusMap = {
        draft: 'info',
        published: 'success',
        active: 'success',
        paused: 'warning',
        closed: 'danger'
      }
      return statusMap[status] || 'info'
    },

    getStatusText(status) {
      const statusMap = {
        draft: '草稿',
        published: '招聘中',
        active: '招聘中',
        paused: '已暂停',
        closed: '已结束'
      }
      return statusMap[status] || '未知'
    },

    getEducationText(education) {
      const educationMap = {
        'bachelor': '本科',
        'master': '硕士',
        'phd': '博士',
        'college': '大专',
        'highschool': '高中',
        'other': '其他'
      }
      return educationMap[education.toLowerCase()] || education
    },

    formatTime(time) {
      if (!time) return ''
      
      try {
        // 尝试直接创建Date对象
        let date = new Date(time)
        
        // 检查是否为有效日期
        if (isNaN(date.getTime())) {
          console.warn('无效的时间格式:', time)
          return ''
        }

        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        const hour = String(date.getHours()).padStart(2, '0')
        const minute = String(date.getMinutes()).padStart(2, '0')
        const second = String(date.getSeconds()).padStart(2, '0')

        return `${year}-${month}-${day} ${hour}:${minute}:${second}`
      } catch (error) {
        console.error('时间格式化失败:', error)
        return ''
      }
    },

    handleFilter() {
      this.listQuery.page = 1
      this.fetchList()
    },
    resetQuery() {
      this.listQuery = {
        page: 1,
        limit: 10,
        keyword: undefined,
        type: undefined,
        status: undefined
      }
      this.fetchList()
    },
    handleCreate() {
      this.dialogTitle = '新增职位'
      this.positionForm = {
        id: undefined,
        title: '',
        type: '',
        department: '',
        location: '',
        salaryMin: '',
        salaryMax: '',
        salaryType: 'month',
        description: '',
        requirements: '',
        preferences: '',
        experienceRequired: '',
        educationRequired: '',
        headcount: 1,
        benefits: [],
        emailKeywords: '',
        emailSyncEnabled: false,
        receivingEmail: ''
      }
      this.dialogVisible = true
      this.keywordInput = ''
      this.keywordList = []
    },
    handleEdit(row) {
      // 检查福利待遇数据
      const benefitsArray = typeof row.benefits === 'string' ? row.benefits.split(',') : Array.isArray(row.benefits) ? row.benefits : []

      const mappedBenefits = benefitsArray.map(benefit => {
        const found = Object.entries(this.getBenefitMap()).find(([key, val]) => val === benefit)
        return found ? found[0] : benefit
      })

      this.positionForm = {
        id: row.id,
        title: row.title,
        type: row.jobType,
        department: row.department || '',
        location: row.location || '',
        salaryMin: row.salaryMin || '',
        salaryMax: row.salaryMax || '',
        salaryType: row.salaryType === '面议' ? 'negotiate'
          : row.salaryType === '年薪' ? 'year' : 'month',
        description: row.description || '',
        requirements: row.requirements || '',
        preferences: row.preferences || '',
        experienceRequired: row.experienceRequired || '',
        educationRequired: row.educationRequired || '',
        headcount: row.headcount || 1,
        benefits: mappedBenefits,
        emailSyncEnabled: row.emailSyncEnabled || false,
        receivingEmail: row.receivingEmail || ''
      }

      // 处理关键字 - 从各种可能的字段中提取关键字
      this.keywordList = []
      // 首先检查keywordsList字段（API返回的格式）
      if (row.keywordsList && Array.isArray(row.keywordsList) && row.keywordsList.length > 0) {
        this.keywordList = row.keywordsList.map(item => item.keyword)
      }
      // 然后检查传统的keywords字段
      else if (row.keywords && Array.isArray(row.keywords) && row.keywords.length > 0) {
        this.keywordList = row.keywords.map(item => item.keyword)
      }
      // 最后检查字符串格式的emailKeywords
      else if (row.emailKeywords) {
        this.keywordList = row.emailKeywords.split(',').map(k => k.trim()).filter(k => k)
      }
      this.keywordInput = ''
      
      this.dialogTitle = '编辑职位'
      this.dialogVisible = true
    },
    resetForm() {
      this.$refs.form && this.$refs.form.resetFields()
    },
    async handleSavePosition() {
      try {
        await this.$refs.form.validate()
        
        // 额外校验：如果开启了邮箱同步，接收邮箱必须选择
        if (this.positionForm.emailSyncEnabled && !this.positionForm.receivingEmail) {
          this.$message.error('开启邮箱同步后，必须选择接收邮箱')
          return
        }
        
        const submitData = {
          id: this.positionForm.id,
          title: this.positionForm.title,
          jobType: this.positionForm.type,
          department: this.positionForm.department,
          location: this.positionForm.location,
          salaryMin: Number(this.positionForm.salaryType === 'negotiate' ? 0 : this.positionForm.salaryMin),
          salaryMax: Number(this.positionForm.salaryType === 'negotiate' ? 0 : this.positionForm.salaryMax),
          salaryType: this.positionForm.salaryType === 'month' ? '月薪'
            : this.positionForm.salaryType === 'year' ? '年薪' : '面议',
          description: this.positionForm.description,
          requirements: this.positionForm.requirements,
          preferences: this.positionForm.preferences,
          benefits: this.positionForm.benefits.map(benefit => this.getBenefitLabel(benefit)).join(','),
          experienceRequired: this.positionForm.experienceRequired,
          educationRequired: this.positionForm.educationRequired,
          headcount: Number(this.positionForm.headcount),
          emailSyncEnabled: this.positionForm.emailSyncEnabled,
          receivingEmail: this.positionForm.emailSyncEnabled ? this.positionForm.receivingEmail : '',
          status: 'published' // 修改为正确的状态值
        }

        // 处理关键字 - 根据后端JobKeyword模型的结构
        if (this.positionForm.emailSyncEnabled && this.keywordList.length > 0 && this.positionForm.receivingEmail) {
          // 首先获取选中邮箱的ID
          const syncEmailId = this.getSyncEmailIdByEmail(this.positionForm.receivingEmail);
          
          // 将关键字列表转换为后端需要的格式
          submitData.keywords = this.keywordList.map(keyword => ({
            keyword: keyword,
            sync_email_id: syncEmailId || 1 // 如果获取不到ID则使用默认值1
          }))
        } else {
          submitData.keywords = [] // 传空数组表示清除关键字
        }
        
        // 为向后兼容，同时也保留旧数据格式
        submitData.emailKeywords = this.keywordList.join(',')

        try {
          // 调用store的action来更新职位
          if (this.positionForm.id) {
            // 如果有ID，则是更新已有职位
            await this.updatePosition({
              id: this.positionForm.id,
              data: submitData
            })
          } else {
            // 如果没有ID，则是创建新职位
            await this.createPosition(submitData)
          }
          
          // 成功后关闭对话框并显示成功消息
          this.dialogVisible = false
          this.$message.success(this.positionForm.id ? '更新成功' : '创建成功')
          
          // 刷新列表
          this.fetchList()
        } catch (error) {
          this.$message.error(`操作失败: ${error.message || '未知错误'}`)
        }
      } catch (error) {
        this.$message.error('表单验证失败，请检查输入')
      }
    },
    async handleUpdateStatus(row, status) {
      try {
        await this.$confirm(
          `确认${status === 'paused' ? '暂停' : status === 'active' ? '恢复' : '结束'}该职位?`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await this.updatePositionStatus({id: row.id, status})
        this.$message.success('操作成功')
        this.fetchList()
      } catch (error) {
        console.error('更新状态失败:', error)
      }
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该职位?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await this.deletePosition(row.id)
        this.$message.success('删除成功')
        this.fetchList()
      } catch (error) {
        console.error('删除职位失败:', error)
      }
    },
    getBenefitMap() {
      return {
        'insurance': '五险一金',
        'annual_bonus': '年终奖',
        'overtime_pay': '加班补助',
        'meal': '餐补',
        'transportation': '交通补助',
        'communication': '通讯补贴',
        'holiday_benefits': '节日福利',
        'paid_leave': '带薪年假',
        'health_check': '定期体检',
        'travel': '员工旅游'
      }
    },
    getBenefitLabel(value) {
      return this.getBenefitMap()[value] || value
    },
    addKeyword() {
      if (!this.keywordInput.trim()) return
      
      // 处理可能包含逗号的输入，分割成多个关键字
      const keywords = this.keywordInput.split(',').map(k => k.trim()).filter(k => k)
      
      keywords.forEach(keyword => {
        if (!this.keywordList.includes(keyword)) {
          this.keywordList.push(keyword)
        }
      })
      
      this.keywordInput = ''
    },
    removeKeyword(index) {
      this.keywordList.splice(index, 1)
    },
    getEmailDepartment(email) {
      // 从预设的邮箱选项中查找对应的部门
      const option = this.syncEmailOptions.find(item => item.value === email)
      return option ? option.department : ''
    },
    getSyncEmailIdByEmail(email) {
      // 通过邮箱地址获取邮箱ID
      if (!email) {
        return null
      }
      
      const option = this.syncEmailOptions.find(item => item.value === email)
      if (!option) {
        return null
      }
      
      if (!option.id) {
        // 尝试从email对象中获取ID
        const emailData = (this.syncEmailOptions || []).find(e => e.email === email)
        if (emailData && emailData.id) {
          return emailData.id
        }
      }
      
      return option.id || null
    },
    getEmailLastSyncTime(email) {
      // 从预设的邮箱选项中查找对应的最后同步时间
      const option = this.syncEmailOptions.find(item => item.value === email)
      return option ? option.lastSyncTime || '' : ''
    },
    getEmailStatusTitle(email) {
      const option = this.syncEmailOptions.find(item => item.value === email)
      if (!option) return '未找到邮箱信息'
      
      // 首先检查邮箱是否激活
      if (!option.isActive) {
        return '该邮箱未激活，请先在系统设置中激活邮箱'
      }
      
      // 检查同步状态
      const syncTime = option.lastSyncTime
      return syncTime && syncTime !== '从未同步'
        ? `邮箱状态正常，上次同步时间: ${syncTime}`
        : '该邮箱尚未同步过，请先在系统设置中进行测试'
    },
    getEmailStatusType(email) {
      const option = this.syncEmailOptions.find(item => item.value === email)
      if (!option) return 'warning'
      
      // 首先检查邮箱是否激活
      if (!option.isActive) {
        return 'error'
      }
      
      // 检查同步状态
      const syncTime = option.lastSyncTime
      return syncTime && syncTime !== '从未同步' ? 'success' : 'warning'
    },
    handleSyncChange(val) {
      if (val && !this.positionForm.receivingEmail) {
        // 当开启邮箱同步时，尝试根据部门自动推荐邮箱
        this.recommendEmailByDepartment()
      }
    },
    recommendEmailByDepartment() {
      const department = this.positionForm.department
      if (!department) return

      // 根据部门名称匹配邮箱
      const matchedOptions = this.syncEmailOptions.filter(option => 
        option.department.includes(department) || department.includes(option.department)
      )

      if (matchedOptions.length > 0) {
        // 取第一个匹配的邮箱
        this.positionForm.receivingEmail = matchedOptions[0].value
        this.$message.success(`已自动选择 ${matchedOptions[0].department} 的邮箱`)
      }
    },
    onDepartmentChange() {
      // 如果已经开启了邮箱同步但还没选择邮箱，则根据部门推荐
      if (this.positionForm.emailSyncEnabled && !this.positionForm.receivingEmail) {
        this.recommendEmailByDepartment()
      }
    },
    goToEmailSettings() {
      // 跳转到邮箱设置页面
      this.$router.push('/settings/email')
    },
    async fetchSyncEmailOptions() {
      try {
        // 从系统邮箱设置接口获取同步邮箱列表
        const response = await this.getEmailList({
          page: 1,
          per_page: 100, // 获取足够多的邮箱
          is_active: true // 只获取启用状态的邮箱
        })
        
        // 确保response和data存在
        if (!response || !response.data) {
          throw new Error('获取邮箱数据格式错误')
        }
        
        // 将系统邮箱转换为下拉选项格式
        this.syncEmailOptions = (response.data || []).map(email => {
          return {
            id: email.id,
            value: email.email,
            label: email.email,
            department: email.description || '',
            // 使用lastSyncTime字段
            lastSyncTime: email.lastSyncTime ? this.formatTime(email.lastSyncTime) : '从未同步',
            isActive: email.isActive
          };
        });
      } catch (error) {
        this.$message.error('获取同步邮箱选项失败，请刷新重试')
        
        // 加载失败时提供一些默认选项以便测试
        this.syncEmailOptions = [
          { value: 'hr@company.com', label: 'hr@company.com', department: '人力资源部' },
          { value: 'tech@company.com', label: 'tech@company.com', department: '技术部' }
        ]
      }
    },
    getPositionKeywords(row) {
      // 获取职位的关键字列表，兼容各种数据格式
      // 首先检查是否有keywordsList数组（API返回的字段）
      if (row.keywordsList && Array.isArray(row.keywordsList) && row.keywordsList.length > 0) {
        return row.keywordsList.map(item => item.keyword)
      }
      // 然后检查其他可能的格式
      else if (row.keywords_list && Array.isArray(row.keywords_list) && row.keywords_list.length > 0) {
        return row.keywords_list.map(item => item.keyword)
      } else if (row.keywords && Array.isArray(row.keywords) && row.keywords.length > 0) {
        return row.keywords.map(item => item.keyword)
      } else if (row.keyword) {
        return [row.keyword]
      } else if (row.emailKeywords) {
        return row.emailKeywords.split(',').map(k => k.trim()).filter(k => k)
      }
      return []
    },
    async fetchList() {
      try {
        const response = await this.$store.dispatch('position/getList', this.listQuery);
        return response;
      } catch (error) {
        this.$message.error('获取职位列表失败，请刷新重试');
        return [];
      }
    },
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;

  .filter-container {
    margin-bottom: 20px;
    .filter-item {
      width: 200px;
      margin-right: 10px;
    }
  }

  .table-container {
    .card-title {
      font-size: 16px;
      font-weight: 500;
    }
  }

  .position-form {
    padding: 20px;

    .el-select {
      width: 100%;
    }
  }

  .salary-text {
    color: #f56c6c;
    font-weight: 500;
    background: #fef0f0;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .el-tag {
    margin-right: 5px;
    &.el-tag--mini {
      height: 22px;
      padding: 0 8px;
      line-height: 20px;

      &.el-tag--info {
        background-color: #f4f4f5;
        border-color: #e9e9eb;
        color: #909399;
      }
    }
  }

  .dialog-footer {
    text-align: right;
    padding-top: 20px;
    border-top: 1px solid #dcdfe6;
  }

  .el-table {
    margin: 15px 0;

    .el-table__header th {
      background-color: #f5f7fa;
      color: #606266;
      font-weight: 500;
    }

    .el-table__row {
      &:hover {
        td {
          background-color: #f5f7fa !important;
        }
      }
    }
  }

  .box-card {
    margin-bottom: 20px;
    border-radius: 8px;

    .card-header {
      display: flex;
      align-items: center;

      .text-muted {
        margin-left: 10px;
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .salary-range {
    .salary-separator {
      text-align: center;
      line-height: 40px;
    }

    .el-input-number {
      width: 100%;
    }
  }

  .benefit-group {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
    line-height: 1.4;
  }

  .keyword-input {
    margin-bottom: 10px;
  }

  .keyword-tags {
    margin-top: 5px;
    min-height: 32px;
    padding: 5px;
    border: 1px dashed #dcdfe6;
    border-radius: 4px;
    background-color: #f9f9f9;
  }

  .keyword-tag {
    margin-right: 6px;
    margin-bottom: 6px;
  }

  .no-keywords {
    color: #909399;
    font-size: 14px;
    padding: 5px;
  }

  .keyword-list-tag {
    margin-right: 3px;
  }

  .email-department {
    margin-top: 5px;
    font-size: 12px;
    color: #909399;
  }

  .email-sync-time {
    margin-top: 3px;
    font-size: 12px;
    color: #67c23a;
  }

  .email-status {
    margin-top: 10px;
  }

  ::v-deep .el-card__header {
    padding: 15px 20px;
    border-bottom: 1px solid #ebeef5;
    background: #fafafa;
  }

  ::v-deep .el-card__body {
    padding: 20px;
  }
}
</style>
