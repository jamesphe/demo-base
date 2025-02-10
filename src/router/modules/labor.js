import Layout from '@/layout'

const laborRouter = {
  path: '/labor',
  component: Layout,
  name: 'LaborManage',
  meta: {
    title: '劳动关系管理',
    icon: 'form'
  },
  children: [
    {
      path: 'entry',
      component: () => import('@/views/labor/entry'),
      name: 'LaborEntry',
      meta: { title: '入职管理' }
    },
    {
      path: 'contract',
      component: () => import('@/views/labor/contract'),
      name: 'LaborContract',
      meta: { title: '合同管理' }
    },
    {
      path: 'retire',
      component: () => import('@/views/labor/retire'),
      name: 'LaborRetire',
      meta: { title: '离退休手续管理' }
    }
  ]
}

export default laborRouter
