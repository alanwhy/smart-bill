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
      <div class="card p-6">
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
</script>
