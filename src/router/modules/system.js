import Layout from '@/layout'

const systemRouter = {
  path: '/system',
  component: Layout,
  name: 'System',
  meta: {
    title: '系统设置',
    icon: 'el-icon-setting'
  },
  children: [
    {
      path: 'user',
      component: () => import('@/views/system/user'),
      name: 'User',
      meta: { title: '用户管理' }
    },
    {
      path: 'role',
      component: () => import('@/views/system/role'),
      name: 'Role',
      meta: { title: '角色权限管理' }
    },
    {
      path: 'api',
      component: () => import('@/views/system/api'),
      name: 'Api',
      meta: { title: '数据接口与集成配置' }
    },
    {
      path: 'log',
      component: () => import('@/views/system/log'),
      name: 'Log',
      meta: { title: '日志管理' }
    },
    {
      path: 'param',
      component: () => import('@/views/system/param'),
      name: 'Param',
      meta: { title: '系统参数设置' }
    },
    {
      path: 'backup',
      component: () => import('@/views/system/backup'),
      name: 'Backup',
      meta: { title: '数据备份与恢复' }
    }
  ]
}

export default systemRouter
