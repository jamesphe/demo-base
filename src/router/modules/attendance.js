import Layout from '@/layout'

const attendanceRouter = {
  path: '/attendance',
  component: Layout,
  name: 'Attendance',
  meta: {
    title: '考勤管理',
    icon: 'el-icon-date'
  },
  children: [
    {
      path: 'leave',
      component: () => import('@/views/attendance/leave'),
      name: 'Leave',
      meta: { title: '请销假管理' },
      children: [
        {
          path: 'apply',
          component: () => import('@/views/attendance/leave/apply'),
          name: 'LeaveApply',
          meta: { title: '请假申请' }
        },
        {
          path: 'approve',
          component: () => import('@/views/attendance/leave/approve'),
          name: 'LeaveApprove',
          meta: { title: '请假审核' }
        },
        {
          path: 'query',
          component: () => import('@/views/attendance/leave/query'),
          name: 'LeaveQuery',
          meta: { title: '请假查询' }
        }
      ]
    },
    {
      path: 'check',
      component: () => import('@/views/attendance/check'),
      name: 'Check',
      meta: { title: '考勤打卡管理' },
      children: [
        {
          path: 'sign',
          component: () => import('@/views/attendance/check/sign'),
          name: 'CheckSign',
          meta: { title: '在线签到/签退' }
        },
        {
          path: 'appeal',
          component: () => import('@/views/attendance/check/appeal'),
          name: 'CheckAppeal',
          meta: { title: '异常申诉与处理' }
        },
        {
          path: 'report',
          component: () => import('@/views/attendance/check/report'),
          name: 'CheckReport',
          meta: { title: '考勤信息查询与报表生成' }
        }
      ]
    }
  ]
}

export default attendanceRouter
