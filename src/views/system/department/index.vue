<template>
  <div class="app-container">
    <h2>院系管理</h2>
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="请输入院系名称或代码"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleAdd">
        添加院系
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="departmentList"
      style="width: 100%"
      border
    >
      <el-table-column prop="name" label="院系名称" align="center" />
      <el-table-column prop="code" label="院系代码" align="center" />
      <el-table-column prop="director" label="院系主任" align="center" />
      <el-table-column prop="contact" label="联系方式" align="center" />
      <el-table-column prop="classCount" label="班级数" align="center" />
      <el-table-column prop="studentCount" label="学生数" align="center" />
      <el-table-column label="操作" align="center" width="300">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="success" size="mini" @click="handleClass(scope.row)">班级管理</el-button>
          <el-button type="danger" size="mini" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getDepartments"
    />

    <!-- 添加/编辑院系对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form ref="departmentForm" :model="departmentForm" :rules="rules" label-width="100px">
        <el-form-item label="院系名称" prop="name">
          <el-input v-model="departmentForm.name" placeholder="请输入院系名称" />
        </el-form-item>
        <el-form-item label="院系代码" prop="code">
          <el-input v-model="departmentForm.code" placeholder="请输入院系代码" />
        </el-form-item>
        <el-form-item label="院系主任" prop="director">
          <el-input v-model="departmentForm.director" placeholder="请输入院系主任姓名" />
        </el-form-item>
        <el-form-item label="联系方式" prop="contact">
          <el-input v-model="departmentForm.contact" placeholder="请输入联系方式" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getDepartmentList, addDepartment, updateDepartment, deleteDepartment } from '@/api/department'
import Pagination from '@/components/Pagination'

export default {
  name: 'Department',
  components: { Pagination },
  data() {
    return {
      departmentList: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      departmentForm: {
        id: undefined,
        name: '',
        code: '',
        director: '',
        contact: ''
      },
      rules: {
        name: [{ required: true, message: '请输入院系名称', trigger: 'blur' }],
        code: [{ required: true, message: '请输入院系代码', trigger: 'blur' }],
        director: [{ required: true, message: '请输入院系主任', trigger: 'blur' }],
        contact: [{ required: true, message: '请输入联系方式', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getDepartments()
  },
  methods: {
    async getDepartments() {
      this.listLoading = true
      try {
        const { data } = await getDepartmentList(this.listQuery)
        this.departmentList = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取院系列表失败:', error)
        this.$message.error('获取院系列表失败')
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getDepartments()
    },
    resetForm() {
      this.departmentForm = {
        id: undefined,
        name: '',
        code: '',
        director: '',
        contact: ''
      }
    },
    handleAdd() {
      this.dialogTitle = '添加院系'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.resetForm()
        this.$refs['departmentForm'].clearValidate()
      })
    },
    handleEdit(row) {
      this.dialogTitle = '编辑院系'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.departmentForm = { ...row }
        this.$refs['departmentForm'].clearValidate()
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该院系?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await deleteDepartment(row.id)
          this.$message.success('删除成功')
          this.getDepartments()
        } catch (error) {
          console.error('删除院系失败:', error)
          this.$message.error('删除院系失败')
        }
      })
    },
    handleClass(row) {
      this.$router.push({ path: `/system/class/${row.id}` })
    },
    async submitForm() {
      this.$refs['departmentForm'].validate(async(valid) => {
        if (valid) {
          try {
            if (this.departmentForm.id) {
              await updateDepartment(this.departmentForm)
              this.$message.success('更新成功')
            } else {
              await addDepartment(this.departmentForm)
              this.$message.success('添加成功')
            }
            this.dialogVisible = false
            this.getDepartments()
          } catch (error) {
            console.error('保存院系失败:', error)
            this.$message.error('保存院系失败')
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}
.filter-item {
  margin-right: 10px;
  margin-bottom: 10px;
}
</style>
