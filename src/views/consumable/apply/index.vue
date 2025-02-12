<template>
  <div class="app-container">
    <!-- 搜索栏 -->
    <div class="filter-container">
      <el-form :inline="true" :model="listQuery" class="demo-form-inline">
        <el-form-item label="申请状态">
          <el-select v-model="listQuery.status" placeholder="请选择状态" clearable>
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="耗材类型">
          <el-select v-model="listQuery.type" placeholder="请选择类型" clearable>
            <el-option v-for="type in typeOptions" :key="type" :label="type" :value="type" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请人">
          <el-input v-model="listQuery.applicant" placeholder="请输入申请人" clearable />
        </el-form-item>
        <el-form-item label="申请日期">
          <el-date-picker
            v-model="listQuery.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="yyyy-MM-dd"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">查询</el-button>
          <el-button v-if="!isAdmin" type="success" @click="handleCreate">新建申报</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 申报列表 -->
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      style="width: 100%"
      @sort-change="handleSort"
    >
      <el-table-column label="申报编号" prop="id" align="center" width="80" />
      <el-table-column label="申请人" prop="applicant" width="100" />
      <el-table-column label="耗材类型" prop="type" width="100" />
      <el-table-column label="耗材名称" prop="name" width="120" />
      <el-table-column label="数量" width="100">
        <template slot-scope="{row}">
          {{ row.quantity }} {{ row.unit }}
        </template>
      </el-table-column>
      <el-table-column label="紧急程度" prop="urgency" width="80" sortable="custom" :sort-orders="['ascending', 'descending']">
        <template slot-scope="{row}">
          <el-tag :type="row.urgency === '特急' ? 'danger' : row.urgency === '紧急' ? 'warning' : ''">
            {{ row.urgency }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="申请部门" prop="department" width="120" />
      <el-table-column label="申请日期" width="160" prop="applyDate" sortable="custom" :sort-orders="['ascending', 'descending']">
        <template slot-scope="{row}">
          {{ row.applyDate }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTextFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200">
        <template slot-scope="{row}">
          <el-button
            v-if="isAdmin && row.status === 'pending'"
            size="mini"
            type="success"
            @click="handleApprove(row)">
            通过
          </el-button>
          <el-button
            v-if="isAdmin && row.status === 'pending'"
            size="mini"
            type="danger"
            @click="handleReject(row)">
            拒绝
          </el-button>
          <el-button
            size="mini"
            type="primary"
            @click="handleDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 申报表单弹窗 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="100px"
      >
        <el-form-item label="耗材类型" prop="type">
          <el-select v-model="temp.type" placeholder="请选择类型">
            <el-option v-for="type in typeOptions" :key="type" :label="type" :value="type" />
          </el-select>
        </el-form-item>
        <el-form-item label="耗材名称" prop="name">
          <el-input v-model="temp.name"/>
        </el-form-item>
        <el-form-item label="申请数量" prop="quantity">
          <el-input-number v-model="temp.quantity" :min="1"/>
          <el-select v-model="temp.unit" style="margin-left: 10px">
            <el-option label="个" value="个"/>
            <el-option label="包" value="包"/>
            <el-option label="盒" value="盒"/>
            <el-option label="卷" value="卷"/>
            <el-option label="套" value="套"/>
          </el-select>
        </el-form-item>
        <el-form-item label="紧急程度" prop="urgency">
          <el-select v-model="temp.urgency">
            <el-option label="普通" value="普通"/>
            <el-option label="紧急" value="紧急"/>
            <el-option label="特急" value="特急"/>
          </el-select>
        </el-form-item>
        <el-form-item label="预计使用日期" prop="expectedDate">
          <el-date-picker v-model="temp.expectedDate" type="date" placeholder="选择日期"/>
        </el-form-item>
        <el-form-item label="用途说明" prop="purpose">
          <el-input
            v-model="temp.purpose"
            type="textarea"
            :rows="3"
            placeholder="请详细说明耗材用途"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="temp.remark"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </div>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog 
      title="申请详情" 
      :visible.sync="detailVisible" 
      width="700px"
      custom-class="detail-dialog"
    >
      <div class="detail-header">
        <div class="status-box">
          <el-tag 
            :type="detail.status | statusFilter" 
            size="medium"
            effect="dark"
          >
            {{ detail.status | statusTextFilter }}
          </el-tag>
        </div>
        <div class="apply-info">
          <span class="apply-id">申请编号：{{ detail.id }}</span>
          <span class="apply-date">申请时间：{{ detail.applyDate }}</span>
        </div>
      </div>

      <el-divider content-position="left">基本信息</el-divider>
      
      <el-row :gutter="20" class="detail-content">
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-user"></i>
            <span class="label">申请人：</span>
            <span class="value">{{ detail.applicant }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-office-building"></i>
            <span class="label">申请部门：</span>
            <span class="value">{{ detail.department }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-box"></i>
            <span class="label">耗材类型：</span>
            <span class="value">{{ detail.type }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-goods"></i>
            <span class="label">耗材名称：</span>
            <span class="value">{{ detail.name }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-shopping-cart-full"></i>
            <span class="label">申请数量：</span>
            <span class="value">{{ detail.quantity }} {{ detail.unit }}</span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-warning-outline"></i>
            <span class="label">紧急程度：</span>
            <span class="value">
              <el-tag 
                size="small" 
                :type="detail.urgency === '特急' ? 'danger' : detail.urgency === '紧急' ? 'warning' : 'info'"
              >
                {{ detail.urgency }}
              </el-tag>
            </span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="detail-item">
            <i class="el-icon-date"></i>
            <span class="label">预计使用日期：</span>
            <span class="value">{{ detail.expectedDate }}</span>
          </div>
        </el-col>
      </el-row>

      <el-divider content-position="left">申请说明</el-divider>

      <div class="detail-desc">
        <div class="desc-item">
          <div class="desc-label">
            <i class="el-icon-document"></i>
            用途说明：
          </div>
          <div class="desc-content">{{ detail.purpose }}</div>
        </div>
        <div class="desc-item">
          <div class="desc-label">
            <i class="el-icon-notebook-2"></i>
            备注信息：
          </div>
          <div class="desc-content">{{ detail.remark || '无' }}</div>
        </div>
      </div>

      <template v-if="detail.status !== 'pending'">
        <el-divider content-position="left">审批信息</el-divider>
        <el-row :gutter="20" class="detail-content">
          <el-col :span="12">
            <div class="detail-item">
              <i class="el-icon-user"></i>
              <span class="label">审批人：</span>
              <span class="value">{{ detail.approver }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-item">
              <i class="el-icon-time"></i>
              <span class="label">审批时间：</span>
              <span class="value">{{ detail.approveDate }}</span>
            </div>
          </el-col>
        </el-row>
      </template>

      <div slot="footer" class="dialog-footer">
        <el-button @click="detailVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Pagination from '@/components/Pagination'
import { getApplyList, createApply, updateApplyStatus } from '@/api/consumable'

export default {
  name: 'ConsumableApply',
  components: { Pagination },
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        status: '',
        type: '',
        applicant: '',
        dateRange: [],
        sort: '',
        order: ''
      },
      typeOptions: ['办公用品', '实验耗材', '教学用品', '清洁用品', '电子耗材'],
      dialogVisible: false,
      detailVisible: false,
      dialogTitle: '',
      temp: {
        id: undefined,
        type: '',
        name: '',
        quantity: 1,
        unit: '个',
        urgency: '普通',
        purpose: '',
        expectedDate: '',
        remark: ''
      },
      detail: {},
      rules: {
        type: [{ required: true, message: '请选择耗材类型', trigger: 'change' }],
        name: [{ required: true, message: '请输入耗材名称', trigger: 'blur' }],
        quantity: [{ required: true, message: '请输入申请数量', trigger: 'blur' }],
        urgency: [{ required: true, message: '请选择紧急程度', trigger: 'change' }],
        purpose: [{ required: true, message: '请输入用途说明', trigger: 'blur' }],
        expectedDate: [{ required: true, message: '请选择预计使用日期', trigger: 'change' }]
      }
    }
  },
  computed: {
    ...mapGetters([
      'roles',
      'name'
    ]),
    isAdmin() {
      return this.roles.includes('admin')
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      console.log('Fetching list with query:', this.listQuery)
      getApplyList(this.listQuery).then(response => {
        console.log('API response:', response)
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      }).catch(error => {
        console.error('API error:', error)
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      this.dialogTitle = '新建耗材申报'
      this.temp = {
        type: '',
        name: '',
        quantity: 1,
        unit: '个',
        urgency: '普通',
        purpose: '',
        expectedDate: '',
        remark: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    submitForm() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createApply(this.temp).then(() => {
            this.dialogVisible = false
            this.$message({
              type: 'success',
              message: '提交成功'
            })
            this.getList()
          })
        }
      })
    },
    handleApprove(row) {
      updateApplyStatus(row.id, 'approved').then(() => {
        this.$message({
          type: 'success',
          message: '审批通过'
        })
        this.getList()
      })
    },
    handleReject(row) {
      this.$confirm('确认拒绝该申请?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        updateApplyStatus(row.id, 'rejected').then(() => {
          this.$message({
            type: 'success',
            message: '已拒绝'
          })
          this.getList()
        })
      })
    },
    handleDetail(row) {
      this.detail = { ...row }
      this.detailVisible = true
    },
    handleSort(column) {
      console.log('Sort changed:', column)
      this.listQuery.sort = column.prop
      this.listQuery.order = column.order === 'ascending' ? 'asc' : 'desc'
      console.log('Updated listQuery:', this.listQuery)
      this.getList()
    }
  }
}
</script>

<style lang="scss" scoped>
.detail-dialog {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .status-box {
      .el-tag {
        padding: 0 15px;
        height: 32px;
        line-height: 32px;
      }
    }
    
    .apply-info {
      color: #606266;
      font-size: 14px;
      
      .apply-date {
        margin-left: 20px;
      }
    }
  }

  .detail-content {
    padding: 10px 0;
    
    .detail-item {
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      
      i {
        color: #409EFF;
        margin-right: 8px;
        font-size: 16px;
      }
      
      .label {
        color: #606266;
        margin-right: 8px;
      }
      
      .value {
        color: #303133;
        flex: 1;
      }
    }
  }

  .detail-desc {
    padding: 0 20px;
    
    .desc-item {
      margin-bottom: 20px;
      
      .desc-label {
        color: #606266;
        margin-bottom: 8px;
        font-weight: 500;
        
        i {
          color: #409EFF;
          margin-right: 8px;
        }
      }
      
      .desc-content {
        color: #303133;
        line-height: 1.6;
        padding: 10px;
        background: #f5f7fa;
        border-radius: 4px;
        min-height: 40px;
      }
    }
  }

  .el-divider__text {
    font-size: 16px;
    font-weight: 500;
  }
}
</style>
