<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="项目名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-input
        v-model="listQuery.projectCode"
        placeholder="项目编号"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.majorCode"
        placeholder="归口专业"
        style="width: 200px"
        class="filter-item"
        clearable
      >
        <el-option
          v-for="item in majorOptions"
          :key="item.code"
          :label="item.name"
          :value="item.code"
        />
      </el-select>
      <el-select
        v-model="listQuery.semester"
        placeholder="学期"
        style="width: 150px"
        class="filter-item"
        clearable
      >
        <el-option label="第一学期" value="1" />
        <el-option label="第二学期" value="2" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
        新增项目
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="projectList"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column prop="projectCode" label="项目编号" width="120" />
      <el-table-column prop="name" label="项目名称" min-width="150" />
      <el-table-column prop="isVirtual" label="虚拟仿真" width="100" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.isVirtual ? 'success' : 'info'">
            {{ row.isVirtual ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="majorName" label="归口专业" min-width="120" />
      <el-table-column prop="courseCode" label="计划课程号" width="120" />
      <el-table-column prop="moduleCount" label="模块数量" width="100" align="center" />
      <el-table-column prop="trainingHours" label="实训课时" width="100" align="center" />
      <el-table-column prop="academicYear" label="学年" width="100" align="center" />
      <el-table-column prop="semester" label="学期" width="100" align="center">
        <template slot-scope="{row}">
          第{{ row.semester }}学期
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="250" fixed="right">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="success" size="mini" @click="handleViewDetails(row)">
            查看详情
          </el-button>
          <el-button type="danger" size="mini" @click="handleDelete(row)">
            删除
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

    <!-- 编辑/新增对话框 -->
    <el-dialog :title="dialogStatus === 'create' ? '新增实训项目' : '编辑实训项目'" :visible.sync="dialogFormVisible" width="70%">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目编号" prop="projectCode">
              <el-input v-model="temp.projectCode" placeholder="请输入项目编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目名称" prop="name">
              <el-input v-model="temp.name" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="归口专业号" prop="majorCode">
              <el-input v-model="temp.majorCode" placeholder="请输入专业编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="归口专业名称" prop="majorName">
              <el-input v-model="temp.majorName" placeholder="请输入专业名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划课程号" prop="courseCode">
              <el-input v-model="temp.courseCode" placeholder="请输入课程编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否虚拟仿真" prop="isVirtual">
              <el-switch
                v-model="temp.isVirtual"
                active-text="是"
                inactive-text="否"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模块数量" prop="moduleCount">
              <el-input-number v-model="temp.moduleCount" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实训课时数" prop="trainingHours">
              <el-input-number v-model="temp.trainingHours" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学年" prop="academicYear">
              <el-input v-model="temp.academicYear" placeholder="如：2023-2024" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学期" prop="semester">
              <el-select v-model="temp.semester" placeholder="请选择" style="width: 100%">
                <el-option label="第一学期" value="1" />
                <el-option label="第二学期" value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否对外服务" prop="isExternalService">
              <el-switch
                v-model="temp.isExternalService"
                active-text="是"
                inactive-text="否"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="配套实训资源" prop="trainingResources">
          <el-input v-model="temp.trainingResources" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="典型任务名称" prop="typicalTasks">
          <el-input v-model="temp.typicalTasks" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="技能要求" prop="skillRequirements">
          <el-input v-model="temp.skillRequirements" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="考核方式" prop="assessmentMethod">
          <el-input v-model="temp.assessmentMethod" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="其他实训地点" prop="otherTrainingLocations">
          <el-input v-model="temp.otherTrainingLocations" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="校内实训室号" prop="trainingRoomCode">
          <el-select
            v-model="temp.trainingRoomCode"
            placeholder="请选择实训室"
            style="width: 100%"
            filterable
            clearable
          >
            <el-option
              v-for="room in trainingRoomOptions"
              :key="room.roomCode"
              :label="`${room.roomCode} - ${room.name}`"
              :value="room.roomCode"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { getTrainingProjects, createTrainingProject, updateTrainingProject, deleteTrainingProject } from '@/api/training-project'

export default {
  name: 'TrainingProject',
  components: { Pagination },
  data() {
    return {
      projectList: [],
      total: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 10,
        name: undefined,
        projectCode: undefined,
        majorCode: undefined,
        semester: undefined
      },
      dialogFormVisible: false,
      dialogStatus: '',
      temp: {
        id: undefined,
        projectCode: '',
        name: '',
        isVirtual: false,
        majorCode: '',
        majorName: '',
        courseCode: '',
        trainingResources: '',
        typicalTasks: '',
        skillRequirements: '',
        assessmentMethod: '',
        moduleCount: 1,
        trainingHours: 0,
        isExternalService: false,
        academicYear: '',
        semester: '1',
        otherTrainingLocations: '',
        trainingRoomCode: ''
      },
      rules: {
        projectCode: [{ required: true, message: '项目编号不能为空', trigger: 'blur' }],
        name: [{ required: true, message: '项目名称不能为空', trigger: 'blur' }],
        majorCode: [{ required: true, message: '归口专业号不能为空', trigger: 'blur' }],
        majorName: [{ required: true, message: '归口专业名称不能为空', trigger: 'blur' }],
        courseCode: [{ required: true, message: '计划课程号不能为空', trigger: 'blur' }],
        academicYear: [{ required: true, message: '学年不能为空', trigger: 'blur' }],
        semester: [{ required: true, message: '请选择学期', trigger: 'change' }]
      },
      majorOptions: [], // 专业选项
      trainingRoomOptions: [] // 实训室选项
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getTrainingProjects(this.listQuery)
        this.projectList = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取实训项目列表失败:', error)
      }
      this.listLoading = false
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        projectCode: '',
        name: '',
        isVirtual: false,
        majorCode: '',
        majorName: '',
        courseCode: '',
        trainingResources: '',
        typicalTasks: '',
        skillRequirements: '',
        assessmentMethod: '',
        moduleCount: 1,
        trainingHours: 0,
        isExternalService: false,
        academicYear: '',
        semester: '1',
        otherTrainingLocations: '',
        trainingRoomCode: ''
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
          // TODO: 调用API创建项目
          this.dialogFormVisible = false
          this.$message({
            type: 'success',
            message: '创建成功'
          })
          this.getList()
        }
      })
    },
    handleEdit(row) {
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
          // TODO: 调用API更新项目
          this.dialogFormVisible = false
          this.$message({
            type: 'success',
            message: '更新成功'
          })
          this.getList()
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该实训项目?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: 调用API删除项目
        this.$message({
          type: 'success',
          message: '删除成功!'
        })
        this.getList()
      })
    },
    handleViewDetails(row) {
      this.$router.push(`/base/training-project/detail/${row.id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.filter-container {
  padding-bottom: 10px;
  .filter-item {
    margin-right: 10px;
    vertical-align: top;
  }
}

.dialog-footer {
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
