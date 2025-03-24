<template>
  <div class="dashboard-tenant-admin">
    <el-row :gutter="20">
      <el-col :span="6">
        <count-panel 
          title="总简历数" 
          :value="stats.totalResumes"
          icon="el-icon-document"
        />
      </el-col>
      <el-col :span="6">
        <count-panel 
          title="本月新增" 
          :value="stats.monthlyNewResumes"
          icon="el-icon-plus"
        />
      </el-col>
      <el-col :span="6">
        <count-panel 
          title="进行中职位" 
          :value="stats.activePositions"
          icon="el-icon-suitcase"
        />
      </el-col>
      <el-col :span="6">
        <count-panel 
          title="本月面试" 
          :value="stats.monthlyInterviews"
          icon="el-icon-date"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="chart-wrapper">
          <line-chart title="招聘趋势" />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="chart-wrapper">
          <pie-chart title="职位分布" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <recent-activities />
      </el-col>
      <el-col :span="12">
        <todo-list />
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'TenantAdminDashboard',
  data() {
    return {
      stats: {
        totalResumes: 0,
        monthlyNewResumes: 0,
        activePositions: 0,
        monthlyInterviews: 0
      }
    }
  }
}
</script> 