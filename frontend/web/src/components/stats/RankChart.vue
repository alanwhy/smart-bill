<template>
  <div class="card p-4 flex flex-col h-full min-h-[320px]">
    <h3 class="text-sm font-semibold text-text mb-3">消费排行</h3>
    <div class="flex-1 relative min-h-0">
      <div v-if="isEmpty" class="absolute inset-0 flex flex-col items-center justify-center text-text-muted">
        <svg class="w-10 h-10 mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 10h16M4 14h8m-8 4h4" />
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
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { MerchantRank } from '@/stores/stats'

echarts.use([BarChart, TooltipComponent, GridComponent, CanvasRenderer])

const props = defineProps<{
  data: MerchantRank[]
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const isEmpty = computed(() => props.data.length === 0)

function buildOption() {
  // 倒序，最大值在上方
  const sorted = [...props.data].reverse()
  const names = sorted.map((d) => d.name)
  const values = sorted.map((d) => +d.value.toFixed(2))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1E293B',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      axisPointer: { type: 'shadow' },
      formatter: (params: any[]) => {
        const p = params[0]
        return `${p.name}<br/>${p.marker}<b>¥${p.value.toFixed(2)}</b>`
      },
    },
    grid: { left: 8, right: 64, bottom: 8, top: 8, containLabel: true },
    xAxis: {
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
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#CBD5E1',
        fontSize: 11,
        formatter: (name: string) => name.length > 8 ? name.substring(0, 8) + '…' : name,
      },
    },
    series: [
      {
        type: 'bar',
        data: values,
        barMaxWidth: 18,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: (params: any) => {
            const ratio = params.dataIndex / (values.length - 1 || 1)
            return new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#8B5CF6' },
              { offset: 1, color: `rgba(59,130,246,${0.6 + ratio * 0.4})` },
            ])
          },
        },
        label: {
          show: true,
          position: 'right',
          color: '#94A3B8',
          fontSize: 10,
          formatter: (p: any) => `¥${p.value >= 1000 ? (p.value / 1000).toFixed(1) + 'k' : p.value.toFixed(0)}`,
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#A78BFA' },
              { offset: 1, color: '#60A5FA' },
            ]),
          },
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
