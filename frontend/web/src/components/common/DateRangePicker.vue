<template>
  <div class="relative" ref="rootRef">
    <!-- 触发输入框 -->
    <button
      type="button"
      class="flex items-center gap-2 h-8 px-3 text-sm rounded-lg border transition-colors duration-150 focus:outline-none"
      :class="[
        isOpen
          ? 'border-primary/70 bg-surface ring-1 ring-primary/40'
          : 'border-border bg-surface hover:border-primary/50',
        hasValue ? 'text-text' : 'text-text-muted',
      ]"
      @click="togglePanel"
    >
      <svg class="w-3.5 h-3.5 flex-shrink-0 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <span class="whitespace-nowrap">
        <template v-if="localStart || localEnd">
          {{ localStart || '…' }} <span class="opacity-60 mx-0.5">→</span> {{ localEnd || '…' }}
        </template>
        <template v-else>{{ placeholder }}</template>
      </span>
      <!-- 清除按钮 -->
      <span
        v-if="hasValue"
        class="ml-1 flex items-center rounded-full hover:text-text transition-colors"
        @click.stop="clearDates"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </span>
    </button>

    <!-- 下拉面板（Teleport 到 body，固定定位） -->
    <Teleport to="body">
      <Transition name="dp-fade">
        <div
          v-if="isOpen"
          ref="panelRef"
          class="fixed z-[9999] bg-surface border border-border rounded-xl shadow-2xl"
          :style="panelStyle"
        >
          <!-- 快捷选项 -->
          <div class="flex items-center gap-1 px-3 pt-3 pb-2 border-b border-border">
            <button
              v-for="s in shortcuts"
              :key="s.label"
              class="px-2 py-0.5 text-xs rounded-md border border-border/60 text-text-muted hover:text-text hover:border-primary/50 transition-colors duration-150"
              @click="applyShortcut(s)"
            >{{ s.label }}</button>
          </div>
          <!-- 双栏日历 -->
          <div class="flex">
            <CalendarPanel
              :year="leftYear"
              :month="leftMonth"
              :start="localStart"
              :end="localEnd"
              :hover-date="hoverDate"
              @prev-month="prevLeftMonth"
              @next-month="nextLeftMonthIfAllowed"
              @select="handleSelect"
              @hover="hoverDate = $event"
            />
            <div class="w-px bg-border self-stretch mx-0" />
            <CalendarPanel
              :year="rightYear"
              :month="rightMonth"
              :start="localStart"
              :end="localEnd"
              :hover-date="hoverDate"
              @prev-month="prevRightMonthIfAllowed"
              @next-month="nextRightMonth"
              @select="handleSelect"
              @hover="hoverDate = $event"
            />
          </div>
          <!-- 底部确认 -->
          <div class="flex items-center justify-between px-3 py-2.5 border-t border-border">
            <span class="text-xs text-text-muted">
              <template v-if="localStart && !localEnd">请选择结束日期</template>
              <template v-else-if="localStart && localEnd">{{ localStart }} 至 {{ localEnd }}</template>
              <template v-else>请选择日期范围</template>
            </span>
            <div class="flex gap-2">
              <button class="btn btn-ghost btn-sm h-7 px-3 text-xs" @click="cancelPanel">取消</button>
              <button
                class="btn btn-primary btn-sm h-7 px-3 text-xs"
                :disabled="!localStart || !localEnd"
                @click="confirmPanel"
              >确定</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, defineComponent, h, onMounted, onBeforeUnmount } from 'vue'

const props = withDefaults(defineProps<{
  startDate?: string
  endDate?: string
  placeholder?: string
}>(), {
  placeholder: '选择日期范围',
})

const emit = defineEmits<{
  'update:startDate': [v: string | undefined]
  'update:endDate': [v: string | undefined]
  change: [start: string | undefined, end: string | undefined]
}>()

// ─── State ─────────────────────────────────────────────────────────
const isOpen = ref(false)
const rootRef = ref<HTMLElement | null>(null)
const panelRef = ref<HTMLElement | null>(null)
const panelStyle = ref<Record<string, string>>({})

const localStart = ref(props.startDate || '')
const localEnd = ref(props.endDate || '')
const hoverDate = ref('')
const selecting = ref<'start' | 'end'>('start')

// calendar nav — left always <= right-1 month
const today = new Date()
const leftYear = ref(today.getFullYear())
const leftMonth = ref(today.getMonth()) // 0-based
const rightYear = computed(() => {
  if (leftMonth.value === 11) return leftYear.value + 1
  return leftYear.value
})
const rightMonth = computed(() => (leftMonth.value + 1) % 12)

const hasValue = computed(() => !!(localStart.value || localEnd.value))

// ─── Sync props → local ────────────────────────────────────────────
watch(() => props.startDate, v => { localStart.value = v || '' })
watch(() => props.endDate, v => { localEnd.value = v || '' })

