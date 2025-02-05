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
        <el-table-column label="职位名称" prop="title" min-width="180" show-overflow-tooltip>
          <template slot-scope="{row}">
            <el-link type="primary" @click="handleEdit(row)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="部门" prop="department" width="120" align="center" />
        <el-table-column label="工作地点" prop="location" width="100" align="center" />
        <el-table-column label="职位类型" width="100" align="center">
          <template slot-scope="{row}">
            <el-tag :type="row.type === 'fulltime' ? 'primary' : row.type === 'parttime' ? 'success' : 'warning'">
              {{ row.type === 'fulltime' ? '全职' : row.type === 'parttime' ? '兼职' : '实习' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="薪资范围" width="150" align="center">
          <template slot-scope="{row}">
            <span class="salary-text">{{ row.salaryMin }}-{{ row.salaryMax }}K/{{ row.salaryUnit === 'month' ? '月' : '年' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template slot-scope="{row}">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'paused' ? 'warning' : 'info'">
              {{ row.status === 'active' ? '招聘中' : row.status === 'paused' ? '已暂停' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="160" align="center">
          <template slot-scope="{row}">
            <span>{{ row.createTime | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="340" fixed="right">
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
                v-if="row.status === 'active'"
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位名称" prop="title">
              <el-input v-model="positionForm.title" placeholder="请输入职位名称"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位类型" prop="type">
              <el-select v-model="positionForm.type" placeholder="请选择职位类型" style="width: 100%">
                <el-option label="全职" value="fulltime" />
                <el-option label="兼职" value="parttime" />
                <el-option label="实习" value="intern" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-input v-model="positionForm.department" placeholder="请输入部门"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作地点" prop="location">
              <el-cascader
                v-model="positionForm.location"
                :options="cityOptions"
                placeholder="请选择工作地点"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="薪资范围">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-input-number v-model="positionForm.salaryMin" :min="1" placeholder="最低薪资" style="width: 100%"/>
            </el-col>
            <el-col :span="8">
              <el-input-number v-model="positionForm.salaryMax" :min="1" placeholder="最高薪资" style="width: 100%"/>
            </el-col>
            <el-col :span="8">
              <el-select v-model="positionForm.salaryUnit" style="width: 100%">
                <el-option label="K/月" value="month" />
                <el-option label="K/年" value="year" />
              </el-select>
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item label="职位描述" prop="description">
          <el-input type="textarea" :rows="4" v-model="positionForm.description" placeholder="请输入职位描述"/>
        </el-form-item>

        <el-form-item label="任职要求" prop="requirements">
          <el-input type="textarea" :rows="4" v-model="positionForm.requirements" placeholder="请输入任职要求"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="updatePosition">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getPositionList, updatePosition, deletePosition, updatePositionStatus } from '@/api/position'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'

export default {
  name: 'PositionMaintain',
  components: { Pagination },
  filters: {
    parseTime
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
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
        location: [],
        salaryMin: '',
        salaryMax: '',
        salaryUnit: 'month',
        description: '',
        requirements: ''
      },
      cityOptions: [], // 需要添加城市数据
      rules: {
        title: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
        type: [{ required: true, message: '请选择职位类型', trigger: 'change' }],
        department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
        location: [{ required: true, message: '请选择工作地点', trigger: 'change' }],
        description: [{ required: true, message: '请输入职位描述', trigger: 'blur' }],
        requirements: [{ required: true, message: '请输入任职要求', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getPositionList(this.listQuery)
        this.list = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取职位列表失败:', error)
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetQuery() {
      this.listQuery = {
        page: 1,
        limit: 10,
        keyword: undefined,
        type: undefined,
        status: undefined
      }
      this.getList()
    },
    handleCreate() {
      this.dialogTitle = '新增职位'
      this.positionForm = {
        id: undefined,
        title: '',
        type: '',
        department: '',
        location: [],
        salaryMin: '',
        salaryMax: '',
        salaryUnit: 'month',
        description: '',
        requirements: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.positionForm = Object.assign({}, row)
      this.dialogTitle = '编辑职位'
      this.dialogVisible = true
    },
    resetForm() {
      this.$refs.form && this.$refs.form.resetFields()
    },
    async updatePosition() {
      try {
        await this.$refs.form.validate()
        await updatePosition(this.positionForm)
        this.dialogVisible = false
        this.$message.success('更新成功')
        this.getList()
      } catch (error) {
        console.error('更新职位失败:', error)
        this.$message.error('更新失败，请重试')
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
        await updatePositionStatus(row.id, status)
        this.$message.success('操作成功')
        this.getList()
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
        await deletePosition(row.id)
        this.$message.success('删除成功')
        this.getList()
      } catch (error) {
        console.error('删除职位失败:', error)
      }
    }
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
  }

  .el-tag {
    margin-right: 5px;
  }

  .dialog-footer {
    text-align: right;
    padding-top: 20px;
    border-top: 1px solid #dcdfe6;
  }
}
</style> 