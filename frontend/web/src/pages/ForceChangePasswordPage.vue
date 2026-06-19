<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-background text-text px-4 py-12">
    <!-- Brand -->
    <div class="mb-8 text-center">
      <div class="flex items-center justify-center gap-2.5 mb-2">
        <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 11c0-1.1-.9-2-2-2s-2 .9-2 2 .9 2 2 2 2-.9 2-2zm6 0V7a6 6 0 10-12 0v4M5 11h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2v-8a2 2 0 012-2z" />
          </svg>
        </div>
        <span class="text-2xl font-bold text-primary tracking-tight">Smart Bill</span>
      </div>
      <p class="text-sm text-text-muted">首次登录请修改初始密码</p>
    </div>

    <!-- Card -->
    <div class="w-full max-w-sm card p-8">
      <h2 class="text-xl font-semibold text-text mb-2">修改密码</h2>
      <p class="text-xs text-text-muted mb-5">为了账号安全，请先设置新密码再继续使用</p>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm text-text-secondary mb-1.5">当前密码</label>
          <input
            v-model="form.oldPassword"
            type="password"
            class="input w-full"
            placeholder="请输入当前密码"
            :disabled="isLoading"
            autocomplete="current-password"
          />
        </div>
        <div>
          <label class="block text-sm text-text-secondary mb-1.5">新密码</label>
          <input
            v-model="form.newPassword"
            type="password"
            class="input w-full"
            placeholder="至少 6 位"
            :disabled="isLoading"
            autocomplete="new-password"
          />
        </div>
        <div>
          <label class="block text-sm text-text-secondary mb-1.5">确认新密码</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            class="input w-full"
            placeholder="再次输入新密码"
            :disabled="isLoading"
            autocomplete="new-password"
          />
        </div>

        <p v-if="errorMsg" class="text-sm text-error">{{ errorMsg }}</p>

        <div class="flex flex-col gap-2 pt-1">
          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isLoading ? '保存中...' : '保存并继续' }}
          </button>
          <button
            type="button"
            @click="handleCancel"
            :disabled="isLoading"
            class="btn btn-secondary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            退出登录
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const isLoading = ref(false)
const errorMsg = ref('')

const handleSubmit = async () => {
  errorMsg.value = ''
  if (!form.value.oldPassword || !form.value.newPassword || !form.value.confirmPassword) {
    errorMsg.value = '请填写所有字段'
    return
  }
  if (form.value.newPassword.length < 6) {
    errorMsg.value = '新密码至少 6 位'
    return
  }
  if (form.value.newPassword !== form.value.confirmPassword) {
    errorMsg.value = '两次输入的新密码不一致'
    return
  }
  if (form.value.newPassword === form.value.oldPassword) {
    errorMsg.value = '新密码不能与旧密码相同'
    return
  }

  isLoading.value = true
  try {
    await authApi.changePassword(form.value.oldPassword, form.value.newPassword)
    authStore.markPasswordChanged()
    await authStore.fetchCycle()
    router.replace({ name: 'Dashboard' })
  } catch (e) {
    errorMsg.value = (e as Error).message || '修改失败，请重试'
  } finally {
    isLoading.value = false
  }
}

const handleCancel = () => {
  authStore.logout()
  router.replace({ name: 'Login' })
}
</script>
