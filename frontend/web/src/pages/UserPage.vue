<template>
  <div class="min-h-full pb-20 lg:pb-0">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-text mb-2">用户中心</h1>
        <p class="text-text-muted">管理您的账户信息</p>
      </div>

      <!-- 用户信息 -->
      <div class="card p-6 mb-6">
        <h2 class="text-lg font-semibold text-text mb-4">账户信息</h2>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-text-muted">当前用户</p>
              <p class="font-medium text-text">{{ authStore.username }}</p>
            </div>
          </div>
          <button @click="handleLogout" class="btn btn-secondary gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>退出登录</span>
          </button>
        </div>
      </div>

      <!-- 修改密码 -->
      <div class="card p-6 mb-6">
        <h2 class="text-lg font-semibold text-text mb-4">修改密码</h2>
        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="block text-sm text-text-secondary mb-1.5">旧密码</label>
            <input
              v-model="pwForm.oldPassword"
              type="password"
              class="input w-full"
              placeholder="请输入旧密码"
              :disabled="isSavingPw"
            />
          </div>
          <div>
            <label class="block text-sm text-text-secondary mb-1.5">新密码</label>
            <input
              v-model="pwForm.newPassword"
              type="password"
              class="input w-full"
              placeholder="至少 6 位"
              :disabled="isSavingPw"
            />
          </div>
          <div>
            <label class="block text-sm text-text-secondary mb-1.5">确认新密码</label>
            <input
              v-model="pwForm.confirmPassword"
              type="password"
              class="input w-full"
              placeholder="再次输入新密码"
              :disabled="isSavingPw"
            />
          </div>
          <p v-if="pwError" class="text-sm text-error">{{ pwError }}</p>
          <p v-if="pwSuccess" class="text-sm text-success">{{ pwSuccess }}</p>
          <button
            type="submit"
            :disabled="isSavingPw"
            class="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSavingPw ? '保存中...' : '保存密码' }}
          </button>
        </form>
        <p class="text-xs text-text-muted mt-4">修改密码成功后将自动退出登录，请使用新密码重新登录。</p>
      </div>

      <!-- 数据管理（仅 PC 端） -->
      <div v-if="isDesktop" class="card p-8">
        <!-- 卡片标题 -->
        <div class="flex items-center gap-3 mb-8">
          <div class="w-9 h-9 rounded-xl bg-primary/15 flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-text leading-none">数据管理</h2>
            <p class="text-xs text-text-muted mt-1">导出或导入账单数据</p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-8">
          <!-- 导出区域 -->
          <div class="space-y-5">
            <!-- 区块标题 -->
            <div class="flex items-center gap-2.5 pb-4 border-b border-border/60">
              <div class="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </div>
              <h3 class="text-sm font-semibold text-text tracking-wide">导出账单</h3>
            </div>

            <div>
              <label class="block text-xs font-medium text-text-secondary mb-2 uppercase tracking-wider">开始日期</label>
              <input v-model="exportStart" type="date" class="input w-full text-sm" :max="exportEnd || undefined" />
            </div>
            <div>
              <label class="block text-xs font-medium text-text-secondary mb-2 uppercase tracking-wider">结束日期</label>
              <input v-model="exportEnd" type="date" class="input w-full text-sm" :min="exportStart || undefined" />
            </div>
            <p v-if="exportError" class="text-xs text-error bg-error/10 border border-error/20 rounded-lg px-3 py-2">{{ exportError }}</p>
            <button
              @click="handleExport"
              :disabled="isExporting"
              class="btn btn-primary w-full gap-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              <svg v-if="!isExporting" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <svg v-else class="w-4 h-4 flex-shrink-0 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
              </svg>
              {{ isExporting ? '导出中...' : '导出 Excel' }}
            </button>
          </div>

          <!-- 导入区域 -->
          <div class="space-y-5 border-l border-border/60 pl-8">
            <!-- 区块标题 -->
            <div class="flex items-center gap-2.5 pb-4 border-b border-border/60">
              <div class="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg class="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l4-4m0 0l4 4m-4-4v12" />
                </svg>
              </div>
              <h3 class="text-sm font-semibold text-text tracking-wide">导入账单</h3>
            </div>

            <!-- 下载模板 -->
            <button
              @click="handleDownloadTemplate"
              class="btn btn-secondary w-full gap-2 text-sm font-medium cursor-pointer"
            >
              <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              下载导入模板
            </button>

            <!-- 上传区域 -->
            <div
              class="border-2 border-dashed border-border rounded-xl p-6 text-center cursor-pointer transition-all duration-200 hover:border-primary/60 hover:bg-primary/5 relative"
              :class="{ 'border-primary bg-primary/8': isDragOver }"
              @click="triggerFileInput"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleFileDrop"
            >
              <input
                ref="fileInputRef"
                type="file"
                accept=".xlsx,.xls"
                class="hidden"
                @change="handleFileChange"
              />
              <svg class="w-10 h-10 mx-auto text-text-muted mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p v-if="!importFile" class="text-sm text-text-muted leading-relaxed">
                拖放 Excel 文件至此<br/>
                <span class="text-primary font-medium">或点击选择文件</span>
              </p>
              <p v-else class="text-sm font-medium text-text truncate px-2">{{ importFile.name }}</p>
            </div>

            <!-- 验证结果 -->
            <div v-if="importParsing" class="flex items-center gap-2.5 text-sm text-text-muted bg-border/30 rounded-lg px-4 py-3">
              <svg class="w-4 h-4 animate-spin flex-shrink-0" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
              </svg>
              正在解析文件...
            </div>
            <div v-else-if="importErrors.length > 0" class="rounded-xl bg-error/10 border border-error/20 p-4">
              <p class="text-sm font-semibold text-error mb-2.5">发现 {{ importErrors.length }} 个错误，请修正后重新上传</p>
              <ul class="space-y-1.5 max-h-28 overflow-y-auto">
                <li
                  v-for="(err, i) in importErrors"
                  :key="i"
                  class="text-xs text-error/80 leading-relaxed"
                >第 {{ err.row }} 行 · {{ err.field }}：{{ err.message }}</li>
              </ul>
            </div>
            <div v-else-if="importRows.length > 0" class="rounded-xl bg-success/10 border border-success/20 px-4 py-3 flex items-center gap-2.5">
              <svg class="w-4 h-4 text-success flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <p class="text-sm text-success font-medium">验证通过，共 {{ importRows.length }} 条记录</p>
            </div>

            <!-- 确认导入按钮 -->
            <button
              v-if="importRows.length > 0 && importErrors.length === 0"
              @click="handleImport"
              :disabled="isImporting"
              class="btn btn-primary w-full gap-2 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="!isImporting" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-4 h-4 flex-shrink-0 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/>
              </svg>
              {{ isImporting ? '导入中...' : `确认导入 ${importRows.length} 条` }}
            </button>
            <p v-if="importSuccess" class="text-xs text-success bg-success/10 border border-success/20 rounded-lg px-3 py-2">{{ importSuccess }}</p>
            <p v-if="importError" class="text-xs text-error bg-error/10 border border-error/20 rounded-lg px-3 py-2">{{ importError }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCategoriesStore } from '@/stores/categories'
