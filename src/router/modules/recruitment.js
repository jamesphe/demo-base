import Layout from '@/layout'

const recruitmentRouter = {
  path: '/recruitment',
  component: Layout,
  name: 'Recruitment',
  meta: {
    title: '招聘管理',
    icon: 'user'
  },
  children: [
    {
      path: 'plan',
      component: () => import('@/views/recruitment/plan'),
      name: 'RecruitmentPlan',
      meta: { title: '招聘计划维护' }
    },
    {
      path: 'post',
      component: () => import('@/views/recruitment/post'),
      name: 'RecruitmentPost',
      meta: { title: '岗位上报' }
    }
    // ... 其他招聘管理子菜单
  ]
}

export default recruitmentRouter
