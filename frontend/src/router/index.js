import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layout'
import { getToken } from '@/utils/auth'
import store from '@/store'

Vue.use(Router)

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
    name: 'login',
    component: () => import('@/views/login/index.vue'),
    hidden: true,
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/login/qywx-callback',
    component: () => import('@/views/login/qywx-callback'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/trial-application',
    name: 'TrialApplication',
    component: () => import('@/views/trial-application/index'),
    hidden: true,
    meta: {
      title: '申请免费试用',
      requiresAuth: false
    }
  },
  {
    path: '/trial-application/terms',
    name: 'TermsOfService',
    component: () => import('@/views/trial-application/terms'),
    hidden: true,
    meta: {
      title: '服务条款',
      requiresAuth: false
    }
  },
  {
    path: '/trial-application/privacy',
    name: 'PrivacyPolicy',
    component: () => import('@/views/trial-application/privacy'),
    hidden: true,
    meta: {
      title: '隐私政策',
      requiresAuth: false
    }
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
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
          hasNavHeader: true,
          requiresAuth: true
        }
      }
    ]
  }
]

/**
 * asyncRoutes
 * 需要根据用户角色动态加载的路由
 */
export const asyncRoutes = [
  {
    path: '/tenant',
    component: Layout,
    meta: {
      title: '租户管理',
      icon: 'el-icon-s-home',
      roles: ['admin']
    },
    children: [
      {
        path: '',
        component: () => import('@/views/tenant/index'),
        name: 'TenantManagement',
        meta: {
          title: '租户列表',
          roles: ['admin']
        }
      },
      {
        path: 'trial',
        name: 'TenantTrial',
        component: () => import('@/views/tenant/trial'),
        meta: {
          title: '试用管理',
          roles: ['admin'],
          activeMenu: '/tenant/trial'
        }
      }
    ]
  },
  { path: '*', redirect: '/404', hidden: true },
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
      },
      {
        path: 'applications',
        component: () => import('@/views/position/applications'),
        name: 'PositionApplications',
        meta: {
          title: '职位申请',
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
          roles: ['admin', 'tenant_admin']
        }
      },
      {
        path: 'role',
        component: () => import('@/views/settings/role'),
        name: 'SettingsRole',
        meta: {
          title: '角色管理',
          roles: ['admin']
        }
      },
      {
        path: 'permission',
        component: () => import('@/views/settings/permission'),
        name: 'SettingsPermission',
        meta: {
          title: '权限管理',
          roles: ['admin']
        }
      }
    ]
  }
]

const createRouter = () => new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 全局导航守卫
router.beforeEach((to, from, next) => {
  // 可以在这里处理路由信息
  const routeInfo = {
    currentRoute: to.path,
    routeName: to.name,
    hasNavHeader: to.meta.hasNavHeader
  }

  // 使用命名空间提交 mutation
  store.commit('route/SET_ROUTE_INFO', routeInfo)

  // 获取token
  const token = localStorage.getItem('token') || getToken()

  //console.log('路由守卫 - 目标路由:', to)
  //console.log('路由守卫 - 来源路由:', from)

  // 如果路由需要权限验证
  if (to.meta.requiresAuth) {
    //console.log('路由守卫 - 需要权限验证')
    //console.log('路由守卫 - Token状态:', token ? '存在' : '不存在')
    if (!token) {
      //console.log('路由守卫 - 无Token，重定向到登录页')
      next({ name: 'login' })
      return
    }
  }

  // 直接放行，让permission.js中的守卫处理权限验证
  next()
})

export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher
}

export default router
