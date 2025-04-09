export const TRIAL_STATUS = {
  PENDING: 'pending',
  ACTIVE: 'active',
  REJECTED: 'rejected',
  EXPIRED: 'expired',
  NONE: 'none'
}

export const TRIAL_STATUS_MAP = {
  [TRIAL_STATUS.PENDING]: {
    text: '待审核',
    type: 'warning'
  },
  [TRIAL_STATUS.ACTIVE]: {
    text: '试用中',
    type: 'success'
  },
  [TRIAL_STATUS.REJECTED]: {
    text: '已拒绝',
    type: 'danger'
  },
  [TRIAL_STATUS.EXPIRED]: {
    text: '已过期',
    type: 'info'
  },
  [TRIAL_STATUS.NONE]: {
    text: '未申请',
    type: 'info'
  }
}
