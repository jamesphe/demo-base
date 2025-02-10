<template>
  <div class="app-container">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>岗位管理</span>
        <el-button
          style="float: right; padding: 3px 0"
          type="text"
          icon="el-icon-plus"
          @click="handleAdd"
        >新增</el-button>
      </div>

      <!-- 搜索区域 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="岗位名称">
          <el-input v-model="queryParams.name" placeholder="请输入岗位名称" clearable />
        </el-form-item>
        <el-form-item label="岗位编码">
          <el-input v-model="queryParams.code" placeholder="请输入岗位编码" clearable />
        </el-form-item>
        <el-form-item label="岗位类型">
          <el-select v-model="queryParams.type" placeholder="请选择岗位类型" clearable>
            <el-option
              v-for="item in positionTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable>
            <el-option label="启用" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery">查询</el-button>
          <el-button icon="el-icon-refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格区域 -->
      <el-table
        v-loading="loading"
        :data="positionList"
        style="width: 100%"
      >
        <el-table-column prop="name" label="岗位名称" />
        <el-table-column prop="code" label="岗位编码" />
        <el-table-column prop="typeName" label="岗位类型" />
        <el-table-column prop="orderNum" label="显示顺序" width="100" />
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
              {{ scope.row.status === 1 ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="scope">
            <el-button
              type="text"
              size="mini"
              @click="handleEdit(scope.row)"
            >编辑</el-button>
            <el-button
              type="text"
              size="mini"
              @click="handleDelete(scope.row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <pagination
        :hidden="total <= 0"
        :total="total"
        :page.sync="queryParams.pageNum"
        :limit.sync="queryParams.pageSize"
        @pagination="handlePagination"
      />

      <!-- 添加或修改岗位对话框 -->
      <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
        <el-form ref="form" :model="form" :rules="rules" label-width="80px">
          <el-form-item label="岗位名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入岗位名称" />
          </el-form-item>
          <el-form-item label="岗位编码" prop="code">
            <el-input v-model="form.code" placeholder="请输入岗位编码" />
          </el-form-item>
          <el-form-item label="岗位类型" prop="type">
            <el-select v-model="form.type" placeholder="请选择岗位类型">
              <el-option
                v-for="item in positionTypes"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="显示顺序" prop="orderNum">
            <el-input-number v-model="form.orderNum" :min="0" :max="999" />
          </el-form-item>
          <el-form-item label="岗位状态">
            <el-radio-group v-model="form.status">
              <el-radio :label="1">启用</el-radio>
              <el-radio :label="0">停用</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="岗位描述">
            <el-input v-model="form.description" type="textarea" placeholder="请输入岗位描述" />
          </el-form-item>
          <el-form-item label="任职要求">
            <el-input v-model="form.requirements" type="textarea" placeholder="请输入任职要求" />
          </el-form-item>
          <el-form-item label="岗位职责">
            <el-input v-model="form.duties" type="textarea" placeholder="请输入岗位职责" />
          </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import { listPosition, getPosition, addPosition, updatePosition, deletePosition } from '@/api/position'
import Pagination from '@/components/Pagination'

export default {
  name: 'Position',
  components: { Pagination },
  data() {
    return {
      // 遮罩层
      loading: false,
      // 总条数
      total: 0,
      // 岗位列表
      positionList: [],
      // 岗位类型选项
      positionTypes: [
        { value: 1, label: '教师岗位' },
        { value: 2, label: '行政岗位' },
        { value: 3, label: '教辅岗位' },
        { value: 4, label: '工勤岗位' }
      ],
      // 弹出层标题
      title: '',
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        name: undefined,
        code: undefined,
        type: undefined,
        status: undefined
      },
      // 表单参数
      form: {
        id: undefined,
        name: undefined,
        code: undefined,
        type: undefined,
        orderNum: 0,
        status: 1,
        description: undefined,
        requirements: undefined,
        duties: undefined
      },
      // 表单校验
      rules: {
        name: [
          { required: true, message: '岗位名称不能为空', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '岗位编码不能为空', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择岗位类型', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    /** 查询岗位列表 */
    async getList() {
      this.loading = true
      try {
        const response = await listPosition({
          ...this.queryParams,
          pageNum: Number(this.queryParams.pageNum) || 1,
          pageSize: Number(this.queryParams.pageSize) || 10,
          type: this.queryParams.type ? Number(this.queryParams.type) : undefined,
          status: this.queryParams.status ? Number(this.queryParams.status) : undefined
        })

        if (response.code === 20000 && response.data) {
          const { items = [], total = 0 } = response.data
          this.positionList = items
          this.total = Number(total) || 0
        } else {
          this.positionList = []
          this.total = 0
        }
      } catch (error) {
        console.error('获取岗位列表失败:', error)
        this.positionList = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    /** 搜索按钮操作 */
    handleQuery() {
      console.log('Handle query with params:', this.queryParams)
      this.queryParams.pageNum = 1
      this.getList()
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.total = 0
      this.queryParams = {
        pageNum: 1,
        pageSize: 10,
        name: undefined,
        code: undefined,
        type: undefined,
        status: undefined
      }
      this.handleQuery()
    },
    /** 新增按钮操作 */
    handleAdd() {
      console.log('Handle add')
      this.reset()
      this.open = true
      this.title = '添加岗位'
    },
    /** 编辑按钮操作 */
    async handleEdit(row) {
      console.log('Handle edit:', row)
      try {
        const response = await getPosition(row.id)
        console.log('Get position detail response:', response)
        this.form = response.data
        this.open = true
        this.title = '修改岗位'
      } catch (error) {
        console.error('获取岗位详情失败:', error)
      }
    },
    /** 提交按钮 */
    submitForm() {
      console.log('Submit form:', this.form)
      this.$refs.form.validate(async(valid) => {
        if (valid) {
          try {
            const submitData = {
              ...this.form,
              type: Number(this.form.type),
              status: Number(this.form.status),
              orderNum: Number(this.form.orderNum)
            }

            if (this.form.id) {
              const response = await updatePosition(submitData)
              console.log('Update position response:', response)
              this.$message.success('修改成功')
            } else {
              const response = await addPosition(submitData)
              console.log('Add position response:', response)
              this.$message.success('新增成功')
            }
            this.open = false
            this.getList()
          } catch (error) {
            console.error('提交失败:', error)
          }
        }
      })
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      this.$confirm('是否确认删除名称为"' + row.name + '"的岗位?', '警告', {
        type: 'warning'
      }).then(async() => {
        try {
          await deletePosition(row.id)
          this.$message.success('删除成功')
          this.getList()
        } catch (error) {
          console.error('删除失败:', error)
        }
      }).catch(() => {})
    },
    // 表单重置
    reset() {
      this.form = {
        id: undefined,
        name: undefined,
        code: undefined,
        type: undefined,
        orderNum: 0,
        status: 1,
        description: undefined,
        requirements: undefined,
        duties: undefined
      }
      if (this.$refs.form) {
        this.$refs.form.resetFields()
      }
    },
    /** 取消按钮 */
    cancel() {
      this.open = false
      this.reset()
    },
    /** 处理分页变化 */
    handlePagination({ page, limit }) {
      console.log('Pagination changed:', { page, limit })
      this.queryParams.pageNum = page
      this.queryParams.pageSize = limit
      this.getList()
    }
  }
}
</script>