// ─── Panel positioning ─────────────────────────────────────────────
function updatePanelPosition() {
  if (!rootRef.value) return
  const rect = rootRef.value.getBoundingClientRect()
  const panelWidth = 560
  let left = rect.left
  if (left + panelWidth > window.innerWidth - 8) {
    left = window.innerWidth - panelWidth - 8
  }
  panelStyle.value = {
    top: `${rect.bottom + 6}px`,
    left: `${left}px`,
    width: `${panelWidth}px`,
  }
}

function togglePanel() {
  if (isOpen.value) {
    isOpen.value = false
    return
  }
  // init calendar to show current start month
  if (localStart.value) {
    const d = new Date(localStart.value)
    leftYear.value = d.getFullYear()
    leftMonth.value = d.getMonth()
  } else {
    leftYear.value = today.getFullYear()
    leftMonth.value = today.getMonth() === 0 ? 0 : today.getMonth() - 1
    if (leftMonth.value < 0) {
      leftMonth.value = 11
      leftYear.value -= 1
    }
  }
  selecting.value = 'start'
  hoverDate.value = ''
  isOpen.value = true
  nextTick(updatePanelPosition)
}

// ─── Click outside ─────────────────────────────────────────────────
function onMouseDown(e: MouseEvent) {
  const target = e.target as Node
  if (!rootRef.value?.contains(target) && !panelRef.value?.contains(target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onMouseDown))
onBeforeUnmount(() => document.removeEventListener('mousedown', onMouseDown))

// ─── Calendar navigation ───────────────────────────────────────────
function prevLeftMonth() {
  if (leftMonth.value === 0) { leftMonth.value = 11; leftYear.value -= 1 }
  else leftMonth.value -= 1
}
function nextLeftMonthIfAllowed() {
  // left must be < right (rightMonth = leftMonth+1)
  // so left can't advance beyond (rightYear,rightMonth-1)
  // which means: left can never be >= right, already ensured by rightMonth = left+1
  // just ensure left+1 < right (they're always left+1=right, so we can allow left to advance if we also advance right)
  if (leftMonth.value === 11) { leftMonth.value = 0; leftYear.value += 1 }
  else leftMonth.value += 1
}
function prevRightMonthIfAllowed() {
  // right can't go <= left; right = left+1 always, controlled via leftMonth
  prevLeftMonth()
}
function nextRightMonth() {
  nextLeftMonthIfAllowed()
}

// ─── Date selection ────────────────────────────────────────────────
function handleSelect(dateStr: string) {
  if (selecting.value === 'start') {
    localStart.value = dateStr
    localEnd.value = ''
    selecting.value = 'end'
  } else {
    if (dateStr < localStart.value) {
      // swap
      localEnd.value = localStart.value
      localStart.value = dateStr
    } else {
      localEnd.value = dateStr
    }
    // don't auto-confirm, wait for user to click 确定
  }
}

// ─── Shortcuts ─────────────────────────────────────────────────────
interface Shortcut { label: string; getDates: () => [string, string] }

function fmt(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const shortcuts: Shortcut[] = [
  {
    label: '本周',
    getDates: () => {
      const d = new Date(); const day = d.getDay() || 7
      const mon = new Date(d); mon.setDate(d.getDate() - day + 1)
      return [fmt(mon), fmt(d)]
    },
  },
  {
    label: '本月',
    getDates: () => {
      const d = new Date()
      const start = new Date(d.getFullYear(), d.getMonth(), 1)
      return [fmt(start), fmt(d)]
    },
  },
  {
    label: '上月',
    getDates: () => {
      const d = new Date()
      const start = new Date(d.getFullYear(), d.getMonth() - 1, 1)
      const end = new Date(d.getFullYear(), d.getMonth(), 0)
      return [fmt(start), fmt(end)]
    },
  },
  {
    label: '近7天',
    getDates: () => {
      const end = new Date(); const start = new Date()
      start.setDate(end.getDate() - 6)
      return [fmt(start), fmt(end)]
    },
  },
  {
    label: '近30天',
    getDates: () => {
      const end = new Date(); const start = new Date()
      start.setDate(end.getDate() - 29)
      return [fmt(start), fmt(end)]
    },
  },
  {
    label: '今年',
    getDates: () => {
      const d = new Date()
      return [`${d.getFullYear()}-01-01`, fmt(d)]
    },
  },
]

function applyShortcut(s: Shortcut) {
  const [start, end] = s.getDates()
  localStart.value = start
  localEnd.value = end
  selecting.value = 'start'
}

function cancelPanel() {
  localStart.value = props.startDate || ''
  localEnd.value = props.endDate || ''
  isOpen.value = false
}

function confirmPanel() {
  isOpen.value = false
  emit('update:startDate', localStart.value || undefined)
  emit('update:endDate', localEnd.value || undefined)
  emit('change', localStart.value || undefined, localEnd.value || undefined)
}

function clearDates() {
  localStart.value = ''
  localEnd.value = ''
  emit('update:startDate', undefined)
  emit('update:endDate', undefined)
  emit('change', undefined, undefined)
}

// ─── CalendarPanel (inline component) ─────────────────────────────
const CalendarPanel = defineComponent({
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
    start: { type: String, default: '' },
    end: { type: String, default: '' },
    hoverDate: { type: String, default: '' },
  },
  emits: ['prevMonth', 'nextMonth', 'select', 'hover'],
  setup(props, { emit }) {
    const WEEK = ['日', '一', '二', '三', '四', '五', '六']

    function getDays() {
      const firstDay = new Date(props.year, props.month, 1).getDay()
      const totalDays = new Date(props.year, props.month + 1, 0).getDate()
      const cells: Array<{ date: string; day: number; thisMonth: boolean }> = []
      // prev month padding
      const prevDays = new Date(props.year, props.month, 0).getDate()
      for (let i = firstDay - 1; i >= 0; i--) {
        const d = prevDays - i
        const m = props.month === 0 ? 12 : props.month
        const y = props.month === 0 ? props.year - 1 : props.year
        cells.push({ date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, day: d, thisMonth: false })
      }
      for (let d = 1; d <= totalDays; d++) {
        cells.push({
          date: `${props.year}-${String(props.month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
          day: d,
          thisMonth: true,
        })
      }
      // next month padding
      const remaining = 42 - cells.length
      for (let d = 1; d <= remaining; d++) {
        const m = props.month === 11 ? 1 : props.month + 2
        const y = props.month === 11 ? props.year + 1 : props.year
        cells.push({ date: `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`, day: d, thisMonth: false })
      }
      return cells
    }

    const todayStr = (() => {
      const d = new Date()
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    })()

    return () => {
      const cells = getDays()
      const effectiveEnd = props.hoverDate && props.start && !props.end
        ? (props.hoverDate > props.start ? props.hoverDate : props.start)
        : props.end
      const effectiveStart = props.hoverDate && props.start && !props.end
        ? (props.hoverDate < props.start ? props.hoverDate : props.start)
        : props.start

      return h('div', { class: 'w-[268px] px-3 py-3 select-none' }, [
        // header
        h('div', { class: 'flex items-center justify-between mb-3' }, [
          h('button', {
            class: 'p-1 rounded hover:bg-border transition-colors text-text-muted hover:text-text',
            onClick: () => emit('prevMonth'),
          }, h('svg', { class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
            h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 19l-7-7 7-7' })
          )),
          h('span', { class: 'text-sm font-medium text-text' },
            `${props.year}年 ${props.month + 1}月`
          ),
          h('button', {
            class: 'p-1 rounded hover:bg-border transition-colors text-text-muted hover:text-text',
            onClick: () => emit('nextMonth'),
          }, h('svg', { class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
            h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5l7 7-7 7' })
          )),
        ]),
        // weekdays
        h('div', { class: 'grid grid-cols-7 mb-1' },
          WEEK.map(w => h('div', { class: 'text-center text-xs text-text-muted py-1' }, w))
        ),
        // cells
        h('div', { class: 'grid grid-cols-7 gap-y-0.5' },
          cells.map(cell => {
            const isStart = cell.date === props.start
            const isEnd = cell.date === props.end || cell.date === effectiveEnd
            const inRange = effectiveStart && effectiveEnd && cell.date > effectiveStart && cell.date < effectiveEnd
            const isToday = cell.date === todayStr

            let cls = 'relative h-7 flex items-center justify-center text-xs cursor-pointer transition-colors duration-100 '
            if (!cell.thisMonth) cls += 'text-text-muted/30 '
            else if (isToday && !isStart && !isEnd) cls += 'font-semibold text-primary '
            else if (cell.thisMonth) cls += 'text-text '

            let bgCls = ''
            if (isStart || isEnd) bgCls = 'bg-primary text-white! rounded-full z-10'
            else if (inRange) bgCls = 'bg-primary/20 rounded-none'

            return h('div', {
              class: 'relative',
              onMouseenter: () => emit('hover', cell.date),
              onMouseleave: () => emit('hover', ''),
            }, [
              // range background bar
              (isStart && effectiveEnd && effectiveEnd > effectiveStart)
                ? h('div', { class: 'absolute inset-y-0 right-0 left-1/2 bg-primary/20' })
                : null,
              (isEnd && effectiveStart && effectiveEnd > effectiveStart)
                ? h('div', { class: 'absolute inset-y-0 left-0 right-1/2 bg-primary/20' })
                : null,
              h('div', {
                class: `${cls} ${bgCls} relative z-10 w-7 h-7 mx-auto`,
                onClick: () => cell.thisMonth && emit('select', cell.date),
              }, String(cell.day))
            ])
          })
        ),
      ])
    }
  }
})
</script>

<style scoped>
.dp-fade-enter-active,
.dp-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.dp-fade-enter-from,
.dp-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
