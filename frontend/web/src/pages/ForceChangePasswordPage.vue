<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-background text-text px-4 py-12">
    <!-- Brand -->
    <div class="mb-8 text-center">
      <div class="flex items-center justify-center gap-2.5 mb-2">
        <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M7 8V6.5C7 5.67 7.67 5 8.5 5h5C14.33 5 15 5.67 15 6.5V8" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round"/>
            <rect x="2" y="8" width="20" height="12" rx="3" fill="#F59E0B"/>
            <rect x="14" y="11" width="6" height="6" rx="3" fill="#92400E"/>
            <circle cx="17" cy="14" r="1.5" fill="#F59E0B"/>
          </svg>
        </div>
        <span class="text-2xl font-bold text-primary tracking-tight">爱理财</span>
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
