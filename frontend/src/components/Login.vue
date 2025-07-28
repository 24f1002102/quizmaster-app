<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="welcome-text">Welcome To Quiz Master</div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username (email):</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Enter your email"
            required
          />
        </div>

        <div class="input-group">
          <label for="password">Password:</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Enter your password"
            required
          />
        </div>

        <div class="button-group">
          <button type="submit">Login</button>
          <button type="button" @click="goToRegister">Create New User?</button>
        </div>
      </form>

      <!-- ✅ Success/Error Messages moved out of button group -->
      <div class="message-container">
        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const loading = ref(false)

function clearMessages() {
  successMessage.value = ''
  errorMessage.value = ''
}

async function handleLogin() {
  clearMessages()
  loading.value = true

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    })

    const data = await response.json()
    console.log('Login Response:', data)

    if (response.ok && data.success) {
      localStorage.setItem('loggedIn', 'true')
      successMessage.value = 'Login successful! Redirecting...'

      setTimeout(() => {
        if (data.role === 'admin') {
          router.push('/admin-dashboard')
        } else {
          router.push('/user-dashboard')
        }
      }, 1000)
    } else {
      errorMessage.value = data.message || 'Invalid username or password'
    }
  } catch (err) {
    console.error('Login error:', err)
    errorMessage.value = 'An error occurred while logging in'
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

onMounted(() => {
  window.onpageshow = function (event) {
    if (event.persisted) {
      window.location.reload()
    }
  }
})
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');

.login-container {
  background: white;
  padding: 20px;
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
}

.button-group button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.button-group button:hover {
  background-color: #0056b3;
}

.message-container {
  margin-top: 20px;
}

.success-text {
  font-family: cursive;
  color: green;
  
}

.error-text {
  color: red;
  font-family: cursive;
}
</style>

<style>
html,
body,
#app,
.login-wrapper {
  height: 100%;
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
}

.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
