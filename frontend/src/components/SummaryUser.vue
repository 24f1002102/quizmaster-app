<template>
  <div>
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/user-dashboard">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/scores">Scores</router-link>
        <span class="separator">|</span>
        <router-link to="/summary-user" class="active">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="welcome-message">
        Welcome {{ username }}
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2>Summary</h2>
      <div class="chart-container">
        <!-- Bar Chart -->
        <div class="chart">
          <h3>Subject-wise No. of Quizzes Attended</h3>
          <canvas ref="subjectChartCanvas"></canvas>
        </div>

        <!-- Pie Chart -->
        <div class="chart">
          <h4>Month-wise No. of Quizzes Attempted</h4>
          <canvas ref="monthChartCanvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js/auto';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('User');

const subjects = ref([]);
const quizzesAttended = ref([]);
const months = ref([]);
const quizzesAttempted = ref([]);

const subjectChartCanvas = ref(null);
const monthChartCanvas = ref(null);

// Logout function
const logout = () => {
  fetch('/api/logout', {
    method: 'POST',
    credentials: 'include',
  })
    .then(() => {
      localStorage.removeItem('loggedIn');
      localStorage.removeItem('username');
      router.push('/login');
    })
    .catch(() => {
      localStorage.removeItem('loggedIn');
      localStorage.removeItem('username');
      router.push('/login');
    });
};

onMounted(async () => {
  try {
    // Fetch username from session
    const userRes = await fetch('/api/current_user', { credentials: 'include' });
    const userData = await userRes.json();
    if (userData.username) {
      username.value = userData.username;
      localStorage.setItem('username', userData.username);
    }

    // Fetch summary data
    const response = await fetch('/api/user-summary', { credentials: 'include' });
    const data = await response.json();

    subjects.value = data.subjects;
    quizzesAttended.value = data.quizzes_attended;
    months.value = data.months.reverse();
    quizzesAttempted.value = data.quizzes_attempted.reverse();

    new Chart(subjectChartCanvas.value, {
      type: 'bar',
      data: {
        labels: subjects.value,
        datasets: [{
          label: 'Quizzes Attended',
          data: quizzesAttended.value,
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Quizzes'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Subjects'
            }
          }
        }
      }
    });

    new Chart(monthChartCanvas.value, {
      type: 'pie',
      data: {
        labels: months.value,
        datasets: [{
          label: 'Quizzes Attempted',
          data: quizzesAttempted.value,
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom'
          },
          title: {
            display: true,
            text: 'Quizzes Attempted by Month'
          }
        }
      }
    });

  } catch (err) {
    console.error('Error fetching data:', err);
  }
});
</script>


<style scoped>
body {
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
}

/* Header */
.header {
  background-color: #007bff;
  padding: 25px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}
.nav-link-button {
  background: none;
  border: none;
  color: white;
  font-weight: bold;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
  margin: 0;
}

.nav-link-button:hover {
  text-decoration: underline;
}

.nav-link-button:focus {
  outline: none;
  box-shadow: none;
}
.logout-link {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.logout-link:hover {
  background-color: #0056b3;
}

.nav-links {
  display: flex;
  gap: 10px;
  align-items: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: bold;
}

.nav-links a:hover {
  text-decoration: underline;
}

.nav-links a.active {
  text-decoration: underline;
}

.separator {
  color: white;
  font-weight: bold;
}

.welcome-message {
  font-weight: bold;
}

/* Main Content */
.main-content {
  padding: 20px;
  text-align: center;
}

.main-content h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #0325ff;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

/* Charts Container */
.chart-container {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  flex-wrap: wrap;
}

/* Chart Styles */
.chart {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(117, 234, 7, 0.1);
  width: 45%;
  margin-bottom: 20px;
}

.chart h3 {
  font-size: 24px;
  color: #63e009;
  margin-bottom: 10px;
}

.chart h4 {
  font-size: 24px;
  color: #ff0000;
  margin-bottom: 10px;
}

canvas {
  max-width: 100%;
}

@media (max-width: 768px) {
  .chart {
    width: 100%;
  }
}
</style>
