<template>
  <div class="job-status">
    <el-form label-width="120px">
      <el-form-item label="求职状态">
        <el-select v-model="status" placeholder="请选择">
          <el-option label="在职找工作" value="在职找工作" />
          <el-option label="离职找工作" value="离职找工作" />
          <el-option label="暂不找工作" value="暂不找工作" />
        </el-select>
      </el-form-item>

      <el-form-item label="期望工作地">
        <el-cascader
          v-model="expectedLocation"
          :options="locationOptions"
          placeholder="请选择工作地点"
        />
      </el-form-item>

      <el-form-item label="期望薪资">
        <el-input-number v-model="salaryMin" :min="0" :step="1000" />
        <span class="mx-2">至</span>
        <el-input-number v-model="salaryMax" :min="0" :step="1000" />
      </el-form-item>

      <el-form-item label="到岗时间">
        <el-select v-model="availableTime" placeholder="请选择">
          <el-option label="随时到岗" value="随时到岗" />
          <el-option label="一周内" value="一周内" />
          <el-option label="一个月内" value="一个月内" />
        </el-select>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'JobStatus',
  data() {
    return {
      status: '',
      expectedLocation: [],
      salaryMin: 0,
      salaryMax: 0,
      availableTime: '',
      locationOptions: [] // 需要添加地区数据
    }
  }
}
</script>
