/**
 * 月度账单周期日期计算工具
 *
 * 支持自定义起始日：如 cycle_start_day=15 代表每月 15 日到次月 14 日为一个周期。
 * offset=0 → 当前周期；offset=-1 → 上一周期；offset=1 → 下一周期（以此类推）
 */

export interface CycleDates {
  startDate: string  // yyyy-MM-dd
  endDate: string    // yyyy-MM-dd
  label: string      // 如「本月支出」「上月支出」「本周期支出」
}

/**
 * 将 Date 格式化为 yyyy-MM-dd
 */
function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/**
 * 获取指定月份的最后一天
 */
function lastDayOfMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate()
}

/**
 * 计算指定周期的起止日期
 *
 * @param cycleStartDay - 周期起始日（1-28）
 * @param offset        - 0=当前周期, -1=上一周期, 1=下一周期
 * @returns CycleDates
 */
export function getCycleDates(cycleStartDay: number, offset: number = 0): CycleDates {
  const day = Math.max(1, Math.min(28, cycleStartDay))
  const today = new Date()
  const todayDate = today.getDate()

  // 判断「当前周期」的起始年月：
  // 若今天 >= 起始日，则当前周期起始是「本月 startDay」
  // 若今天 < 起始日，则当前周期起始是「上月 startDay」
  let currentCycleYear: number
  let currentCycleMonth: number // 1-12

  if (todayDate >= day) {
    currentCycleYear = today.getFullYear()
    currentCycleMonth = today.getMonth() + 1
  } else {
    // 上月
    const d = new Date(today.getFullYear(), today.getMonth() - 1, 1)
    currentCycleYear = d.getFullYear()
    currentCycleMonth = d.getMonth() + 1
  }

  // 加上 offset，计算目标周期起始年月
  const totalMonths = (currentCycleYear - 1) * 12 + (currentCycleMonth - 1) + offset
  const targetYear = Math.floor(totalMonths / 12) + 1
  const targetMonth = (totalMonths % 12) + 1

  // 周期起始日期
  const startDate = new Date(targetYear, targetMonth - 1, day)

  // 周期结束日期：下一个月的 day-1（即下个周期起始日前一天）
  const nextMonthTotalMonths = totalMonths + 1
  const nextYear = Math.floor(nextMonthTotalMonths / 12) + 1
  const nextMonth = (nextMonthTotalMonths % 12) + 1
  const endDayMax = lastDayOfMonth(nextYear, nextMonth)
  const endDayNum = Math.min(day - 1 === 0 ? endDayMax : day - 1, endDayMax)
  const endDate = new Date(nextYear, nextMonth - 1, endDayNum)

  // 标签逻辑：cycleStartDay=1 时使用「月」术语，其他使用「周期」
  const isStandardMonth = day === 1
  let label: string
  if (offset === 0) {
    label = isStandardMonth ? '本月支出' : '本周期支出'
  } else if (offset === -1) {
    label = isStandardMonth ? '上月支出' : '上周期支出'
  } else {
    label = `${isStandardMonth ? '月' : '周期'}支出`
  }

  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate),
    label,
  }
}
