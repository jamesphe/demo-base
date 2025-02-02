<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="实训室名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select 
        v-model="listQuery.baseId" 
        placeholder="所属基地" 
        clearable 
        style="width: 200px" 
        class="filter-item"
        @change="handleFilter"
      >
        <el-option 
          v-for="item in baseList" 
          :key="item.id" 
          :label="item.name" 
          :value="item.id" 
        />
      </el-select>
      <el-select v-model="listQuery.status" placeholder="状态" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
        新增实训室
      </el-button>
    </div>

    <!-- 实训室列表 -->
    <el-table
      v-loading="listLoading"
      :data="roomList"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column prop="roomCode" label="实训室号" min-width="120" />
      <el-table-column prop="name" label="实训室名称" min-width="150" />
      <el-table-column prop="physicalRoomNo" label="房间号" min-width="100" />
      <el-table-column prop="managementUnitName" label="管理单位" min-width="150" />
      <el-table-column prop="baseName" label="所属基地" min-width="150" />
      <el-table-column prop="managerId" label="负责人工号" min-width="120" />
      <el-table-column prop="capacity" label="工位数" width="100" align="center" sortable="custom" />
      <el-table-column prop="deviceCount" label="设备数量" width="100" align="center" sortable="custom" />
      <el-table-column prop="buildingArea" label="建筑面积(㎡)" width="120" align="center" sortable="custom" />
      <el-table-column prop="weeklyClassHours" label="周课时数" width="100" align="center" sortable="custom" />
      <el-table-column label="状态" width="100" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTextFilter }}
          </el-tag>
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
    <el-dialog 
      :title="dialogStatus === 'create' ? '新增实训室' : '编辑实训室'" 
      :visible.sync="dialogFormVisible"
      width="65%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实训室号" prop="roomCode">
              <el-input v-model="temp.roomCode" placeholder="请输入实训室编号"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实训室名称" prop="name">
              <el-input v-model="temp.name" placeholder="请输入实训室名称"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属基地" prop="baseId">
              <el-select v-model="temp.baseId" class="filter-item" placeholder="请选择基地" style="width: 100%">
                <el-option 
                  v-for="item in baseList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="temp.status" class="filter-item" placeholder="请选择状态" style="width: 100%">
                <el-option 
                  v-for="item in statusOptions" 
                  :key="item.value" 
                  :label="item.label" 
                  :value="item.value"
                >
                  <el-tag :type="item.value | statusFilter" size="small">
                    {{ item.label }}
                  </el-tag>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="房间号" prop="physicalRoomNo">
              <el-input v-model="temp.physicalRoomNo" placeholder="请输入房间号"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="房间名称" prop="physicalRoomName">
              <el-input v-model="temp.physicalRoomName" placeholder="请输入房间名称"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="负责人工号" prop="managerId">
              <el-input v-model="temp.managerId" placeholder="请输入教工号">
                <el-button slot="append" icon="el-icon-user" />
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="建筑面积" prop="buildingArea">
              <el-input-number 
                v-model="temp.buildingArea" 
                :min="0" 
                :precision="2"
                style="width: 100%"
                placeholder="请输入建筑面积"
              >
                <template slot="append">㎡</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用面积" prop="usableArea">
              <el-input-number 
                v-model="temp.usableArea" 
                :min="0" 
                :precision="2"
                style="width: 100%"
                placeholder="请输入使用面积"
              >
                <template slot="append">㎡</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工位数" prop="capacity">
              <el-input-number 
                v-model="temp.capacity" 
                :min="1"
                style="width: 100%"
                placeholder="请输入工位数"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备台套数" prop="deviceCount">
              <el-input-number 
                v-model="temp.deviceCount" 
                :min="0"
                style="width: 100%"
                placeholder="请输入设备数量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每周课时数" prop="weeklyClassHours">
              <el-input-number 
                v-model="temp.weeklyClassHours" 
                :min="0"
                style="width: 100%"
                placeholder="请输入课时数"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="建立日期" prop="establishDate">
              <el-date-picker
                v-model="temp.establishDate"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="yyyy-MM-dd"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合作企业" prop="cooperativeCompany">
              <el-input v-model="temp.cooperativeCompany" placeholder="请输入合作企业名称"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="配套设施" prop="facilities">
          <el-input type="textarea" v-model="temp.facilities" :rows="2" placeholder="请输入配套设施信息"/>
        </el-form-item>

        <el-form-item label="备注">
          <el-input type="textarea" v-model="temp.remark" :rows="2" placeholder="请输入备注信息"/>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination'