import { useDevice } from '@/utils/useDevice'
import { authApi } from '@/api/auth'
import { billApi } from '@/api/bills'
import { downloadTemplate, exportBillsToExcel, parseImportFile } from '@/utils/excel'
import type { ImportBillRow } from '@/utils/excel'

const router = useRouter()
const authStore = useAuthStore()
const categoriesStore = useCategoriesStore()
const { isDesktop } = useDevice()

// ---------------------------------------------------------------------------
// 修改密码
// ---------------------------------------------------------------------------
const pwForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const isSavingPw = ref(false)
const pwError = ref('')
const pwSuccess = ref('')

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'Login' })
}

const handleChangePassword = async () => {
  pwError.value = ''
  pwSuccess.value = ''

  if (!pwForm.value.oldPassword || !pwForm.value.newPassword || !pwForm.value.confirmPassword) {
    pwError.value = '请填写所有字段'
    return
  }
  if (pwForm.value.newPassword.length < 6) {
    pwError.value = '新密码至少 6 位'
    return
  }
  if (pwForm.value.newPassword !== pwForm.value.confirmPassword) {
    pwError.value = '两次输入的新密码不一致'
    return
  }

  isSavingPw.value = true
  try {
    await authApi.changePassword(pwForm.value.oldPassword, pwForm.value.newPassword)
    pwSuccess.value = '密码修改成功，即将退出登录...'
    pwForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    setTimeout(() => {
      authStore.logout()
      router.push({ name: 'Login' })
    }, 1000)
  } catch (e) {
    pwError.value = (e as Error).message || '修改失败，请重试'
  } finally {
    isSavingPw.value = false
  }
}

