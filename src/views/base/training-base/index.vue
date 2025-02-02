<template>
  <div class="app-container">
    <h2>实训基地管理</h2>
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="基地名称/单位名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.typeCode" placeholder="基地类别" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">搜索</el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleAdd">添加基地</el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="baseList"
      style="width: 100%"
      border
    >
      <el-table-column prop="id" label="基地编号" width="100" align="center" />
      <el-table-column prop="name" label="基地名称" min-width="150" />
      <el-table-column prop="deptName" label="管理单位" min-width="120" />
      <el-table-column prop="createTime" label="建立日期" width="120" align="center" />
      <el-table-column prop="typeCode" label="基地类别" width="150" align="center" />
      <el-table-column prop="manager" label="联系人" width="100" align="center" />
      <el-table-column prop="contact" label="联系电话" width="120" align="center" />
      <el-table-column prop="roomCount" label="实训室数量" width="100" align="center" />
      <el-table-column label="操作" align="center" width="300">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="success" size="mini" @click="handleRoom(scope.row)">实训室</el-button>
          <el-button type="danger" size="mini" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getBases"
    />

    <!-- 添加/编辑实训基地对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="650px">
      <el-form ref="baseForm" :model="baseForm" :rules="rules" label-width="120px">
        <el-form-item label="基地名称" prop="name">
          <el-input v-model="baseForm.name" />
        </el-form-item>
        <el-form-item label="管理单位" prop="deptName">
          <el-input v-model="baseForm.deptName" />
        </el-form-item>
        <el-form-item label="基地类别" prop="typeCode">
          <el-select v-model="baseForm.typeCode" style="width: 100%">
            <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="依托单位" prop="supportUnit">
          <el-input v-model="baseForm.supportUnit" />
        </el-form-item>
        <el-form-item label="适应专业" prop="majors">
          <el-input v-model="baseForm.majors" type="textarea" :rows="2" placeholder="多个专业用逗号分隔" />
        </el-form-item>
        <el-form-item label="合作企业" prop="partner">
          <el-input v-model="baseForm.partner" />
        </el-form-item>
        <el-form-item label="联系人" prop="manager">
          <el-input v-model="baseForm.manager" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact">
          <el-input v-model="baseForm.contact" />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="baseForm.description" type="textarea" :rows="3" />
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
import { getBaseList, addBase, updateBase, deleteBase } from '@/api/base'
import Pagination from '@/components/Pagination'

export default {
  name: 'TrainingBase',
  components: { Pagination },
  data() {
    return {
      baseList: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: '',
        typeCode: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      typeOptions: [
        { label: '校内实训基地', value: '01-校内实训基地' },
        { label: '校外实训基地', value: '02-校外实训基地' },
        { label: '生产性实训基地', value: '03-生产性实训基地' }
      ],
      baseForm: {
        id: undefined,
        name: '',
        deptId: '',
        deptName: '',
        createTime: '',
        supportUnit: '',
        majors: '',
        partner: '',
        typeCode: '',
        manager: '',
        contact: '',
        description: ''
      },
      rules: {
        name: [{ required: true, message: '请输入基地名称', trigger: 'blur' }],
        deptName: [{ required: true, message: '请输入管理单位', trigger: 'blur' }],
        typeCode: [{ required: true, message: '请选择基地类别', trigger: 'change' }],
        manager: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
        contact: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getBases()
  },
  methods: {
    async getBases() {
      this.listLoading = true
      try {
        const { data } = await getBaseList(this.listQuery)
        this.baseList = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取实训基地列表失败:', error)
        this.$message.error('获取实训基地列表失败')
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getBases()
    },
    resetForm() {
      this.baseForm = {
        id: undefined,
        name: '',
        deptId: '',
        deptName: '',
        createTime: '',
        supportUnit: '',
        majors: '',
        partner: '',
        typeCode: '',
        manager: '',
        contact: '',
        description: ''
      }
    },
    handleAdd() {
      this.dialogTitle = '添加实训基地'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.resetForm()
        this.$refs['baseForm'].clearValidate()
      })
    },
    handleEdit(row) {
      this.dialogTitle = '编辑实训基地'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.baseForm = { ...row }
        this.$refs['baseForm'].clearValidate()
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该实训基地?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await deleteBase(row.id)
          this.$message.success('删除成功')
          this.getBases()
        } catch (error) {
          console.error('删除实训基地失败:', error)
          this.$message.error('删除实训基地失败')
        }
      })
    },
    handleRoom(row) {
      this.$router.push({ path: `/base/room/${row.id}` })
    },
    async submitForm() {
      this.$refs['baseForm'].validate(async(valid) => {
        if (valid) {
          try {
            if (this.baseForm.id) {
              await updateBase(this.baseForm)
              this.$message.success('更新成功')
            } else {
              await addBase(this.baseForm)
              this.$message.success('添加成功')
            }
            this.dialogVisible = false
            this.getBases()
          } catch (error) {
            console.error('保存实训基地失败:', error)
            this.$message.error('保存实训基地失败')
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