import { getTrainingRooms } from '@/api/training-room'
import { getBaseList } from '@/api/base'

export default {
  name: 'TrainingRoom',
  components: { Pagination },
  filters: {
    statusFilter(status) {
      const statusMap = {
        available: 'success',    // 可用 - 绿色
        maintenance: 'warning',  // 维护中 - 黄色
        occupied: 'danger'       // 已预约 - 红色
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        available: '可用',
        maintenance: '维护中', 
        occupied: '已预约'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      listLoading: false,
      roomList: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        name: undefined,
        status: undefined,
        baseId: undefined,
        sort: undefined,
        order: undefined
      },
      statusOptions: [
        { label: '可用', value: 'available' },
        { label: '维修中', value: 'maintenance' },
        { label: '已预约', value: 'occupied' }
      ],
      dialogFormVisible: false,
      dialogStatus: '',
      temp: {
        id: undefined,
        roomCode: '',
        name: '',
        baseId: undefined,
        managementUnitId: '',
        managementUnitName: '',
        establishDate: '',
        managerId: '',
        capacity: 1,
        physicalRoomNo: '',
        physicalRoomName: '',
        cooperativeCompany: '',
        buildingArea: 0,
        usableArea: 0,
        deviceCount: 0,
        facilities: '',
        weeklyClassHours: 0,
        status: 'available',
        remark: ''
      },
      rules: {
        roomCode: [{ required: true, message: '实训室号不能为空', trigger: 'blur' }],
        name: [{ required: true, message: '实训室名称不能为空', trigger: 'blur' }],
        baseId: [{ required: true, message: '请选择所属基地', trigger: 'change' }],
        managerId: [{ required: true, message: '负责人教工号不能为空', trigger: 'blur' }],
        physicalRoomNo: [{ required: true, message: '房间号不能为空', trigger: 'blur' }],
        capacity: [{ required: true, message: '请设置工位数', trigger: 'blur' }],
        status: [{ required: true, message: '请选择状态', trigger: 'change' }]
      },
      trainingRooms: [],
      baseList: []
    }
  },
  created() {
    this.getBaseList()
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.listLoading = true
      try {
        const { data } = await getTrainingRooms(this.listQuery)
        this.roomList = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取实训室数据失败:', error)
      }
      this.listLoading = false
    },
    getList() {
      this.fetchData()
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        roomCode: '',
        name: '',
        baseId: undefined,
        managementUnitId: '',
        managementUnitName: '',
        establishDate: '',
        managerId: '',
        capacity: 1,
        physicalRoomNo: '',
        physicalRoomName: '',
        cooperativeCompany: '',
        buildingArea: 0,
        usableArea: 0,
        deviceCount: 0,
        facilities: '',
        weeklyClassHours: 0,
        status: 'available',
        remark: ''
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
          // TODO: 调用API创建实训室
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
          // TODO: 调用API更新实训室
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
      this.$confirm('确认删除该实训室?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // TODO: 调用API删除实训室
        this.$message({
          type: 'success',
          message: '删除成功!'
        })
        this.getList()
      })
    },
    handleViewDetails(row) {
      this.$router.push(`/base/training-room/detail/${row.id}`)
    },
    async getBaseList() {
      try {
        const { data } = await getBaseList()
        this.baseList = data.items
      } catch (error) {
        console.error('获取实训基地列表失败:', error)
      }
    },
    handleSort({ prop, order }) {
      this.listQuery.sort = prop
      this.listQuery.order = order
      this.fetchData()
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

:deep(.el-dialog__body) {
  padding: 20px 40px;
}

:deep(.el-form-item__label) {
  font-weight: bold;
}

:deep(.el-input-number) {
  width: 100%;
}
</style> 