// ---------------------------------------------------------------------------
// 导出
// ---------------------------------------------------------------------------
const today = new Date().toISOString().slice(0, 10)
const firstOfMonth = today.slice(0, 8) + '01'
const exportStart = ref(firstOfMonth)
const exportEnd = ref(today)
const isExporting = ref(false)
const exportError = ref('')

const handleExport = async () => {
  exportError.value = ''
  if (!exportStart.value || !exportEnd.value) {
    exportError.value = '请选择导出时间段'
    return
  }
  if (exportStart.value > exportEnd.value) {
    exportError.value = '开始日期不能晚于结束日期'
    return
  }
  isExporting.value = true
  try {
    const bills = await billApi.listBills(authStore.userId!, {
      startDate: exportStart.value,
      endDate: exportEnd.value,
    })
    if (!bills.length) {
      exportError.value = '所选时间段内没有账单记录'
      return
    }
    const filename = `账单_${exportStart.value}_${exportEnd.value}.xlsx`
    exportBillsToExcel(bills, filename)
  } catch (e) {
    exportError.value = (e as Error).message || '导出失败，请重试'
  } finally {
    isExporting.value = false
  }
}

// ---------------------------------------------------------------------------
// 导入
// ---------------------------------------------------------------------------
const fileInputRef = ref<HTMLInputElement | null>(null)
const importFile = ref<File | null>(null)
const isDragOver = ref(false)
const importParsing = ref(false)
const importRows = ref<ImportBillRow[]>([])
const importErrors = ref<Array<{ row: number; field: string; message: string }>>([])
const isImporting = ref(false)
const importSuccess = ref('')
const importError = ref('')

const resetImportState = () => {
  importRows.value = []
  importErrors.value = []
  importSuccess.value = ''
  importError.value = ''
}

const parseFile = async (file: File) => {
  importFile.value = file
  resetImportState()
  importParsing.value = true
  try {
    await categoriesStore.getOrFetch()
    const result = await parseImportFile(file, categoriesStore.sortedCategories)
    importRows.value = result.rows
    importErrors.value = result.errors
  } catch (e) {
    importErrors.value = [{ row: 0, field: '文件', message: (e as Error).message || '解析失败' }]
  } finally {
    importParsing.value = false
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) parseFile(file)
}

const handleFileDrop = (e: DragEvent) => {
  isDragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) parseFile(file)
}

const handleDownloadTemplate = async () => {
  await categoriesStore.getOrFetch()
  const names = categoriesStore.sortedCategories.map((c) => c.name)
  downloadTemplate(names)
}

const handleImport = async () => {
  importSuccess.value = ''
  importError.value = ''
  isImporting.value = true
  try {
    const items = importRows.value
      .filter((r) => r.category_id !== undefined)
      .map((r) => ({
        value: r.value,
        merchant_name: r.merchant_name,
        transaction_date: r.transaction_date,
        category_id: r.category_id!,
        description: r.description || undefined,
      }))

    const result = await billApi.batchCreateBills({
      user_id: authStore.userId!,
      items,
    })
    importSuccess.value = `成功导入 ${result.created_count} 条账单`
    importFile.value = null
    importRows.value = []
    if (fileInputRef.value) fileInputRef.value.value = ''
  } catch (e) {
    importError.value = (e as Error).message || '导入失败，请重试'
  } finally {
    isImporting.value = false
  }
}

onMounted(() => {
  if (isDesktop.value) {
    categoriesStore.getOrFetch()
  }
})
</script>

