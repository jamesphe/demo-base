import Layout from '@/layout'

const hrmsRouter = {
  path: '/hrms',
  component: Layout,
  redirect: '/hrms/basic/organization',
  name: 'HRMS',
  meta: {
    title: '人力资源管理',
    icon: 'peoples'
  },
  children: [
    // 基础信息维护
    {
      path: 'basic',
      component: { render: h => h('router-view') },
      redirect: '/hrms/basic/organization',
      name: 'Basic',
      meta: { title: '基础信息维护' },
      children: [
        {
          path: 'organization',
          component: () => import('@/views/hrms/basic/organization/index'),
          name: 'Organization',
          meta: { title: '机构管理' }
        },
        {
          path: 'position',
          component: () => import('@/views/hrms/basic/position/index'),
          name: 'Position',
          meta: { title: '岗位/职位管理' }
        },
        {
          path: 'title',
          component: () => import('@/views/hrms/basic/title/index'),
          name: 'Title',
          meta: { title: '职称管理' }
        },
        {
          path: 'staff',
          component: () => import('@/views/hrms/basic/staff/index'),
          name: 'Staff',
          meta: { title: '教职工信息管理' }
        }
      ]
    },

    // 劳动关系维护
    {
      path: 'labor',
      name: 'Labor',
      component: () => import('@/views/hrms/labor/index'),
      meta: { title: '劳动关系维护' },
      children: [
        {
          path: 'entry',
          component: () => import('@/views/hrms/labor/entry'),
          name: 'Entry',
          meta: { title: '入职管理' }
        },
        {
          path: 'contract',
          component: () => import('@/views/hrms/labor/contract'),
          name: 'Contract',
          meta: { title: '合同管理' }
        },
        {
          path: 'certificate',
          component: () => import('@/views/hrms/labor/certificate'),
          name: 'Certificate',
          meta: { title: '证件管理' }
        }
      ]
    },

    // 薪酬维护
    {
      path: 'salary',
      name: 'Salary',
      component: () => import('@/views/hrms/salary/index'),
      meta: { title: '薪酬维护' },
      children: [
        {
          path: 'base',
          component: () => import('@/views/hrms/salary/base'),
          name: 'SalaryBase',
          meta: { title: '基本工资录入与调整' }
        },
        {
          path: 'course',
          component: () => import('@/views/hrms/salary/course'),
          name: 'SalaryCourse',
          meta: { title: '课时工资管理' }
        },
        {
          path: 'hr',
          component: () => import('@/views/hrms/salary/hr'),
          name: 'SalaryHR',
          meta: { title: '人事处工资录入与待审核' }
        }
      ]
    },

    // 培训维护
    {
      path: 'training',
      name: 'Training',
      component: () => import('@/views/hrms/training/index'),
      meta: { title: '培训维护' },
      children: [
        {
          path: 'plan',
          component: () => import('@/views/hrms/training/plan'),
          name: 'TrainingPlan',
          meta: { title: '培训计划制定与审批' }
        },
        {
          path: 'sign',
          component: () => import('@/views/hrms/training/sign'),
          name: 'TrainingSign',
          meta: { title: '培训报名与签到管理' }
        },
        {
          path: 'feedback',
          component: () => import('@/views/hrms/training/feedback'),
          name: 'TrainingFeedback',
          meta: { title: '培训评价与反馈' }
        }
      ]
    },

    // 考核维护
    {
      path: 'assessment',
      name: 'Assessment',
      component: () => import('@/views/hrms/assessment/index'),
      meta: { title: '考核维护' },
      children: [
        {
          path: 'hr',
          component: () => import('@/views/hrms/assessment/hr'),
          name: 'AssessmentHR',
          meta: { title: '人事处考核管理' }
        },
        {
          path: 'course',
          component: () => import('@/views/hrms/assessment/course'),
          name: 'AssessmentCourse',
          meta: { title: '课时考核管理' }
        }
      ]
    }
  ]
}

export default hrmsRouter
