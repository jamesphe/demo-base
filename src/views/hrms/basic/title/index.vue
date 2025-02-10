<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="请输入职称名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.level" placeholder="职称等级" clearable class="filter-item" style="width: 130px">
        <el-option
          v-for="item in levelOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select v-model="listQuery.category" placeholder="职称类别" clearable class="filter-item" style="width: 130px">
        <el-option
          v-for="item in categoryOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        新增职称
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="职称编码" prop="code" align="center" width="120">
        <template slot-scope="{row}">
          <span>{{ row.code }}</span>
        </template>
      </el-table-column>

      <el-table-column label="职称名称" prop="name" align="center" min-width="120">
        <template slot-scope="{row}">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="职称等级" prop="levelName" align="center" width="120">
        <template slot-scope="{row}">
          <span>{{ row.levelName }}</span>
        </template>
      </el-table-column>

      <el-table-column label="职称类别" prop="categoryName" align="center" width="120">
        <template slot-scope="{row}">
          <span>{{ row.categoryName }}</span>
        </template>
      </el-table-column>

      <el-table-column label="所需学历" prop="education" align="center" width="100">
        <template slot-scope="{row}">
          <span>{{ row.education }}</span>
        </template>
      </el-table-column>

      <el-table-column label="工作年限" prop="workYear" align="center" width="100">
        <template slot-scope="{row}">
          <span>{{ row.workYear }}</span>
        </template>
      </el-table-column>

      <el-table-column label="聘任年限" prop="appointmentPeriod" align="center" width="100">
        <template slot-scope="{row}">
          <span>{{ row.appointmentPeriod }}</span>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status === 1 ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            编辑
          </el-button>
          <el-button v-if="row.status === 1" size="mini" type="warning" @click="handleModifyStatus(row,0)">
            停用
          </el-button>
          <el-button v-else size="mini" type="success" @click="handleModifyStatus(row,1)">
            启用
          </el-button>
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

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="650px">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
        class="title-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职称编码" prop="code">
              <el-input v-model="temp.code" placeholder="请输入职称编码" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称名称" prop="name">
              <el-input v-model="temp.name" placeholder="请输入职称名称" clearable />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职称等级" prop="level">
              <el-select v-model="temp.level" class="filter-item" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in levelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <span style="float: left">{{ item.label }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称类别" prop="category">
              <el-select v-model="temp.category" class="filter-item" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                >
                  <span style="float: left">{{ item.label }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所需学历" prop="education">
              <el-select v-model="temp.education" class="filter-item" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in educationOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                >
                  <span style="float: left">{{ item }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作年限" prop="workYear">
              <el-select v-model="temp.workYear" class="filter-item" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in workYearOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                >
                  <span style="float: left">{{ item }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="聘任年限" prop="appointmentPeriod">
              <el-select v-model="temp.appointmentPeriod" class="filter-item" placeholder="请选择" style="width: 100%">
                <el-option
                  v-for="item in appointmentPeriodOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                >
                  <span style="float: left">{{ item }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="temp.status">
                <el-radio :label="1">启用</el-radio>
                <el-radio :label="0">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="评审条件" prop="requirement">
          <el-input
            v-model="temp.requirement"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 5 }"
            placeholder="请输入评审条件说明"
          />
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { fetchList, createTitle, updateTitle } from '@/api/title'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'

export default {
  name: 'Title',
  components: { Pagination },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        1: 'success',
        0: 'info'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        keyword: undefined,
        level: undefined,
        category: undefined
      },
      levelOptions: [
        { label: '正高级', value: '1' },
        { label: '副高级', value: '2' },
        { label: '中级', value: '3' },
        { label: '初级', value: '4' }
      ],
      categoryOptions: [
        { label: '教师系列', value: '1' },
        { label: '实验系列', value: '2' },
        { label: '工程系列', value: '3' },
        { label: '研究系列', value: '4' },
        { label: '技能系列', value: '5' }
      ],
      educationOptions: ['博士', '硕士', '本科', '专科'],
      workYearOptions: ['5年以上', '3年以上', '2年以上', '1年以上'],
      appointmentPeriodOptions: ['长期', '3年', '2年', '1年'],
      temp: {
        id: undefined,
        code: '',
        name: '',
        level: '',
        category: '',
        education: '',
        workYear: '',
        appointmentPeriod: '',
        requirement: '',
        status: 1
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑职称',
        create: '新增职称'
      },
      rules: {
        code: [{ required: true, message: '职称编码必填', trigger: 'blur' }],
        name: [{ required: true, message: '职称名称必填', trigger: 'blur' }],
        level: [{ required: true, message: '职称等级必选', trigger: 'change' }],
        category: [{ required: true, message: '职称类别必选', trigger: 'change' }],
        education: [{ required: true, message: '所需学历必选', trigger: 'change' }],
        workYear: [{ required: true, message: '工作年限必选', trigger: 'change' }],
        appointmentPeriod: [{ required: true, message: '聘任年限必选', trigger: 'change' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        code: '',
        name: '',
        level: '',
        category: '',
        education: '',
        workYear: '',
        appointmentPeriod: '',
        requirement: '',
        status: 1
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createTitle(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateTitle(tempData).then(() => {
            const index = this.list.findIndex(v => v.id === this.temp.id)
            this.list.splice(index, 1, this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作成功',
        type: 'success'
      })
      row.status = status
    }
  }
}
</script>

<style lang="scss" scoped>
.title-form {
  padding: 20px 20px 0;

  .el-select {
    width: 100%;
  }

  .el-textarea {
    width: 100%;
  }

  ::v-deep .el-form-item {
    margin-bottom: 20px;

    .el-form-item__label {
      font-weight: 500;
      color: #606266;
    }

    .el-form-item__content {
      .el-input__inner,
      .el-textarea__inner {
        &:hover,
        &:focus {
          border-color: #409EFF;
        }
      }
    }
  }
}

.dialog-footer {
  text-align: right;
  padding: 20px;

  .el-button {
    padding: 9px 20px;
    font-size: 14px;
    border-radius: 4px;

    & + .el-button {
      margin-left: 10px;
    }
  }
}

.el-select-dropdown__item {
  padding: 0 20px;

  span {
    padding: 8px 0;
  }
}
</style>
