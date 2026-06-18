<template>
  <!-- 模态框背景 -->
  <div class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-surface rounded-2xl shadow-xl w-full max-w-lg">
      <!-- 头部 -->
      <div class="border-b border-border px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-text">{{ mode === 'create' ? '手动录入账单' : '编辑账单' }}</h2>
        <button
          @click="emit('close')"
          class="p-2 hover:bg-border rounded-lg transition-colors duration-200"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 内容 -->
      <div class="p-6 space-y-4">
        <!-- 收支类型 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">类型</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              type="button"
              @click="formData.type = 'expense'"
              :class="[
                'py-2 rounded-lg border-2 text-sm font-medium transition-all duration-200',
                formData.type === 'expense'
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border bg-surface text-text-secondary hover:border-primary/50',
              ]"
            >
              支出
            </button>
            <button
              type="button"
              @click="formData.type = 'income'"
              :class="[
                'py-2 rounded-lg border-2 text-sm font-medium transition-all duration-200',
                formData.type === 'income'
                  ? 'border-success bg-success/10 text-success'
                  : 'border-border bg-surface text-text-secondary hover:border-success/50',
              ]"
            >
              收入
            </button>
          </div>
        </div>

        <!-- 金额 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">金额</label>
          <input
            v-model.number="formData.amount"
            type="number"
            step="0.01"
            min="0"
            class="input"
            placeholder="0.00"
          />
        </div>

        <!-- 商户名称 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">商户名称</label>
          <input
            v-model="formData.merchant_name"
            type="text"
            class="input"
            placeholder="输入商户名称"
          />
        </div>

        <!-- 分类 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">分类</label>
          <p v-if="categoriesStore.isLoading && categories.length === 0" class="text-xs text-text-muted">加载中...</p>
          <div v-else class="grid grid-cols-3 gap-2">
            <button
              v-for="cat in categories"
              :key="cat.id"
              @click="formData.category_id = cat.id"
              :class="[
                'p-3 rounded-lg border-2 transition-all duration-200',
                formData.category_id === cat.id
                  ? 'border-primary bg-primary/10'
                  : 'border-border bg-surface hover:border-primary/50',
              ]"
            >
              <div class="text-lg mb-1">{{ cat.icon }}</div>
              <div class="text-xs text-text-secondary">{{ cat.name }}</div>
            </button>
          </div>
        </div>

        <!-- 交易日期 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">交易日期</label>
          <input
            v-model="formData.transaction_date"
            type="datetime-local"
            class="input"
          />
        </div>

        <!-- 备注 -->
        <div>
          <label class="block text-sm font-medium text-text mb-2">备注</label>
          <textarea
            v-model="formData.description"
            :maxlength="100"
            rows="2"
            placeholder="可选，最多 100 字"
            class="input resize-none"
          />
          <p class="text-xs text-text-muted mt-1 text-right">{{ (formData.description || '').length }}/100</p>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="p-3 bg-error/10 border border-error/30 rounded-lg">
          <p class="text-sm text-error">{{ errorMessage }}</p>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="border-t border-border px-6 py-4 flex gap-2 justify-end">
        <button
          @click="emit('close')"
          :disabled="isSubmitting"
          class="btn btn-secondary"
        >
          取消
        </button>
        <button
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="btn btn-primary"
        >
          {{ isSubmitting ? '保存中...' : (mode === 'create' ? '保存' : '保存修改') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useBillsStore } from '@/stores/bills'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import type { BillRecord } from '@/types/bill'
import { format, parseISO } from 'date-fns'

const props = withDefaults(
  defineProps<{
    bill?: BillRecord
    mode?: 'create' | 'edit'
  }>(),
  { mode: 'edit' },
)

const emit = defineEmits<{
  close: []
  update: []
}>()

const billsStore = useBillsStore()
const categoriesStore = useCategoriesStore()
const authStore = useAuthStore()

const categories = computed(() => categoriesStore.sortedCategories)

const isSubmitting = ref(false)
const errorMessage = ref('')

function todayDatetimeLocal(): string {
  return format(new Date(), "yyyy-MM-dd'T'HH:mm")
}

function convertToDatetimeLocal(dateStr: string): string {
  try {
    const date = parseISO(dateStr)
    return format(date, "yyyy-MM-dd'T'HH:mm")
  } catch {
    return dateStr
  }
}

const formData = reactive({
  type: (props.bill && props.bill.value > 0 ? 'income' : 'expense') as 'expense' | 'income',
  amount: props.bill ? Math.abs(props.bill.value) : 0,
  merchant_name: props.bill?.merchant_name ?? '',
  category_id: props.bill?.category_id ?? 0,
  transaction_date: props.bill
    ? convertToDatetimeLocal(props.bill.transaction_date)
    : todayDatetimeLocal(),
  description: props.bill?.description ?? '',
})

onMounted(() => {
  categoriesStore.getOrFetch()
})

const handleSubmit = async () => {
  errorMessage.value = ''

  if (!formData.merchant_name.trim()) {
    errorMessage.value = '请输入商户名称'
    return
  }

  if (!formData.amount || formData.amount <= 0) {
    errorMessage.value = '金额必须大于 0'
    return
  }

  if (!formData.category_id) {
    errorMessage.value = '请选择分类'
    return
  }

  // 根据收支类型决定提交时的正负号
  const signedValue =
    formData.type === 'expense' ? -Math.abs(formData.amount) : Math.abs(formData.amount)

  isSubmitting.value = true

  try {
    if (props.mode === 'create') {
      await billsStore.createBill({
        user_id: authStore.userId!,
        value: signedValue,
        merchant_name: formData.merchant_name,
        category_id: formData.category_id,
        transaction_date: new Date(formData.transaction_date).toISOString(),
        description: formData.description || undefined,
      })
    } else {
      await billsStore.updateBill(props.bill!.id, {
        value: signedValue,
        merchant_name: formData.merchant_name,
        category_id: formData.category_id,
        transaction_date: new Date(formData.transaction_date).toISOString(),
        description: formData.description || undefined,
      })
    }

    emit('update')
  } catch (e) {
    errorMessage.value = (e as Error).message
  } finally {
    isSubmitting.value = false
  }
}
</script>
