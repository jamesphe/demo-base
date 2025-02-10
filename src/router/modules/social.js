import Layout from '@/layout'

const socialRouter = {
  path: '/social',
  component: Layout,
  name: 'SocialManage',
  meta: {
    title: '社保管理',
    icon: 'el-icon-umbrella'
  },
  children: [
    {
      path: 'base',
      component: () => import('@/views/social/base'),
      name: 'SocialBase',
      meta: { title: '社保缴费基数设置' }
    },
    {
      path: 'info',
      component: () => import('@/views/social/info'),
      name: 'SocialInfo',
      meta: { title: '社保信息管理' }
    },
    {
      path: 'change',
      component: () => import('@/views/social/change'),
      name: 'SocialChange',
      meta: { title: '信息变更登记' }
    },
    {
      path: 'transfer',
      component: () => import('@/views/social/transfer'),
      name: 'SocialTransfer',
      meta: { title: '内部调动管理' }
    },
    {
      path: 'staff',
      component: () => import('@/views/social/staff'),
      name: 'SocialStaff',
      meta: { title: '增员/减员管理' }
    },
    {
      path: 'statistics',
      component: () => import('@/views/social/statistics'),
      name: 'SocialStatistics',
      meta: { title: '养老失业统计' }
    },
    {
      path: 'course',
      component: () => import('@/views/social/course'),
      name: 'SocialCourse',
      meta: { title: '课时社保登记审核' }
    }
  ]
}

export default socialRouter
