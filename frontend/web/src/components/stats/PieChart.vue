<template>
  <div class="card p-4 flex flex-col h-full min-h-[320px]">
    <!-- 标题 + Tab -->
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-text">收支分布</h3>
      <div class="flex gap-1 bg-background rounded-lg p-0.5">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="px-3 py-1 text-xs rounded-md transition-colors duration-150"
          :class="activeTab === tab.key ? 'bg-surface text-text font-medium' : 'text-text-muted hover:text-text'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>
    <!-- 图表 -->
    <div class="flex-1 relative min-h-0">
      <div v-if="isEmpty" class="absolute inset-0 flex flex-col items-center justify-center text-text-muted">
        <svg class="w-10 h-10 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
        </svg>
        <span class="text-xs">暂无数据</span>
      </div>
      <div ref="chartRef" class="w-full h-full" style="min-height: 240px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GraphicComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { CategoryStat } from '@/stores/stats'

echarts.use([PieChart, TooltipComponent, LegendComponent, GraphicComponent, CanvasRenderer])

const COLORS = ['#F59E0B', '#8B5CF6', '#10B981', '#3B82F6', '#EF4444', '#EC4899', '#14B8A6', '#F97316', '#A78BFA', '#34D399']

const props = defineProps<{
  data: CategoryStat[]
  totalExpense: number
  totalIncome: number
}>()

const tabs = [
  { key: 'expense' as const, label: '支出' },
  { key: 'income' as const, label: '收入' },
]
const activeTab = ref<'expense' | 'income'>('expense')

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const isEmpty = computed(() => {
  if (activeTab.value === 'expense') return props.totalExpense === 0
  return props.totalIncome === 0
})

const netBalance = computed(() => props.totalIncome - props.totalExpense)

function buildOption() {
  const isExpense = activeTab.value === 'expense'
  const items = props.data.filter((d) => (isExpense ? d.expense > 0 : d.income > 0))
  const total = isExpense ? props.totalExpense : props.totalIncome

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1E293B',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      formatter: (p: any) => `${p.marker}${p.name}<br/>¥${p.value.toFixed(2)} <span style="color:#94A3B8">(${p.percent}%)</span>`,
    },
    legend: {
      orient: 'horizontal',
      left: 'center',
      bottom: 4,
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: '#CBD5E1', fontSize: 11 },
      formatter: (name: string) => {
        const item = items.find((d) => d.name === name)
        if (!item) return name
        const val = isExpense ? item.expense : item.income
        return `${name}  ¥${val.toFixed(0)}`
      },
    },
    graphic: [
      {
        type: 'text',
        left: 'center',
        top: '36%',
        style: {
          text: `¥${total > 0 ? (total >= 10000 ? (total / 10000).toFixed(1) + 'w' : total.toFixed(0)) : '0'}`,
          fill: '#F59E0B',
          fontSize: 18,
          fontWeight: 'bold',
        },
      },
      {
        type: 'text',
        left: 'center',
        top: '48%',
        style: {
          text: isExpense ? '总支出' : '总收入',
          fill: '#94A3B8',
          fontSize: 11,
        },
      },
    ],
    series: [
      {
        type: 'pie',
        radius: ['42%', '65%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: true,
        label: { show: false },
        itemStyle: {
          borderColor: '#0F172A',
          borderWidth: 2,
          borderRadius: 4,
        },
        emphasis: {
          itemStyle: { shadowBlur: 12, shadowColor: 'rgba(245,158,11,0.4)' },
          scale: true,
          scaleSize: 6,
        },
        data: items.map((d, i) => ({
          name: d.name,
          value: isExpense ? d.expense : d.income,
          itemStyle: { color: d.color || COLORS[i % COLORS.length] },
        })),
      },
    ],
  }
}

function initChart() {
  if (!chartRef.value || isEmpty.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  }
  chart.setOption(buildOption(), true)
}

const resizeObserver = new ResizeObserver(() => chart?.resize())

onMounted(() => {
  if (chartRef.value) resizeObserver.observe(chartRef.value)
  initChart()
})

onBeforeUnmount(() => {
  resizeObserver.disconnect()
  chart?.dispose()
})

watch([() => props.data, () => props.totalExpense, () => props.totalIncome, activeTab], () => {
  if (isEmpty.value) {
    chart?.clear()
  } else {
    initChart()
  }
})
</script>
