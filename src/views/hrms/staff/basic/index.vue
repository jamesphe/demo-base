<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="工号">
          <el-input v-model="queryParams.employeeId" placeholder="请输入工号" clearable />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="queryParams.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-cascader
            v-model="queryParams.departmentId"
            :options="departmentOptions"
            :props="{ checkStrictly: true }"
            clearable
            placeholder="请选择部门"
          />
        </el-form-item>
        <el-form-item label="职称">
          <el-select v-model="queryParams.titleId" placeholder="请选择职称" clearable>
            <el-option
              v-for="item in titleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="人员类型">
          <el-select v-model="queryParams.staffType" placeholder="请选择人员类型" clearable>
            <el-option
              v-for="item in staffTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery">查询</el-button>
          <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮区域 -->
    <el-card class="table-card">
      <div class="table-operations">
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增</el-button>
        <el-button type="success" icon="el-icon-upload2" @click="handleImport">导入</el-button>
        <el-button type="warning" icon="el-icon-download" @click="handleExport">导出</el-button>
        <el-button type="danger" icon="el-icon-delete" :disabled="!selectedIds.length" @click="handleBatchDelete">
          批量删除
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="staffList"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="工号" prop="employeeId" width="100" />
        <el-table-column label="姓名" prop="name" width="100">
          <template slot-scope="scope">
            <el-button type="text" @click="handleView(scope.row)">{{ scope.row.name }}</el-button>
          </template>
        </el-table-column>
        <el-table-column label="性别" prop="gender" width="60">
          <template slot-scope="scope">
            {{ scope.row.gender === 1 ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column label="部门" prop="departmentName" />
        <el-table-column label="职位" prop="position" />
        <el-table-column label="职称" prop="title" />
        <el-table-column label="学历" prop="education" width="100" />
        <el-table-column label="入职日期" prop="entryDate" width="100" />
        <el-table-column label="状态" prop="status" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
              {{ scope.row.status === 1 ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="人员类型" align="center">
          <template slot-scope="scope">
            <el-tag :type="getStaffTypeTag(scope.row.staffType)">
              {{ getStaffTypeLabel(scope.row.staffType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template slot-scope="scope">
            <el-button type="text" icon="el-icon-edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="text" icon="el-icon-delete" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="getList"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="700px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="employeeId">
              <el-input v-model="form.employeeId" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio :label="1">男</el-radio>
                <el-radio :label="2">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门" prop="departmentId">
              <el-cascader
                v-model="form.departmentId"
                :options="departmentOptions"
                :props="{ checkStrictly: true }"
                placeholder="请选择部门"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-select v-model="form.position" placeholder="请选择职位">
                <el-option
                  v-for="item in positionOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="titleId">
              <el-select v-model="form.titleId" placeholder="请选择职称">
                <el-option
                  v-for="item in titleOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历" prop="education">
              <el-select v-model="form.education" placeholder="请选择学历">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="专科" value="专科" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="entryDate">
              <el-date-picker
                v-model="form.entryDate"
                type="date"
                placeholder="选择入职日期"
                value-format="yyyy-MM-dd"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="人员类型" prop="staffType">
              <el-select v-model="form.staffType" placeholder="请选择人员类型">
                <el-option
                  v-for="item in staffTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog title="导入员工信息" :visible.sync="importVisible" width="400px" append-to-body>
      <el-upload
        class="upload-demo"
        drag
        action="/api/staff/import"
        :headers="headers"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
      >
        <i class="el-icon-upload" />
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div slot="tip" class="el-upload__tip">只能上传 xlsx/xls 文件</div>
      </el-upload>
      <div slot="footer" class="dialog-footer">
        <el-button @click="importVisible = false">取 消</el-button>
        <el-button type="primary" @click="downloadTemplate">下载模板</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import request from '@/utils/request'

export default {
  name: 'StaffBasic',
  components: { Pagination },
  data() {
    return {
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        employeeId: undefined,
        name: undefined,
        departmentId: undefined,
        titleId: undefined,
        staffType: undefined
      },
      // 表格数据
      staffList: [],
      total: 0,
      loading: false,
      selectedIds: [],

      // 对话框显示控制
      dialogVisible: false,
      dialogTitle: '',
      importVisible: false,

      // 表单数据
      form: {
        employeeId: undefined,
        name: undefined,
        gender: 1,
        departmentId: undefined,
        position: undefined,
        titleId: undefined,
        education: undefined,
        entryDate: undefined,
        staffType: undefined
      },

      // 表单验证规则
      rules: {
        employeeId: [{ required: true, message: '请输入工号', trigger: 'blur' }],
        name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
        departmentId: [{ required: true, message: '请选择部门', trigger: 'change' }],
        position: [{ required: true, message: '请选择职位', trigger: 'change' }],
        titleId: [{ required: true, message: '请选择职称', trigger: 'change' }],
        education: [{ required: true, message: '请选择学历', trigger: 'change' }],
        entryDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
        staffType: [{ required: true, message: '请选择人员类型', trigger: 'change' }]
      },

      // 下拉选项
      departmentOptions: [],
      positionOptions: [],
      titleOptions: [],
      staffTypeOptions: [],

      // 上传相关
      headers: {
        Authorization: 'Bearer ' + this.$store.getters.token
      }
    }
  },
  created() {
    this.getList()
    this.getDepartments()
    this.getPositions()
    this.getTitles()
    this.getStaffTypes()
  },
  methods: {
    // 获取列表数据
    async getList() {
      this.loading = true
      try {
        const response = await request({
          url: '/vue-element-admin/staff/list',
          method: 'get',
          params: this.queryParams
        })
        this.staffList = response.data.items
        this.total = response.data.total
      } catch (error) {
        console.error('获取列表失败:', error)
      }
      this.loading = false
    },

    // 获取部门数据
    async getDepartments() {
      try {
        const response = await request({
          url: '/vue-element-admin/department/tree',
          method: 'get'
        })
        this.departmentOptions = response.data
      } catch (error) {
        console.error('获取部门数据失败:', error)
      }
    },

    // 获取职位数据
    async getPositions() {
      try {
        const response = await request({
          url: '/vue-element-admin/position/list',
          method: 'get'
        })
        this.positionOptions = response.data
      } catch (error) {
        console.error('获取职位数据失败:', error)
      }
    },

    // 获取职称数据
    async getTitles() {
      try {
        const response = await request({
          url: '/vue-element-admin/title/list',
          method: 'get'
        })
        this.titleOptions = response.data
      } catch (error) {
        console.error('获取职称数据失败:', error)
      }
    },

    // 获取人员类型数据
    async getStaffTypes() {
      try {
        const response = await request({
          url: '/vue-element-admin/staff/type/list',
          method: 'get'
        })
        this.staffTypeOptions = response.data
      } catch (error) {
        console.error('获取人员类型数据失败:', error)
      }
    },

    // 获取人员类型标签样式
    getStaffTypeTag(type) {
      const map = {
        1: 'success',
        2: 'warning',
        3: 'warning',
        4: 'info',
        5: 'danger'
      }
      return map[type]
    },

    // 获取人员类型标签文本
    getStaffTypeLabel(type) {
      const option = this.staffTypeOptions.find(item => item.value === type)
      return option ? option.label : ''
    },

    // 查询按钮点击
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },

    // 重置按钮点击
    resetQuery() {
      this.queryParams = {
        pageNum: 1,
        pageSize: 10,
        employeeId: undefined,
        name: undefined,
        departmentId: undefined,
        titleId: undefined,
        staffType: undefined
      }
      this.getList()
    },

    // 多选框选中数据
    handleSelectionChange(selection) {
      this.selectedIds = selection.map(item => item.id)
    },

    // 新增按钮点击
    handleAdd() {
      this.dialogTitle = '添加员工信息'
      this.form = {
        employeeId: undefined,
        name: undefined,
        gender: 1,
        departmentId: undefined,
        position: undefined,
        titleId: undefined,
        education: undefined,
        entryDate: undefined,
        staffType: undefined
      }
      this.dialogVisible = true
    },

    // 编辑按钮点击
    handleEdit(row) {
      this.dialogTitle = '编辑员工信息'
      this.form = { ...row }
      this.dialogVisible = true
    },

    // 查看按钮点击
    handleView(row) {
      // 实现查看详情功能
      this.$router.push(`/hrms/staff/detail/${row.id}`)
    },

    // 删除按钮点击
    handleDelete(row) {
      this.$confirm('确认删除该员工信息吗？', '警告', {
        type: 'warning'
      }).then(() => {
        request({
          url: `/vue-element-admin/staff/${row.id}`,
          method: 'delete'
        }).then(() => {
          this.$message.success('删除成功')
          this.getList()
        })
      })
    },

    // 批量删除
    handleBatchDelete() {
      if (!this.selectedIds.length) {
        this.$message.warning('请选择要删除的记录')
        return
      }
      this.$confirm(`确认删除选中的${this.selectedIds.length}条记录吗？`, '警告', {
        type: 'warning'
      }).then(() => {
        request({
          url: '/vue-element-admin/staff/batch',
          method: 'delete',
          data: this.selectedIds
        }).then(() => {
          this.$message.success('批量删除成功')
          this.getList()
        })
      })
    },

    // 导入按钮点击
    handleImport() {
      this.importVisible = true
    },

    // 导入成功回调
    handleImportSuccess(response) {
      if (response.code === 200) {
        this.$message.success('导入成功')
        this.importVisible = false
        this.getList()
      } else {
        this.$message.error(response.msg)
      }
    },

    // 导入失败回调
    handleImportError() {
      this.$message.error('导入失败')
    },

    // 下载模板
    downloadTemplate() {
      window.location.href = '/api/staff/template'
    },

    // 导出
    handleExport() {
      this.$confirm('确认导出所有员工数据吗？', '提示', {
        type: 'warning'
      }).then(() => {
        window.location.href = '/api/staff/export'
      })
    },

    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (valid) {
          try {
            if (this.form.id) {
              await request({
                url: '/vue-element-admin/staff',
                method: 'put',
                data: this.form
              })
              this.$message.success('修改成功')
            } else {
              await request({
                url: '/vue-element-admin/staff',
                method: 'post',
                data: this.form
              })
              this.$message.success('添加成功')
            }
            this.dialogVisible = false
            this.getList()
          } catch (error) {
            console.error('提交失败:', error)
          }
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.app-container {
  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    .table-operations {
      margin-bottom: 20px;
    }
  }

  .el-tag {
    margin-right: 5px;
  }

  .upload-demo {
    text-align: center;
  }
}
</style>
