<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.keyword"
        placeholder="设备名称/编号"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.status"
        placeholder="设备状态"
        style="width: 120px"
        class="filter-item"
        clearable
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="listQuery.roomId"
        placeholder="所属实训室"
        style="width: 200px"
        class="filter-item"
        clearable
      >
        <el-option
          v-for="room in roomOptions"
          :key="room.id"
          :label="room.name"
          :value="room.id"
        />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
        新增设备
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="equipmentList"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column prop="equipmentCode" label="设备编号" width="120" />
      <el-table-column prop="name" label="设备名称" min-width="120" />
      <el-table-column prop="model" label="设备型号" width="120" />
      <el-table-column prop="price" label="价格" width="120" align="right">
        <template slot-scope="{row}">
          ¥ {{ row.price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column prop="roomName" label="所属实训室" min-width="120" />
      <el-table-column prop="manager" label="负责人" width="100" />
      <el-table-column prop="purchaseDate" label="购置日期" width="100" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTextFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="300" fixed="right">
        <template slot-scope="{row}">
          <div style="white-space: nowrap;">
            <el-button type="primary" size="mini" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="success" size="mini" @click="handleViewDetails(row)">
              查看详情
            </el-button>
            <el-button type="danger" size="mini" @click="handleDelete(row)">
              删除
            </el-button>
          </div>
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
    <el-dialog :title="dialogStatus === 'create' ? '新增设备' : '编辑设备'" :visible.sync="dialogFormVisible" width="65%">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备编号" prop="equipmentCode">
              <el-input v-model="temp.equipmentCode" placeholder="请输入设备编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="temp.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备型号" prop="model">
              <el-input v-model="temp.model" placeholder="请输入设备型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态" prop="status">
              <el-select v-model="temp.status" class="filter-item" placeholder="请选择状态" style="width: 100%">
                <el-option
                  v-for="item in statusOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="价格" prop="price">
              <el-input-number
                v-model="temp.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                placeholder="请输入价格"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number
                v-model="temp.quantity"
                :min="1"
                style="width: 100%"
                placeholder="请输入数量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="购买年限" prop="lifespan">
              <el-input-number
                v-model="temp.lifespan"
                :min="1"
                style="width: 100%"
                placeholder="请输入年限"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属实训室" prop="roomId">
              <el-select
                v-model="temp.roomId"
                placeholder="请选择实训室"
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="room in roomOptions"
                  :key="room.id"
                  :label="room.name"
                  :value="room.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="manager">
              <el-input v-model="temp.manager" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购置日期" prop="purchaseDate">
              <el-date-picker
                v-model="temp.purchaseDate"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="yyyy-MM-dd"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier">
              <el-input v-model="temp.supplier" placeholder="请输入供应商" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="生产厂家" prop="manufacturer">
          <el-input v-model="temp.manufacturer" placeholder="请输入生产厂家" />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input v-model="temp.remark" type="textarea" :rows="2" />
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
import { getEquipmentList, addEquipment, updateEquipment, deleteEquipment } from '@/api/equipment'
import Pagination from '@/components/Pagination'

export default {
  name: 'EquipmentInfo',
  components: { Pagination },
  filters: {
    statusFilter(status) {
      const statusMap = {
        normal: 'success',
        maintenance: 'warning',
        scrapped: 'danger'
      }
      return statusMap[status]
    },
    statusTextFilter(status) {
      const statusMap = {
        normal: '正常',
        maintenance: '维修中',
        scrapped: '已报废'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      listLoading: false,
      equipmentList: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: undefined,
        status: undefined,
        roomId: undefined
      },
      statusOptions: [
        { label: '正常', value: 'normal' },
        { label: '维修中', value: 'maintenance' },
        { label: '已报废', value: 'scrapped' }
      ],
      roomOptions: [], // 实训室选项
      dialogFormVisible: false,
      dialogStatus: '',
      temp: {
        id: undefined,
        equipmentCode: '',
        name: '',
        model: '',
        status: 'normal',
        price: 0,
        quantity: 1,
        lifespan: 1,
        roomId: undefined,
        roomName: '',
        manager: '',
        purchaseDate: '',
        supplier: '',
        manufacturer: '',
        remark: ''
      },
      rules: {
        equipmentCode: [{ required: true, message: '设备编号不能为空', trigger: 'blur' }],
        name: [{ required: true, message: '设备名称不能为空', trigger: 'blur' }],
        model: [{ required: true, message: '设备型号不能为空', trigger: 'blur' }],
        roomId: [{ required: true, message: '请选择所属实训室', trigger: 'change' }],
        manager: [{ required: true, message: '负责人不能为空', trigger: 'blur' }],
        purchaseDate: [{ required: true, message: '请选择购置日期', trigger: 'change' }]
      }
    }
  },
  created() {
    this.getList()
    // TODO: 获取实训室选项列表
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await getEquipmentList(this.listQuery)
        this.equipmentList = data.items
        this.total = data.total
      } catch (error) {
        console.error('获取设备列表失败:', error)
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
        equipmentCode: '',
        name: '',
        model: '',
        status: 'normal',
        price: 0,
        quantity: 1,
        lifespan: 1,
        roomId: undefined,
        roomName: '',
        manager: '',
        purchaseDate: '',
        supplier: '',
        manufacturer: '',
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
      this.$refs['dataForm'].validate(async(valid) => {
        if (valid) {
          try {
            await addEquipment(this.temp)
            this.dialogFormVisible = false
            this.$message({
              type: 'success',
              message: '创建成功'
            })
            this.getList()
          } catch (error) {
            console.error('创建设备失败:', error)
          }
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
      this.$refs['dataForm'].validate(async(valid) => {
        if (valid) {
          try {
            await updateEquipment(this.temp)
            this.dialogFormVisible = false
            this.$message({
              type: 'success',
              message: '更新成功'
            })
            this.getList()
          } catch (error) {
            console.error('更新设备失败:', error)
          }
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该设备?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await deleteEquipment(row.id)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.getList()
        } catch (error) {
          console.error('删除设备失败:', error)
        }
      })
    },
    handleViewDetails(row) {
      this.$router.push(`/equipment/info/detail/${row.id}`)
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
