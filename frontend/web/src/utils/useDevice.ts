import { ref, onMounted, onUnmounted, readonly } from 'vue'

/**
 * 设备类型检测 composable
 *
 * 判断优先级：
 * 1. `matchMedia('(pointer: coarse)')` / `(hover: none)` —— 媒体查询优先
 *    Chrome DevTools 模拟移动设备时会正确切换，真实设备也准确。
 *    注意：userAgentData.mobile 不随 DevTools 模拟变化，不作为主判断。
 * 2. UA 正则兜底（Mobi/Android/iPhone/iPod）
 *
 * 不依赖屏幕断点（px），而是依据设备指针能力和 UA。
 */
function detectMobile(): boolean {
  if (typeof window === 'undefined') return false

  // 1. 媒体查询优先：触摸主输入设备 + 无 hover 能力
  //    Chrome DevTools 模拟移动设备时会正确切换这两个媒体查询，
  //    但 userAgentData.mobile 不会随 DevTools 模拟变化，因此不用它做主判断。
  const isCoarsePointer = window.matchMedia('(pointer: coarse)').matches
  const noHover = window.matchMedia('(hover: none)').matches
  if (isCoarsePointer || noHover) {
    return true
  }

  // 2. UA 兜底：适用于只有粗糙 UA 可用的情况
  const ua = navigator.userAgent
  if (/Mobi|Android|iPhone|iPod/i.test(ua)) {
    return true
  }

  return false
}

let _isMobile: ReturnType<typeof ref<boolean>> | null = null
let _isViewportTooSmall: ReturnType<typeof ref<boolean>> | null = null
// 媒体查询对象，用于监听变化（DevTools 切换设备等）
let _mqlCoarse: MediaQueryList | null = null
let _mqlHover: MediaQueryList | null = null

/**
 * 使用单例，确保全局状态一致。
 */
export function useDevice() {
  if (!_isMobile) {
    _isMobile = ref(detectMobile())

    // 监听媒体查询变化，支持 DevTools 动态切换设备类型
    if (typeof window !== 'undefined') {
      _mqlCoarse = window.matchMedia('(pointer: coarse)')
      _mqlHover = window.matchMedia('(hover: none)')
      const onMqlChange = () => {
        if (_isMobile) _isMobile.value = detectMobile()
      }
      _mqlCoarse.addEventListener('change', onMqlChange)
      _mqlHover.addEventListener('change', onMqlChange)
    }
  }
  if (!_isViewportTooSmall) {
    _isViewportTooSmall = ref(typeof window !== 'undefined' ? window.innerWidth < 768 : false)
  }

  const isMobile = _isMobile
  const isDesktop = ref(!isMobile.value)
  const isViewportTooSmall = _isViewportTooSmall

  function onResize() {
    if (_isViewportTooSmall) {
      _isViewportTooSmall.value = window.innerWidth < 768
    }
    // 设备类型通常不会因 resize 变化，但若媒体查询变化（如桌面横竖屏）可重新检测
    if (_isMobile) {
      const newVal = detectMobile()
      _isMobile.value = newVal
      isDesktop.value = !newVal
    }
  }

  onMounted(() => {
    window.addEventListener('resize', onResize, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('resize', onResize)
  })

  return {
    isMobile: readonly(isMobile),
    isDesktop: readonly(isDesktop),
    isViewportTooSmall: readonly(isViewportTooSmall),
  }
}
