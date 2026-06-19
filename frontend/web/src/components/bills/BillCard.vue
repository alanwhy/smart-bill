<template>
  <!-- Skeleton placeholder（等待识别中） -->
  <div v-if="bill.isPlaceholder" class="card-hover p-4">
    <div class="flex items-start justify-between animate-pulse">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-10 h-10 rounded-lg bg-border/60 flex-shrink-0" />
          <div class="flex-1 space-y-1.5">
            <div class="h-3.5 bg-border/60 rounded w-2/3" />
            <div class="h-2.5 bg-border/40 rounded w-1/3" />
          </div>
        </div>
        <div class="h-2.5 bg-border/40 rounded w-1/4 mt-1" />
      </div>
      <div class="ml-4">
        <div class="h-5 bg-border/60 rounded w-16" />
      </div>
    </div>
    <p class="text-xs text-text-muted mt-2 flex items-center gap-1">
      <svg class="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      识别中...
    </p>
  </div>

  <!-- ===== 移动端：左滑显示操作按钮 ===== -->
  <div
    v-else-if="isMobile"
    ref="cardWrapperRef"
    class="relative overflow-hidden rounded-xl"
    @touchstart="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- 底层操作按钮（左滑后显现） -->
    <div class="absolute inset-y-0 right-0 flex items-stretch">
      <button
        @click.stop="handleEdit"
        class="flex items-center justify-center w-16 bg-accent/80 active:bg-accent transition-colors duration-150 cursor-pointer"
        aria-label="编辑"
      >
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      </button>
      <button
        @click.stop="handleDelete"
        class="flex items-center justify-center w-16 bg-error active:bg-error/80 transition-colors duration-150 cursor-pointer"
        aria-label="删除"
      >
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>

    <!-- 前景卡片内容 -->
    <div
      class="card-hover p-4 relative z-10"
      :class="{ 'transition-transform duration-200 ease-out': !isDragging }"
      :style="{
        transform: `translateX(${currentOffsetX}px)`,
        borderTopRightRadius: currentOffsetX < 0 ? '0px' : '',
        borderBottomRightRadius: currentOffsetX < 0 ? '0px' : '',
      }"
      @click="onCardClick"
    >
      <div class="flex items-start justify-between">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
              <span class="text-lg">{{ bill.category?.icon || '📦' }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-semibold text-text truncate">{{ bill.merchant_name }}</h3>
              <p class="text-xs text-text-muted">{{ categoryPath }}</p>
            </div>
          </div>
          <p class="text-xs text-text-muted">{{ formatDate(bill.transaction_date) }}</p>
          <p v-if="bill.description" class="text-xs text-text-muted mt-0.5 truncate">{{ bill.description }}</p>
        </div>
        <div class="ml-4 text-right">
          <p class="text-base font-bold" :class="bill.value >= 0 ? 'text-success' : 'text-primary'">
            {{ bill.value >= 0 ? '+' : '-' }}¥{{ Math.abs(bill.value).toFixed(2) }}
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- ===== 桌面端：hover 浮现编辑/删除按钮 ===== -->
  <div v-else class="group relative card-hover p-4">
    <div class="flex items-start justify-between">
      <!-- 左侧内容 -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
            <span class="text-lg">{{ bill.category?.icon || '📦' }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-semibold text-text truncate">{{ bill.merchant_name }}</h3>
            <p class="text-xs text-text-muted">{{ categoryPath }}</p>
          </div>
        </div>
        <p class="text-xs text-text-muted">{{ formatDate(bill.transaction_date) }}</p>
        <p v-if="bill.description" class="text-xs text-text-muted mt-0.5 truncate">{{ bill.description }}</p>
      </div>

      <!-- 右侧：金额 + hover 操作按钮 -->
      <div class="ml-4 flex items-center gap-2 flex-shrink-0">
        <!-- 操作按钮组：hover 时浮现 -->
        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
          <button
            @click.stop="handleEdit"
            class="p-1.5 rounded-lg bg-accent/20 hover:bg-accent/40 text-accent transition-colors duration-150"
            aria-label="编辑"
            title="编辑"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click.stop="handleDelete"
            class="p-1.5 rounded-lg bg-error/20 hover:bg-error/40 text-error transition-colors duration-150"
            aria-label="删除"
            title="删除"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <!-- 金额 -->
        <p class="text-base font-bold" :class="bill.value >= 0 ? 'text-success' : 'text-primary'">
          {{ bill.value >= 0 ? '+' : '-' }}¥{{ Math.abs(bill.value).toFixed(2) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BillRecord } from '@/types/bill'
import { format, parseISO } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useDevice } from '@/utils/useDevice'
import { useCategoriesStore } from '@/stores/categories'

// ---- 模块级共享状态：当前左滑展开的卡片 id ----
// 所有 BillCard 实例共享，确保同一时刻最多一条展开
const activeSwipeId = ref<number | null>(null)

const { isMobile } = useDevice()
const categoriesStore = useCategoriesStore()

const props = defineProps<{
  bill: BillRecord
}>()

const emit = defineEmits<{
  edit: [bill: BillRecord]
  delete: [bill: BillRecord]
}>()

/** 构建多级分类路径，如「餐饮 / 午餐」 */
const categoryPath = computed(() => {
  const cat = props.bill.category
  if (!cat) return '其他'
  const path: string[] = [cat.name]
  let parentId = cat.parent_id
  while (parentId != null) {
    const parent = categoriesStore.byId.get(parentId)
    if (!parent) break
    path.unshift(parent.name)
    parentId = parent.parent_id ?? null
  }
  return path.join(' / ')
})

const ACTION_WIDTH = 128
const SWIPE_THRESHOLD = 40

const cardWrapperRef = ref<HTMLElement | null>(null)
const dragOffset = ref(0)
const isDragging = ref(false)

const isOpen = computed(() => activeSwipeId.value === props.bill.id)

// isOpen 从 true → false 时强制归零，防止中间态残留
watch(isOpen, (val) => {
  if (!val) {
    dragOffset.value = 0
    isDragging.value = false
  }
})

const currentOffsetX = computed(() => {
  if (isDragging.value) return dragOffset.value
  return isOpen.value ? -ACTION_WIDTH : 0
})

let startX = 0
let startY = 0
let isHorizontal: boolean | null = null
// 记录 touchstart 时是否已展开，避免 touchmove 中重新读 isOpen 产生竞态
let wasOpenAtStart = false

function onTouchStart(e: TouchEvent) {
  wasOpenAtStart = isOpen.value
  // 触摸新卡片时，立即关闭其他已展开的卡片
  if (activeSwipeId.value !== null && activeSwipeId.value !== props.bill.id) {
    activeSwipeId.value = null
  }
  startX = e.touches[0].clientX
  startY = e.touches[0].clientY
  dragOffset.value = wasOpenAtStart ? -ACTION_WIDTH : 0
  isDragging.value = false
  isHorizontal = null
}

function onTouchMove(e: TouchEvent) {
  const dx = e.touches[0].clientX - startX
  const dy = e.touches[0].clientY - startY

  if (isHorizontal === null) {
    if (Math.abs(dx) > Math.abs(dy) + 3) {
      isHorizontal = true
      isDragging.value = true
    } else if (Math.abs(dy) > Math.abs(dx) + 3) {
      isHorizontal = false
      return
    } else {
      return
    }
  }

  if (!isHorizontal) return

  const base = wasOpenAtStart ? -ACTION_WIDTH : 0
  let next = base + dx
  next = Math.min(0, Math.max(-ACTION_WIDTH, next))
  dragOffset.value = next
}

function onTouchEnd() {
  if (!isDragging.value) {
    isDragging.value = false
    return
  }
  isDragging.value = false

  // 以 touchstart 时的状态决定阈值，避免中途 activeSwipeId 变化影响判断
  const threshold = wasOpenAtStart ? ACTION_WIDTH - SWIPE_THRESHOLD : SWIPE_THRESHOLD

  if (dragOffset.value < -threshold) {
    activeSwipeId.value = props.bill.id
  } else {
    if (activeSwipeId.value === props.bill.id) {
      activeSwipeId.value = null
    }
  }
}

// 全局 pointerdown 监听：点击当前展开卡片之外的任何位置时收回
function onGlobalPointerDown(e: PointerEvent) {
  if (!isOpen.value) return
  if (cardWrapperRef.value && !cardWrapperRef.value.contains(e.target as Node)) {
    activeSwipeId.value = null
  }
}

onMounted(() => {
  if (isMobile.value) {
    document.addEventListener('pointerdown', onGlobalPointerDown, { passive: true })
  }
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', onGlobalPointerDown)
})

function close() {
  if (activeSwipeId.value === props.bill.id) {
    activeSwipeId.value = null
  }
}

function onCardClick() {
  if (isOpen.value) close()
}

function handleEdit() {
  close()
  emit('edit', props.bill)
}

function handleDelete() {
  close()
  emit('delete', props.bill)
}

const formatDate = (dateStr: string): string => {
  try {
    return format(parseISO(dateStr), 'MM月dd日 HH:mm', { locale: zhCN })
  } catch {
    return dateStr
  }
}
</script>
