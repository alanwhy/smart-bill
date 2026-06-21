<template>
  <div class="card p-4 flex flex-col h-full min-h-[320px]">
    <h3 class="text-sm font-semibold text-text mb-3">消费趋势</h3>
    <div class="flex-1 relative min-h-0">
      <div v-if="isEmpty" class="absolute inset-0 flex flex-col items-center justify-center text-text-muted">
        <svg class="w-10 h-10 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span class="text-xs">暂无数据</span>
      </div>
      <div ref="chartRef" class="w-full h-full" style="min-height: 260px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { DayTrend } from '@/stores/stats'

echarts.use([LineChart, TooltipComponent, GridComponent, CanvasRenderer])

const props = defineProps<{
  data: DayTrend[]
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const isEmpty = computed(() => props.data.length === 0)

function fmtDate(d: string) {
  // YYYY-MM-DD → MM/DD
  return d.substring(5).replace('-', '/')
}

function buildOption() {
  const dates = props.data.map((d) => fmtDate(d.date))
  const expenses = props.data.map((d) => +d.expense.toFixed(2))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1E293B',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      axisPointer: { type: 'line', lineStyle: { color: '#475569', type: 'dashed' } },
      formatter: (params: any[]) => {
        const p = params[0]
        return `<div style="margin-bottom:4px;color:#94A3B8">${p.axisValue}</div>${p.marker}支出: <b>¥${p.value.toFixed(2)}</b>`
      },
    },
    grid: { left: 8, right: 12, bottom: 8, top: 16, containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#334155' } },
      axisTick: { show: false },
      axisLabel: { color: '#64748B', fontSize: 10, interval: 'auto' },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748B',
        fontSize: 10,
        formatter: (v: number) => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v),
      },
      splitLine: { lineStyle: { color: '#1E293B', type: 'dashed' } },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        name: '支出',
        type: 'line',
        data: expenses,
        smooth: 0.4,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: '#F59E0B', width: 2.5 },
        itemStyle: { color: '#F59E0B', borderColor: '#0F172A', borderWidth: 1.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245,158,11,0.30)' },
            { offset: 1, color: 'rgba(245,158,11,0.02)' },
          ]),
        },
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

watch(() => props.data, () => {
  if (isEmpty.value) chart?.clear()
  else initChart()
})
</script>
