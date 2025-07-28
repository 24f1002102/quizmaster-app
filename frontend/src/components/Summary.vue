<template>
  <div class="summary-container">
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/admin-dashboard">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/quiz">Quiz</router-link>
        <span class="separator">|</span>
        <router-link to="/summary" class="active">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span id="username">Admin</span>
        </div>
        <div>
          <form @submit.prevent="searchSubjects">
            <input type="text" class="search-bar" v-model="searchQuery" placeholder="Search users..." />
          </form>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2>Summary Charts</h2>
      <div class="charts-container">
        <!-- Subject-wise Top Scores (Bar Chart) -->
        <div class="chart">
          <h3>Subject-wise Top Scores</h3>
          <canvas ref="topScoresChart"></canvas>
        </div>

        <!-- Subject-wise User Attempts (Radar Chart) -->
        <div class="chart">
          <h3>Subject-wise User Attempts</h3>
          <canvas ref="userAttemptsChart"></canvas>
        </div>
      </div>
    </div>
  </div><!-- User Table Section -->
  <div class="user-table-section">
    <h2 class="registered-users-title">Registered Users</h2>
    <table class="user-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Name</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.full_name }}</td>
          <td>
            <button @click="removeUser(user.id)" class="remove-button">Remove</button>
          </td>
        </tr>
     </tbody>
    </table>
  </div>

  
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';
import { useRouter } from 'vue-router';

export default {
  name: 'Summary',
  setup() {
    const topScoresChart = ref(null);
    const userAttemptsChart = ref(null);
    const chartInstances = ref([]);
    const router = useRouter();

    // Chart data
    const subjects = ref([]);
    const topScores = ref([]);
    const userAttempts = ref([]);

    // User table data
    const users = ref([]);
    const searchQuery = ref('');

    const logout = () => {
      fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      })
        .then(() => {
          localStorage.removeItem('loggedIn');
          router.push('/login');
        })
        .catch(() => {
          localStorage.removeItem('loggedIn');
          router.push('/login');
        });
    };

    const fetchSummaryData = async () => {
      try {
        const response = await fetch('/api/summary', {
          credentials: 'include'
        });
        const result = await response.json();
        subjects.value = result.subjects;
        topScores.value = result.top_scores;
        userAttempts.value = result.user_attempts;
        initCharts();
      } catch (error) {
        console.error("Failed to fetch summary data:", error);
      }
    };

    const fetchUsers = async () => {
      try {
        const res = await fetch('/api/users', {
          credentials: 'include'
        });
        const data = await res.json();
        users.value = data; // expecting flat array of user objects
      } catch (error) {
        console.error("Failed to fetch users:", error);
      }
    };

    const filteredUsers = computed(() => {
      return users.value.filter(user =>
        user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        user.full_name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    const removeUser = async (userId) => {
      if (confirm('Are you sure you want to remove this user?')) {
        try {
          const res = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
          });
          if (res.ok) {
            users.value = users.value.filter(u => u.id !== userId);
          }
        } catch (err) {
          console.error("Error removing user:", err);
        }
      }
    };

    const searchSubjects = () => {
      // Optional: Add subject search logic if needed
    };

    const initCharts = () => {
      // Destroy old charts if any
      chartInstances.value.forEach(chart => chart.destroy());
      chartInstances.value = [];

      const topScoresCtx = topScoresChart.value.getContext('2d');
      const userAttemptsCtx = userAttemptsChart.value.getContext('2d');

      const topScoresChartInstance = new Chart(topScoresCtx, {
        type: 'bar',
        data: {
          labels: subjects.value,
          datasets: [{
            label: 'Top Scores',
            data: topScores.value,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 },
              title: {
                display: true,
                text: 'Scores',
                font: { weight: 'bold' }
              }
            },
            x: {
              title: {
                display: true,
                text: 'Subjects',
                font: { weight: 'bold' }
              }
            }
          },
          plugins: {
            legend: { position: 'top' }
          }
        }
      });

      const userAttemptsChartInstance = new Chart(userAttemptsCtx, {
        type: 'radar',
        data: {
          labels: subjects.value,
          datasets: [{
            label: 'User Attempts',
            data: userAttempts.value,
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            pointBackgroundColor: 'rgba(255, 159, 64, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          scales: {
            r: {
              suggestedMin: 0,
              ticks: { stepSize: 1, backdropColor: 'transparent' },
              pointLabels: { font: { size: 12 } }
            }
          },
          plugins: {
            legend: { position: 'top' },
            tooltip: {
              callbacks: {
                label: ctx => `${ctx.dataset.label}: ${ctx.raw}`
              }
            }
          },
          elements: {
            line: { tension: 0.1 }
          }
        }
      });

      chartInstances.value.push(topScoresChartInstance, userAttemptsChartInstance);

      // Re-render on resize
      window.addEventListener('resize', () => {
        topScoresChartInstance.resize();
        userAttemptsChartInstance.resize();
      });
    };

    onMounted(() => {
      fetchSummaryData();
      fetchUsers();
    });

    return {
      topScoresChart,
      userAttemptsChart,
      logout,
      users,
      filteredUsers,
      searchQuery,
      removeUser,
      searchSubjects
    };
  }
};
</script>




<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");

.user-table-section {
  margin: 2rem;
}
.registered-users-title {
  letter-spacing: 0.4rem;

  font-family: 'Bangers', cursive;
  color: rgb(11, 189, 11);
}
.user-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.user-table th {
  background-color: orange;
  color: white;
  padding: 10px;
  text-align: left;
}

.user-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.remove-button {
  background-color: red;
  color: white;
  border: none;
  padding: 6px 12px;
  cursor: pointer;
  border-radius: 4px;
}

.remove-button:hover {
  background-color: darkred;
}

.summary-container {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
  min-height: 100vh;
}
.header .search-bar {
  padding: 10px;
  border: none;
  border-radius: 10px;
  width: 250px;
}
/* Header */
.header {
  background-color: #007bff;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}

.header .nav-links {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header .nav-links a {
  color: white;
  text-decoration: none;
  font-weight: bold;
}

.header .nav-links a:hover {
  text-decoration: underline;
}

.header .nav-links .separator {
  color: white;
  font-weight: bold;
}

.header .search-container {
  display: flex;
  margin-right: 30px;
  align-items: center;
  gap: 10px;
}

.header .welcome-message {
  font-weight: bold;
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

.nav-links a.active {
  text-decoration: underline;
}

/* Main Content */
.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 70px auto 0;
}

.main-content h2 {
  font-family: "Bangers", cursive;
  font-size: 36px;
  color: #007bff;
  margin-bottom: 30px;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  text-align: center;
}

/* Charts Container */
.charts-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
  margin-top: 20px;
}

/* Chart Styles */
.chart {
  background-color: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  width: 500px;
  max-width: 100%;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.chart:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.chart h3 {
  font-family: "Bangers", cursive;
  font-size: 24px;
  color: #28a745;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
    height: auto;
  }

  .header .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .header .search-container {
    margin: 10px 0 0 0;
    flex-direction: column;
  }

  .main-content {
    margin-top: 120px;
  }

  .main-content h2 {
    font-size: 28px;
  }

  .chart {
    width: 100%;
    padding: 15px;
  }

  .charts-container {
    gap: 20px;
  }
}
</style>