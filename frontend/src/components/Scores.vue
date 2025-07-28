<template>
  <div class="user-dashboard">
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/user-dashboard">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/scores" class="active">Scores</router-link>

        <span class="separator">|</span>
        <router-link to="/summaryuser">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span>{{ username }}</span>
        </div>
        <input v-model="searchQuery" class="search-bar" placeholder="Search by quiz/subjects/chapters..." />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2>Your Quiz Scores</h2>

      <table class="quiz-table" v-if="filteredScores.length">
        <thead>
          <tr>
            <th>Quiz Name</th>
            <th>Subject</th>
            <th>Chapter</th>
            <th>Questions</th>
            <th>Score</th>
            <th>Time</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in filteredScores" :key="quiz.id">
            <td>{{ quiz.quiz_name }}</td>
            <td>{{ quiz.subject_name }}</td>
            <td>{{ quiz.chapter_name }}</td>
            <td>{{ quiz.num_questions }}</td>
            <td>{{ quiz.total_scored }} / {{ quiz.num_questions }}</td>
            <td class="quiz-duration">{{ quiz.time_duration }} mins</td>
            <td class="quiz-date">{{ formatDate(quiz.date_attempted) }}</td>
          </tr>
        </tbody>
      </table>

      <p v-else class="no-quizzes">No quizzes found</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      scores: [],
      searchQuery: '',
      username: 'User',  // default username
    };
  },
  computed: {
    filteredScores() {
      const query = this.searchQuery.toLowerCase();
      return this.scores.filter(score =>
        score.quiz_name.toLowerCase().includes(query) ||
        score.subject_name.toLowerCase().includes(query) ||
        score.chapter_name.toLowerCase().includes(query)
      );
    },
  },
  methods: {
    logout() {
      fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      }).finally(() => {
        localStorage.removeItem('loggedIn');
        this.$router.push('/login');
      });
    },
    fetchScores() {
      fetch('http://localhost:5000/api/scores', {
        method: 'GET',
        credentials: 'include'
      })
        .then(res => res.json())
        .then(data => {
          this.scores = data;
        })
        .catch(err => {
          console.error('Error fetching scores:', err);
          this.scores = [];
        });
    },
    fetchUsername() {
      fetch('http://localhost:5000/api/current_user', {
        credentials: 'include',
      })
        .then(res => res.json())
        .then(data => {
          if (data.username) {
            this.username = data.username;
          }
        })
        .catch(error => {
          console.error('Error fetching username:', error);
        });
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleString();
    },
  },
  mounted() {
    this.fetchScores();
    this.fetchUsername(); // ✅ now included in mounted()
  },
};
</script>


<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");

.user-dashboard {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
  min-height: 100vh;
}
nav-link-button {
  background: none;
  border: none;
  color: white;
  font-weight: bold;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
  margin: 0;
}
.header .welcome-message {
  font-weight: bold;
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

/* Header */
.header {
  background-color: #007bff;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
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

.header .nav-links a.active {
  text-decoration: underline;
}

.header .nav-links .separator {
  color: white;
  font-weight: bold;
}

.header .search-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header .search-bar {
  padding: 10px;
  border: none;
  border-radius: 10px;
  width: 300px;
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

/* Main Content */
.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.main-content h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #007bff;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.quiz-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.quiz-table th, .quiz-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.quiz-table th {
  background-color: #007bff;
  color: white;
  position: sticky;
  top: 60px;
}

.quiz-table tr:hover {
  background-color: #f1f1f1;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-buttons button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  min-width: 100px;
}

.view-button {
  background-color: #007bff;
  color: white;
}

.start-button {
  background-color: #28a745;
  color: white;
}

.start-button:hover {
  background-color: #218838;
}

.view-button:hover {
  background-color: #0056b3;
}

.no-quizzes {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.quiz-date {
  white-space: nowrap;
}

.quiz-duration {
  white-space: nowrap;
}

.disabled-button {
  background-color: #cccccc !important;
  color: #666666 !important;
  cursor: not-allowed !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }

  .header .search-container {
    width: 100%;
    justify-content: center;
  }

  .header .search-bar {
    width: 100%;
  }

  .quiz-table {
    display: block;
    overflow-x: auto;
  }

  .action-buttons {
    flex-direction: column;
    gap: 5px;
  }

  .action-buttons button {
    width: 100%;
  }
}
</style>
