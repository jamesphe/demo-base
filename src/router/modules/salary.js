import Layout from '@/layout'

const salaryRouter = {
  path: '/salary',
  component: Layout,
  name: 'SalaryManage',
  meta: {
    title: '薪资管理',
    icon: 'money'
  },
  children: [
    {
      path: 'setting',
      component: () => import('@/views/salary/setting'),
      name: 'SalarySettingPage',
      meta: { title: '薪资项目设置' }
    },
    {
      path: 'base',
      component: () => import('@/views/salary/base'),
      name: 'SalaryBasePage',
      meta: { title: '基本工资录入与调整' }
    },
    {
      path: 'course',
      component: () => import('@/views/salary/course'),
      name: 'SalaryCoursePage',
      meta: { title: '课时工资计算' }
    },
    {
      path: 'hr',
      component: () => import('@/views/salary/hr'),
      name: 'SalaryHRPage',
      meta: { title: '人事处工资录入与审核' }
    },
    {
      path: 'payment',
      component: () => import('@/views/salary/payment'),
      name: 'SalaryPaymentPage',
      meta: { title: '薪资发放管理' }
    },
    {
      path: 'report',
      component: () => import('@/views/salary/report'),
      name: 'SalaryReportPage',
      meta: { title: '薪资查询与统计报表' }
    }
  ]
}

export default salaryRouter
