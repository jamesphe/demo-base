<template>
  <div class="app-container">
    <h2>试用管理</h2>
    <el-card class="box-card">
      <div class="filter-container">
        <el-radio-group v-model="viewType" class="filter-item" @change="handleViewTypeChange">
          <el-radio-button label="pending">待审核</el-radio-button>
          <el-radio-button label="all">所有记录</el-radio-button>
        </el-radio-group>
      </div>

      <el-table
        v-loading="listLoading"
        :data="list"
        border
        style="width: 100%"
      >
        <el-table-column
          prop="companyName"
          label="公司名称"
          align="center"
        >
          <template slot-scope="{row}">
            <el-link type="primary" @click="showDetail(row)">{{ row.companyName }}</el-link>
          </template>
        </el-table-column>
        <el-table-column
          prop="contactName"
          label="联系人"
          align="center"
        />
        <el-table-column
          prop="contactPhone"
          label="联系电话"
          align="center"
        />
        <el-table-column
          prop="contactEmail"
          label="联系邮箱"
          align="center"
        />
        <el-table-column
          prop="companySize"
          label="公司规模"
          align="center"
        />
        <el-table-column
          prop="trialStartDate"
          label="试用开始日期"
          align="center"
        />
        <el-table-column
          prop="trialEndDate"
          label="试用结束日期"
          align="center"
        />
        <el-table-column
          prop="status"
          label="状态"
          align="center"
        >
          <template slot-scope="{row}">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="rejectReason"
          label="拒绝原因"
          align="center"
        >
          <template slot-scope="{row}">
            <span v-if="row.status === TRIAL_STATUS.REJECTED">
              {{ row.rejectReason }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          align="center"
          width="230"
        >
          <template slot-scope="{row}">
            <template v-if="row.status === TRIAL_STATUS.PENDING">
              <el-button type="success" size="mini" @click="handleApprove(row)">
                通过
              </el-button>
              <el-button type="danger" size="mini" @click="handleReject(row)">
                拒绝
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.per_page"
        @pagination="getList"
      />
    </el-card>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      title="拒绝原因"
      :visible.sync="rejectDialogVisible"
      width="500px"
      append-to-body
    >
      <el-form ref="rejectForm" :model="rejectForm" :rules="rejectRules">
        <el-form-item label="拒绝原因" prop="reason" :rules="[{ required: true, message: '请输入拒绝原因' }]">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="rejectDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="confirmReject">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog
      title="审批试用申请"
      :visible.sync="approveDialogVisible"
      width="600px"
      append-to-body
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
        class="form-container form-wrapper"
      >
        <div class="form-section">
          <div class="section-title">租户信息</div>
          <el-form-item label="租户名称" prop="tenantName">
            <el-input v-model="temp.tenantName" placeholder="请输入租户名称" />
          </el-form-item>
          <el-form-item label="联系人" prop="contactPerson">
            <el-input v-model="temp.contactPerson" placeholder="请输入联系人" />
          </el-form-item>
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="temp.phone" placeholder="请输入联系电话" />
          </el-form-item>
          <el-form-item label="联系邮箱" prop="email">
            <el-input v-model="temp.email" placeholder="请输入联系邮箱" />
          </el-form-item>
          <el-form-item label="公司地址" prop="address">
            <el-input v-model="temp.address" placeholder="请输入公司地址" />
          </el-form-item>
          <el-form-item label="试用开始日期" prop="trialStartDate">
            <el-date-picker
              v-model="temp.trialStartDate"
              type="date"
              placeholder="选择开始日期"
              value-format="yyyy-MM-dd"
            />
          </el-form-item>
          <el-form-item label="试用天数" prop="trialDays">
            <el-input-number
              v-model="temp.trialDays"
              :min="7"
              :max="30"
              placeholder="请输入试用天数"
            />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">管理员账号</div>
          <el-form-item label="管理员邮箱" prop="adminEmail">
            <el-input v-model="temp.adminEmail" placeholder="请输入管理员邮箱" />
          </el-form-item>
          <el-form-item label="管理员用户名" prop="adminUsername">
            <el-input v-model="temp.adminUsername" placeholder="请输入管理员用户名" />
          </el-form-item>
          <el-form-item label="初始密码" prop="adminPassword">
            <el-input v-model="temp.adminPassword" placeholder="请输入初始密码">
              <el-button slot="append" @click="generatePassword">生成密码</el-button>
            </el-input>
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="approveDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="confirmApprove">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      title="试用申请详情"
      :visible.sync="detailDialogVisible"
      width="700px"
      custom-class="detail-dialog"
    >
      <el-form label-width="120px" label-position="left" class="detail-form">
        <div class="detail-section">
          <div class="section-title">
            <i class="el-icon-user" />
            基本信息
          </div>
          <div class="form-content">
            <el-form-item label="公司名称">
              <span class="detail-text">{{ detailData.companyName }}</span>
            </el-form-item>
            <el-form-item label="联系人">
              <span class="detail-text">{{ detailData.contactName }}</span>
            </el-form-item>
            <el-form-item label="联系电话">
              <span class="detail-text">{{ detailData.contactPhone }}</span>
            </el-form-item>
            <el-form-item label="联系邮箱">
              <span class="detail-text">{{ detailData.contactEmail }}</span>
            </el-form-item>
          </div>
        </div>

        <div class="detail-section">
          <div class="section-title">
            <i class="el-icon-office-building" />
            业务信息
          </div>
          <div class="form-content">
            <el-form-item label="公司规模">
              <span class="detail-text">{{ detailData.companySize }}</span>
            </el-form-item>
            <el-form-item label="业务描述" class="multi-line-item">
              <span class="detail-text">{{ detailData.businessDescription }}</span>
            </el-form-item>
            <el-form-item label="申请原因" class="multi-line-item">
              <span class="detail-text">{{ detailData.applicationReason }}</span>
            </el-form-item>
            <el-form-item label="试用时间">
              <span class="detail-text">{{ detailData.trialStartDate }} 至 {{ detailData.trialEndDate }}</span>
            </el-form-item>
            <el-form-item label="申请状态">
              <el-tag :type="getStatusType(detailData.status)" class="status-tag">
                {{ getStatusText(detailData.status) }}
              </el-tag>
            </el-form-item>
            <el-form-item v-if="detailData.status === TRIAL_STATUS.REJECTED" label="拒绝原因" class="multi-line-item">
              <span class="detail-text reject-reason">{{ detailData.rejectReason }}</span>
            </el-form-item>
          </div>
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <template v-if="detailData.status === TRIAL_STATUS.PENDING">
          <el-button type="success" size="medium" @click="handleApprove(detailData)">通过申请</el-button>
          <el-button type="danger" size="medium" @click="handleReject(detailData)">拒绝申请</el-button>
        </template>
        <el-button size="medium" @click="detailDialogVisible = false">{{ detailData.status === TRIAL_STATUS.PENDING ? '取 消' : '关 闭' }}</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import Pagination from '@/components/Pagination'
import { TRIAL_STATUS, TRIAL_STATUS_MAP } from '@/constants/trial'

export default {
  name: 'TenantTrial',
  components: {
    Pagination
  },
  data() {
    return {
      TRIAL_STATUS,
      viewType: 'pending',
      listQuery: {
        page: 1,
        per_page: 10
      },
      rejectDialogVisible: false,
      rejectForm: {
        id: null,
        reason: ''
      },
      detailDialogVisible: false,
      detailData: {
        companyName: '',
        contactName: '',
        contactPhone: '',
        contactEmail: '',
        companySize: '',
        businessDescription: '',
        applicationReason: '',
        trialStartDate: '',
        trialEndDate: '',
        status: '',
        rejectReason: ''
      },
      rejectRules: {
        reason: [
          { required: true, message: '请输入拒绝原因', trigger: 'blur' },
          { min: 5, message: '拒绝原因至少需要5个字符', trigger: 'blur' }
        ]
      },
      approveDialogVisible: false,
      temp: {
        id: null,
        tenantName: '',
        contactPerson: '',
        phone: '',
        email: '',
        address: '',
        trialStartDate: '',
        trialDays: 14,
        adminEmail: '',
        adminUsername: '',
        adminPassword: ''
      },
      rules: {
        tenantName: [
          { required: true, message: '请输入租户名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        contactPerson: [
          { required: true, message: '请输入联系人', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入联系邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        address: [
          { required: true, message: '请输入公司地址', trigger: 'blur' }
        ],
        trialStartDate: [
          { required: true, message: '请选择试用开始日期', trigger: 'change' }
        ],
        trialDays: [
          { required: true, message: '请输入试用天数', trigger: 'blur' }
        ],
        adminEmail: [
          { required: true, message: '请输入管理员邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        adminUsername: [
          { required: true, message: '请输入管理员用户名', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        adminPassword: [
          { required: true, message: '请输入初始密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapState({
      list: state => state.trial.list,
      total: state => state.trial.total,
      listLoading: state => state.trial.listLoading,
      meta: state => state.trial.meta
    })
  },
  created() {
    this.loadList()
  },
  methods: {
    ...mapActions('trial', [
      'getPendingList',
      'getList',
      'approveTrial',
      'rejectTrial'
    ]),

    loadList() {
      if (this.viewType === 'pending') {
        this.getPendingList(this.listQuery)
      } else {
        this.getList(this.listQuery)
      }
    },

    handleViewTypeChange() {
      this.listQuery.page = 1
      this.loadList()
    },

    getStatusType(status) {
      return TRIAL_STATUS_MAP[status]?.type || 'info'
    },

    getStatusText(status) {
      return TRIAL_STATUS_MAP[status]?.text || '未知状态'
    },

    handleApprove(row) {
      this.temp = {
        id: row.id,
        tenantName: row.companyName,
        contactPerson: row.contactName,
        phone: row.contactPhone,
        email: row.contactEmail,
        address: row.companyAddress || '',
        trialStartDate: new Date().toISOString().split('T')[0],
        trialDays: 14,
        adminEmail: row.contactEmail,
        adminUsername: row.contactName,
        adminPassword: this.generateRandomPassword()
      }
      this.approveDialogVisible = true
    },

    generatePassword() {
      this.temp.adminPassword = this.generateRandomPassword()
    },

    generateRandomPassword() {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      let password = ''
      for (let i = 0; i < 8; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length))
      }
      return password
    },

    async confirmApprove() {
      try {
        await this.$refs.dataForm.validate()

        // 构造正确的数据格式
        const approvalData = {
          tenant: {
            name: this.temp.tenantName,
            status: 'trial',
            contact_person: this.temp.contactPerson,
            phone: this.temp.phone,
            email: this.temp.email,
            address: this.temp.address
          },
          trial_start_date: this.temp.trialStartDate,
          trial_days: this.temp.trialDays,
          admin: {
            email: this.temp.adminEmail,
            username: this.temp.adminUsername,
            password: this.temp.adminPassword
          }
        }

        await this.approveTrial({
          id: this.temp.id,
          data: approvalData
        })

        this.$message.success('审批通过成功')
        this.approveDialogVisible = false
        this.detailDialogVisible = false
        this.loadList()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.message || '操作失败')
        }
      }
    },

    handleReject(row) {
      this.rejectForm.id = row.id
      this.rejectForm.reason = ''
      this.rejectDialogVisible = true
    },

    async confirmReject() {
      if (!this.rejectForm.reason) {
        this.$message.warning('请输入拒绝原因')
        return
      }

      try {
        await this.rejectTrial({
          id: this.rejectForm.id,
          reason: this.rejectForm.reason
        })
        this.$message.success('已拒绝该申请')
        this.rejectDialogVisible = false
        this.detailDialogVisible = false
        this.loadList()
      } catch (error) {
        this.$message.error('操作失败')
      }
    },

    showDetail(row) {
      this.detailData = { ...row }
      this.detailDialogVisible = true
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
}
.filter-container {
  margin-bottom: 20px;
}
.filter-item {
  margin-right: 10px;
}
.dialog-footer {
  text-align: right;
}
.detail-section {
  margin-bottom: 20px;
}
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

/* 详情弹窗样式 */
.detail-dialog {
  border-radius: 8px;

  ::v-deep .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #ebeef5;
  }

  ::v-deep .el-dialog__title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  ::v-deep .el-dialog__body {
    padding: 24px;
  }

  ::v-deep .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #ebeef5;
    text-align: right;

    .el-button {
      padding: 9px 20px;
      margin-left: 10px;
    }
  }
}

.detail-form {
  padding: 0 10px;
}

.detail-section {
  background: #fafafa;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 24px;
}
.detail-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.section-title i {
  margin-right: 8px;
  font-size: 18px;
  color: #409EFF;
}

.form-content {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.detail-text {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.multi-line-item .detail-text {
  white-space: pre-line;
  display: block;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.reject-reason {
  color: #f56c6c;
}

.status-tag {
  padding: 6px 16px;
  font-size: 13px;
}

.form-wrapper {
  ::v-deep .el-form-item {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  ::v-deep .el-form-item__label {
    color: #909399;
    font-weight: normal;
    padding-right: 12px;
  }
}

.form-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #606266;

  i {
    margin-right: 8px;
    font-size: 18px;
    color: #409EFF;
  }
}
</style>
