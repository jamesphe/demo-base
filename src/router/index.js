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
        meta: { title: 'Dashboard', icon: 'dashboard', affix: true }
      }
    ]
  }
]

/**
 * asyncRoutes
 * 需要根据用户角色动态加载的路由
 */
export const asyncRoutes = [
  // 实训基础数据管理
  {
    path: '/base',
    component: Layout,
    redirect: '/base/training-base',
    name: 'Base',
    meta: { title: '实训基地', icon: 'education' },
    children: [
      {
        path: 'training-base',
        component: () => import('@/views/base/training-base/index'),
        name: 'TrainingBase',
        meta: { title: '基地管理' }
      },
      {
        path: 'training-room',
        component: () => import('@/views/base/training-room/index'),
        name: 'TrainingRoom',
        meta: { title: '实训室管理' }
      },
      {
        path: 'training-room/detail/:id',
        component: () => import('@/views/base/training-room/detail'),
        name: 'TrainingRoomDetail',
        meta: { title: '实训室详情', activeMenu: '/base/training-room' },
        hidden: true
      },
      {
        path: 'training-project',
        component: () => import('@/views/base/training-project/index'),
        name: 'TrainingProject',
        meta: { title: '实训项目' }
      },
      {
        path: 'training-project/detail/:id',
        component: () => import('@/views/base/training-project/detail'),
        name: 'TrainingProjectDetail',
        meta: { title: '实训项目详情', activeMenu: '/base/training-project' },
        hidden: true
      }
    ]
  },

  // 实训设备管理
  {
    path: '/equipment',
    component: Layout,
    redirect: '/equipment/info',
    name: 'Equipment',
    meta: { title: '设备管理', icon: 'el-icon-cpu', roles: ['admin', 'teacher'] },
    children: [
      {
        path: 'info',
        component: () => import('@/views/equipment/info'),
        name: 'EquipmentInfo',
        meta: { title: '设备信息管理' }
      },
      {
        path: 'info/detail/:id',
        component: () => import('@/views/equipment/info/detail'),
        name: 'EquipmentDetail',
        meta: { title: '设备详情', activeMenu: '/equipment/info' },
        hidden: true
      },
      {
        path: 'approval',
        component: () => import('@/views/equipment/approval/index'),
        name: 'EquipmentApproval',
        meta: { title: '设备申报审核' }
      },
      {
        path: 'purchase',
        component: () => import('@/views/equipment/purchase'),
        name: 'EquipmentPurchase',
        meta: { title: '设备采购验收' }
      },
      {
        path: 'maintain',
        component: () => import('@/views/equipment/maintain'),
        name: 'EquipmentMaintain',
        meta: { title: '设备日常管理' }
      },
      {
        path: 'inventory',
        component: () => import('@/views/equipment/inventory'),
        name: 'EquipmentInventory',
        meta: { title: '设备盘点记录' }
      }
    ]
  },

  // 实训耗材管理
  {
    path: '/consumable',
    component: Layout,
    redirect: '/consumable/apply',
    name: 'Consumable',
    meta: { title: '耗材管理', icon: 'el-icon-box', roles: ['admin', 'teacher'] },
    children: [
      {
        path: 'apply',
        component: () => import('@/views/consumable/apply'),
        name: 'ConsumableApply',
        meta: { title: '耗材申报审核' }
      },
      {
        path: 'purchase',
        component: () => import('@/views/consumable/purchase'),
        name: 'ConsumablePurchase',
        meta: { title: '耗材采购入库' }
      },
      {
        path: 'stock',
        component: () => import('@/views/consumable/stock'),
        name: 'ConsumableStock',
        meta: { title: '耗材库存管理' }
      },
      {
        path: 'use',
        component: () => import('@/views/consumable/use'),
        name: 'ConsumableUse',
        meta: { title: '耗材领用统计' }
      }
    ]
  },

  // 实训课程管理
  {
    path: '/course',
    component: Layout,
    redirect: '/course/plan',
    name: 'Course',
    meta: { title: '课程管理', icon: 'el-icon-reading', roles: ['admin', 'teacher'] },
    children: [
      {
        path: 'plan',
        component: () => import('@/views/course/plan'),
        name: 'CoursePlan',
        meta: { title: '课程计划课表' }
      },
      {
        path: 'attendance',
        component: () => import('@/views/course/attendance'),
        name: 'CourseAttendance',
        meta: { title: '考勤课堂互动' }
      },
      {
        path: 'log',
        component: () => import('@/views/course/log'),
        name: 'CourseLog',
        meta: { title: '实训日志管理' }
      },
      {
        path: 'repair',
        component: () => import('@/views/course/repair'),
        name: 'CourseRepair',
        meta: { title: '设备损坏维修' }
      },
      {
        path: 'grade',
        component: () => import('@/views/course/grade'),
        name: 'CourseGrade',
        meta: { title: '实训成绩评估' }
      }
    ]
  },

  // 系统管理
  {
    path: '/system',
    component: Layout,
    redirect: '/system/user',
    name: 'System',
    meta: {
      title: '系统管理',
      icon: 'system',
      roles: ['admin']
    },
    children: [
      {
        path: 'user',
        component: () => import('@/views/system/user'),
        name: 'User',
        meta: {
          title: '用户管理',
          icon: 'user'
        }
      },
      {
        path: 'role',
        component: () => import('@/views/system/role'),
        name: 'Role',
        meta: {
          title: '角色管理',
          icon: 'peoples'
        }
      },
      {
        path: 'menu',
        component: () => import('@/views/system/menu'),
        name: 'Menu',
        meta: {
          title: '菜单管理',
          icon: 'tree'
        }
      },
      {
        path: 'department',
        component: () => import('@/views/system/department'),
        name: 'Department',
        meta: {
          title: '院系管理',
          icon: 'tree-table'
        }
      }
    ]
  },

  // 数据统计分析
  {
    path: '/statistics',
    component: Layout,
    redirect: '/statistics/course',
    name: 'Statistics',
    meta: { title: '统计分析', icon: 'el-icon-data-analysis', roles: ['admin'] },
    children: [
      {
        path: 'course',
        component: () => import('@/views/statistics/course'),
        name: 'CourseStatistics',
        meta: { title: '课程设备统计' }
      },
      {
        path: 'student',
        component: () => import('@/views/statistics/student'),
        name: 'StudentStatistics',
        meta: { title: '学生成绩统计' }
      }
    ]
  },

  // 404 页面必须放在最后
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
