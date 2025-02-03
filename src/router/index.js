import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * constantRoutes
 * 不需要权限的基础路由
 */
export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect/index')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index'),
        name: 'Dashboard',
        meta: { title: '首页', icon: 'el-icon-s-home' }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/index',
    hidden: true,
    children: [
      {
        path: 'index',
        component: () => import('@/views/profile/index'),
        name: 'Profile',
        meta: { title: '个人中心', icon: 'user', noCache: true }
      }
    ]
  },
  // 简历管理
  {
    path: '/resume',
    component: Layout,
    meta: { title: '简历管理', icon: 'el-icon-document' },
    children: [
      {
        path: 'upload',
        component: () => import('@/views/resume/upload'),
        name: 'ResumeUpload',
        meta: { title: '简历上传' }
      },
      {
        path: 'parse',
        component: () => import('@/views/resume/parse'),
        name: 'ResumeParse',
        meta: { title: '简历解析' }
      },
      {
        path: 'storage',
        component: () => import('@/views/resume/storage'),
        name: 'ResumeStorage',
        meta: { title: '简历存储' }
      },
      {
        path: 'search',
        component: () => import('@/views/resume/search'),
        name: 'ResumeSearch',
        meta: { title: '简历检索' }
      }
    ]
  },
  // 候选人管理
  {
    path: '/candidate',
    component: Layout,
    name: 'Candidate',
    meta: { title: '候选管理', icon: 'el-icon-s-custom' },
    children: [
      {
        path: 'profile',
        component: () => import('@/views/candidate/profile'),
        name: 'CandidateProfile',
        meta: { title: '候选人档案' }
      },
      {
        path: 'evaluation',
        component: () => import('@/views/candidate/evaluation'),
        name: 'CandidateEvaluation',
        meta: { title: '候选人评估' }
      },
      {
        path: 'recommendation',
        component: () => import('@/views/candidate/recommendation'),
        name: 'CandidateRecommendation',
        meta: { title: '候选人推荐' }
      }
    ]
  },
  // 职位管理
  {
    path: '/position',
    component: Layout,
    meta: { title: '职位管理', icon: 'el-icon-suitcase' },
    children: [
      {
        path: 'publish',
        component: () => import('@/views/position/publish'),
        name: 'PositionPublish',
        meta: { title: '职位发布' }
      },
      {
        path: 'maintain',
        component: () => import('@/views/position/maintain'),
        name: 'PositionMaintain',
        meta: { title: '职位维护' }
      }
    ]
  },
  // 面试管理
  {
    path: '/interview',
    component: Layout,
    meta: { title: '面试管理', icon: 'el-icon-date' },
    children: [
      {
        path: 'schedule',
        component: () => import('@/views/interview/schedule'),
        name: 'InterviewSchedule',
        meta: { title: '面试安排' }
      },
      {
        path: 'record',
        component: () => import('@/views/interview/record'),
        name: 'InterviewRecord',
        meta: { title: '面试记录' }
      }
    ]
  },
  // 招聘分析
  {
    path: '/analysis',
    component: Layout,
    meta: { title: '招聘分析', icon: 'el-icon-data-line' },
    children: [
      {
        path: 'progress',
        component: () => import('@/views/analysis/progress'),
        name: 'AnalysisProgress',
        meta: { title: '招聘进度' }
      },
      {
        path: 'effect',
        component: () => import('@/views/analysis/effect'),
        name: 'AnalysisEffect',
        meta: { title: '招聘效果' }
      }
    ]
  },
  // 系统设置
  {
    path: '/settings',
    component: Layout,
    meta: { title: '系统设置', icon: 'el-icon-setting' },
    children: [
      {
        path: 'user',
        component: () => import('@/views/settings/user'),
        name: 'SettingsUser',
        meta: { title: '用户管理' }
      },
      {
        path: 'role',
        component: () => import('@/views/settings/role'),
        name: 'SettingsRole',
        meta: { title: '角色管理' }
      },
      {
        path: 'permission',
        component: () => import('@/views/settings/permission'),
        name: 'SettingsPermission',
        meta: { title: '权限管理' }
      }
    ]
  }
]

/**
 * asyncRoutes
 * 需要根据用户角色动态加载的路由
 */
export const asyncRoutes = [
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher
}

export default router
