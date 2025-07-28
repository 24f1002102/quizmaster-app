<template>
  <div class="page-wrapper">
    <div class="register-container">
      <div class="welcome-text">Welcome To Quiz Master</div>
      <form @submit.prevent="handleRegister">
        <div class="input-group">
          <label for="username">Username (email):</label>
          <input
            id="username"
            type="email"
            v-model="form.username"
            placeholder="Enter your email"
            required
          />
        </div>
        <div class="input-group">
          <label for="password">Password:</label>
          <input
            id="password"
            type="password"
            v-model="form.password"
            placeholder="Enter your password"
            required
          />
        </div>
        <div class="input-group">
          <label for="full_name">Full Name:</label>
          <input
            id="full_name"
            type="text"
            v-model="form.full_name"
            placeholder="Enter your full name"
            required
          />
        </div>
        <div class="input-group">
          <label for="qualification">Qualification:</label>
          <input
            id="qualification"
            type="text"
            v-model="form.qualification"
            placeholder="Enter your qualification"
          />
        </div>
        <div class="input-group">
          <label for="dob">Date of Birth:</label>
          <input
            id="dob"
            type="date"
            v-model="form.dob"
          />
        </div>
        <div class="button-group">
          <button type="submit" :disabled="loading">
            {{ loading ? 'Registering...' : 'Register' }}
          </button>
          <button type="button" @click="goToLogin" :disabled="loading">
            Existing User?
          </button>
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
  full_name: '',
  qualification: '',
  dob: '',
})

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

function clearMessages() {
  errorMessage.value = ''
  successMessage.value = ''
}

async function handleRegister() {
  clearMessages()
  loading.value = true

  if (!form.username || !form.password || !form.full_name) {
    errorMessage.value = 'Please fill in all required fields.'
    loading.value = false
    return
  }

  try {
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: form.username,
        password: form.password,
        fullname: form.full_name,
        qualification: form.qualification,
        dob: form.dob,
      }),
    })

    const data = await response.json()

    if (response.ok && data.success) {
      successMessage.value = 'Registration successful! Redirecting to login...'
      setTimeout(() => router.push('/login'), 2000)
    } else {
      errorMessage.value = data.message || 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
/* Ensure entire viewport is used */
.page-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f4f4f4;
  font-family: Arial, sans-serif;
}

.register-container {
  background: white;
  padding: 24px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 360px;
}

.welcome-text {
  font-family: 'Pacifico', cursive;
  font-size: 26px;
  color: #007bff;
  margin-bottom: 20px;
  white-space: nowrap;
}

form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-group {
  margin-bottom: 15px;
  width: 100%;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.input-group input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 100%;
  box-sizing: border-box;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  justify-content: center;
  width: 100%;
}

.button-group button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  flex: 1;
}

.button-group button:hover:not(:disabled) {
  background-color: #0056b3;
}

.button-group button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: red;
  margin-top: 15px;
}

.success-message {
  color: green;
  margin-top: 15px;
}
</style>
