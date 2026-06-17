<template>
  <!-- 模态框背景 -->
  <div class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-surface rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
      <!-- 头部 -->
      <div class="sticky top-0 bg-surface border-b border-border px-6 py-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-text">上传账单</h2>
        <button
          @click="$emit('close')"
          class="p-2 hover:bg-border rounded-lg transition-colors duration-200"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 内容 -->
      <div class="p-6 space-y-6">
        <!-- 上传区域 -->
        <div
          @click="triggerFileInput"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          :class="[
            'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors duration-200',
            isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50',
          ]"
        >
          <svg class="w-12 h-12 mx-auto mb-3 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="text-sm font-medium text-text mb-1">点击或拖放上传账单图片</p>
          <p class="text-xs text-text-muted">支持 JPG、PNG，单个文件不超过 5MB</p>

          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/*"
            class="hidden"
            @change="handleFileSelect"
          />
        </div>

        <!-- 已选文件列表 -->
        <div v-if="selectedFiles.length > 0" class="space-y-2">
          <p class="text-sm font-medium text-text">已选择 {{ selectedFiles.length }} 个文件</p>
          <div class="space-y-2">
            <div
              v-for="(file, index) in selectedFiles"
              :key="index"
              class="flex items-center justify-between p-3 bg-surface/50 border border-border rounded-lg"
            >
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <svg class="w-4 h-4 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H7a1 1 0 01-1-1v-6z" clip-rule="evenodd" />
                </svg>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-text truncate">{{ file.name }}</p>
                  <p class="text-xs text-text-muted">{{ formatFileSize(file.size) }}</p>
                </div>
              </div>
              <button
                @click.prevent="removeFile(index)"
                class="p-1 hover:bg-error/10 rounded transition-colors duration-200 flex-shrink-0"
              >
                <svg class="w-4 h-4 text-error" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 上传进度 -->
        <div v-if="isUploading">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-text">上传中...</p>
            <p class="text-sm text-text-muted">{{ uploadProgress }}%</p>
          </div>
          <div class="w-full h-2 bg-surface rounded-full overflow-hidden">
            <div
              class="h-full bg-primary transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            />
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="errorMessage" class="p-3 bg-error/10 border border-error/30 rounded-lg">
          <p class="text-sm text-error">{{ errorMessage }}</p>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="border-t border-border px-6 py-4 flex gap-2 justify-end">
        <button
          @click="$emit('close')"
          :disabled="isUploading"
          class="btn btn-secondary"
        >
          取消
        </button>
        <button
          @click="handleUpload"
          :disabled="selectedFiles.length === 0 || isUploading"
          class="btn btn-primary"
        >
          {{ isUploading ? '上传中...' : `上传 ${selectedFiles.length} 个文件` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useBillsStore } from '@/stores/bills'

defineEmits<{
  close: []
  success: []
}>()

const billsStore = useBillsStore()

const fileInput = ref<HTMLInputElement>()
const selectedFiles = ref<File[]>([])
const isUploading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)
const errorMessage = ref('')

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  addFiles(files)
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  addFiles(files)
}

const addFiles = (files: File[]) => {
  errorMessage.value = ''

  for (const file of files) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      errorMessage.value = '只支持图片文件'
      continue
    }

    // 验证文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = '文件大小不能超过 5MB'
      continue
    }

    selectedFiles.value.push(file)
  }
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const handleUpload = async () => {
  if (selectedFiles.value.length === 0) return

  isUploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''

  try {
    const userId = parseInt(localStorage.getItem('userId') || '1')

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 30
      }
    }, 300)

    await billsStore.uploadBills(userId, selectedFiles.value)

    clearInterval(progressInterval)
    uploadProgress.value = 100

    // 延迟后关闭
    setTimeout(() => {
      $emit('success')
    }, 500)
  } catch (e) {
    errorMessage.value = (e as Error).message
  } finally {
    isUploading.value = false
  }
}
</script>
