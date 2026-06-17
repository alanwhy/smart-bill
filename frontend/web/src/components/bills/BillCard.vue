<template>
  <div class="card-hover group p-4">
    <div class="flex items-start justify-between">
      <!-- 左侧内容 -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-3 mb-2">
          <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-surface flex items-center justify-center">
            <span class="text-lg">{{ bill.category?.icon || '📦' }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-semibold text-text truncate">{{ bill.merchant_name }}</h3>
            <p class="text-xs text-text-muted">{{ bill.category?.name || '其他' }}</p>
          </div>
        </div>
        <p class="text-xs text-text-muted">{{ formatDate(bill.transaction_date) }}</p>
        <p v-if="bill.description" class="text-xs text-text-muted mt-0.5 truncate">{{ bill.description }}</p>
      </div>

      <!-- 右侧操作 -->
      <div class="flex items-center gap-2 ml-4">
        <div class="text-right mr-2">
          <p class="text-base font-bold text-primary">¥{{ bill.value.toFixed(2) }}</p>
        </div>

        <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex gap-1">
          <button
            @click.stop="$emit('edit', bill)"
            class="p-2 hover:bg-surface rounded-lg transition-colors duration-200"
            title="编辑"
          >
            <svg class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click.stop="$emit('delete', bill)"
            class="p-2 hover:bg-error/10 rounded-lg transition-colors duration-200"
            title="删除"
          >
            <svg class="w-4 h-4 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BillRecord } from '@/types/bill'
import { format, parseISO } from 'date-fns'
import { zhCN } from 'date-fns/locale'

defineProps<{
  bill: BillRecord
}>()

defineEmits<{
  edit: [bill: BillRecord]
  delete: [bill: BillRecord]
}>()

const formatDate = (dateStr: string): string => {
  try {
    return format(parseISO(dateStr), 'MM月dd日 HH:mm', { locale: zhCN })
  } catch {
    return dateStr
  }
}
</script>
