import Layout from '@/layout'

const transferRouter = {
  path: '/transfer',
  component: Layout,
  name: 'Transfer',
  meta: {
    title: '人事调动',
    icon: 'el-icon-refresh'
  },
  children: [
    {
      path: 'apply',
      component: () => import('@/views/transfer/apply'),
      name: 'TransferApply',
      meta: { title: '调动申请' }
    },
    {
      path: 'approve',
      component: () => import('@/views/transfer/approve'),
      name: 'TransferApprove',
      meta: { title: '调动审核' }
    },
    {
      path: 'order',
      component: () => import('@/views/transfer/order'),
      name: 'TransferOrder',
      meta: { title: '调令下发' }
    },
    {
      path: 'confirm',
      component: () => import('@/views/transfer/confirm'),
      name: 'TransferConfirm',
      meta: { title: '调令接收与确认' }
    }
  ]
}

export default transferRouter
