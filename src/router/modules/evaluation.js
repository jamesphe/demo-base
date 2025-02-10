import Layout from '@/layout'

const evaluationRouter = {
  path: '/evaluation',
  component: Layout,
  name: 'Evaluation',
  meta: {
    title: '教职工考核',
    icon: 'el-icon-s-check'
  },
  children: [
    {
      path: 'setting',
      component: () => import('@/views/evaluation/setting'),
      name: 'EvaluationSetting',
      meta: { title: '考核类别与指标设置' }
    },
    {
      path: 'record',
      component: () => import('@/views/evaluation/record'),
      name: 'EvaluationRecord',
      meta: { title: '考核结果登记' }
    },
    {
      path: 'query',
      component: () => import('@/views/evaluation/query'),
      name: 'EvaluationQuery',
      meta: { title: '考核结果查询与反馈' }
    }
  ]
}

export default evaluationRouter
