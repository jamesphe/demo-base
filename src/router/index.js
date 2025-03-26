import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layout'
import { getToken } from '@/utils/auth'
import store from '@/store'

Vue.use(Router)

/**
 * constantRoutes
 * 基础路由 - 不需要权限验证
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
    name: 'login',
    component: () => import('@/views/login/index.vue'),
    hidden: true,
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true,
    meta: {
      title: '注册',
      requiresAuth: false
    }
  },
  {
    path: '/trial-application',
    component: () => import('@/views/trial-application/index'),
    name: 'TrialApplication',
    hidden: true,
    meta: {
      title: '申请免费试用',
      requiresAuth: false
    }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/index.vue'),
    hidden: true,
    meta: {
      title: '首页',
      requiresAuth: false
    }
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
  }
]

/**
 * asyncRoutes
 * 需要根据用户角色动态加载的路由
 */
export const asyncRoutes = [
  {
    path: '/dashboard',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/dashboard/index'),
        name: 'Dashboard',
        meta: {
          title: '控制台',
          icon: 'dashboard',
          affix: true,
          roles: ['admin', 'tenant_admin', 'tenant_hr']
        }
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
        meta: {
          title: '个人中心',
          icon: 'user',
          noCache: true,
          roles: ['admin', 'tenant_admin', 'tenant_hr', 'tenant_viewer']
        }
      }
    ]
  },
  // 职位管理
  {
    path: '/position',
    component: Layout,
    meta: {
      title: '职位管理',
      icon: 'el-icon-suitcase',
      roles: ['admin', 'tenant_admin', 'tenant_hr']
    },
    children: [
      {
        path: 'publish',
        component: () => import('@/views/position/publish'),
        name: 'PositionPublish',
        meta: {
          title: '职位发布',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'maintain',
        component: () => import('@/views/position/maintain'),
        name: 'PositionMaintain',
        meta: {
          title: '职位维护',
          roles: ['tenant_admin', 'tenant_hr']
        }
      }
    ]
  },
  // 简历管理
  {
    path: '/resume',
    component: Layout,
    meta: {
      title: '简历管理',
      icon: 'el-icon-document',
      roles: ['admin', 'tenant_admin', 'tenant_hr', 'tenant_viewer']
    },
    children: [
      {
        path: 'upload',
        component: () => import('@/views/resume/upload'),
        name: 'ResumeUpload',
        meta: {
          title: '简历上传',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'parse',
        component: () => import('@/views/resume/parse'),
        name: 'ResumeParse',
        meta: {
          title: '简历解析',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'storage',
        component: () => import('@/views/resume/storage'),
        name: 'ResumeStorage',
        meta: {
          title: '简历存储',
          roles: ['tenant_admin', 'tenant_hr', 'tenant_viewer']
        }
      },
      {
        path: 'search',
        component: () => import('@/views/resume/search'),
        name: 'ResumeSearch',
        meta: {
          title: '简历检索',
          roles: ['tenant_admin', 'tenant_hr', 'tenant_viewer']
        }
      },
      {
        path: 'ai-chat',
        name: 'ResumeAIChat',
        component: () => import('@/views/resume/ai-chat/index.vue'),
        meta: {
          title: 'AI简历助手',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'detail/:id',
        name: 'ResumeDetail',
        component: () => import('@/views/resume/detail/index.vue'),
        meta: {
          title: '简历详情',
          roles: ['tenant_admin', 'tenant_hr', 'tenant_viewer']
        },
        hidden: true
      }
    ]
  },
  // 候选人管理
  {
    path: '/candidate',
    component: Layout,
    name: 'Candidate',
    meta: {
      title: '候选管理',
      icon: 'el-icon-s-custom',
      roles: ['admin', 'tenant_admin', 'tenant_hr', 'tenant_viewer']
    },
    children: [
      {
        path: 'profile',
        component: () => import('@/views/candidate/profile'),
        name: 'CandidateProfile',
        meta: {
          title: '候选人档案',
          roles: ['tenant_admin', 'tenant_hr', 'tenant_viewer']
        }
      },
      {
        path: 'evaluation',
        component: () => import('@/views/candidate/evaluation'),
        name: 'CandidateEvaluation',
        meta: {
          title: '候选人评估',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'recommendation',
        component: () => import('@/views/candidate/recommendation'),
        name: 'CandidateRecommendation',
        meta: {
          title: '候选人推荐',
          roles: ['tenant_admin', 'tenant_hr']
        }
      }
    ]
  },
  // 面试管理
  {
    path: '/interview',
    component: Layout,
    meta: {
      title: '面试管理',
      icon: 'el-icon-date',
      roles: ['admin', 'tenant_admin', 'tenant_hr']
    },
    children: [
      {
        path: 'schedule',
        component: () => import('@/views/interview/schedule'),
        name: 'InterviewSchedule',
        meta: {
          title: '面试安排',
          roles: ['tenant_admin', 'tenant_hr']
        }
      },
      {
        path: 'record',
        component: () => import('@/views/interview/record'),
        name: 'InterviewRecord',
        meta: {
          title: '面试记录',
          roles: ['tenant_admin', 'tenant_hr']
        }
      }
    ]
  },
  // 招聘分析
  {
    path: '/analysis',
    component: Layout,
    meta: {
      title: '招聘分析',
      icon: 'el-icon-data-line',
      roles: ['admin', 'tenant_admin']
    },
    children: [
      {
        path: 'progress',
        component: () => import('@/views/analysis/progress'),
        name: 'AnalysisProgress',
        meta: {
          title: '招聘进度',
          roles: ['tenant_admin']
        }
      },
      {
        path: 'effect',
        component: () => import('@/views/analysis/effect'),
        name: 'AnalysisEffect',
        meta: {
          title: '招聘效果',
          roles: ['tenant_admin']
        }
      }
    ]
  },
  // 系统设置
  {
    path: '/settings',
    component: Layout,
    meta: {
      title: '系统设置',
      icon: 'el-icon-setting',
      roles: ['admin', 'tenant_admin']
    },
    children: [
      {
        path: 'user',
        component: () => import('@/views/settings/user'),
        name: 'SettingsUser',
        meta: {
          title: '用户管理',
          roles: ['tenant_admin']
        }
      },
      {
        path: 'role',
        component: () => import('@/views/settings/role'),
        name: 'SettingsRole',
        meta: {
          title: '角色管理',
          roles: ['tenant_admin']
        }
      },
      {
        path: 'permission',
        component: () => import('@/views/settings/permission'),
        name: 'SettingsPermission',
        meta: {
          title: '权限管理',
          roles: ['tenant_admin']
        }
      }
    ]
  },

  // 404 页面必须放在最后
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 全局导航守卫
router.beforeEach(async(to, from, next) => {
  // 获取token
  const token = localStorage.getItem('token') || getToken()

  if (token) {
    if (to.path === '/login') {
      // 已登录则跳转到dashboard
      next({ path: '/dashboard' })
    } else {
      // 判断当前用户是否已拉取完user_info信息
      const hasRoles = store.getters.roles && store.getters.roles.length > 0
      if (hasRoles) {
        next()
      } else {
        try {
          // 获取用户信息
          const { roles } = await store.dispatch('user/getInfo')

          // 根据roles权限生成可访问的路由表
          const accessRoutes = await store.dispatch('permission/generateRoutes', roles)

          // 动态添加可访问路由
          router.addRoutes(accessRoutes)

          // hack方法 确保addRoutes已完成
          next({ path: '/dashboard', replace: true })
        } catch (error) {
          // 移除 token 并跳转登录页
          await store.dispatch('user/resetToken')
          next(`/login?redirect=${to.path}`)
        }
      }
    }
  } else {
    // 没有token
    if (to.meta.requiresAuth === false) {
      // 在免登录白名单，直接进入
      next()
    } else {
      // 否则全部重定向到登录页
      next(`/login?redirect=${to.path}`)
    }
  }
})

export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher
}

export default router
