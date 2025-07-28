<template>
  <div class="view-quiz">
    <!-- Main Content -->
    <div class="main-content">
      <h2>Quiz Overview</h2>
      
      <div v-if="loading" class="loading-message">Loading quiz details...</div>
      <div v-else class="quiz-details">
        <!-- Quiz ID -->
        <div class="detail">
          <label>Quiz ID:</label>
          <div class="value">{{ quiz.id }}</div>
        </div>

        <!-- Subject -->
        <div class="detail">
          <label>Subject:</label>
          <div class="value green-box">{{ quiz.subject }}</div>
        </div>

        <!-- Chapter -->
        <div class="detail">
          <label>Chapter:</label>
          <div class="value green-box">{{ quiz.chapter_name }}</div>
        </div>

        <!-- Number of Questions -->
        <div class="detail">
          <label>Number of Questions:</label>
          <div class="value">{{ quiz.num_questions }}</div>
        </div>

        <!-- Scheduled Date -->
        <div class="detail">
          <label>Scheduled Date:</label>
          <div class="value">{{ quiz.date_of_quiz }}</div>
        </div>

        <!-- Duration -->
        <div class="detail">
          <label>Duration (hh:mm):</label>
          <div class="value">{{ formatDuration(quiz.time_duration) }}</div>
        </div>
      </div>

      <!-- Close Button -->
      <div class="action-buttons">
        <router-link to="/user-dashboard">
          <button type="button">Close</button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default {
  name: 'ViewQuiz',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const quiz = ref({});
    const loading = ref(true);
    const username = ref('User');

    const fetchQuizDetails = async () => {
      try {
        const quizId = route.params.quiz_id;
        const response = await fetch(`/api/quiz/${quizId}`);
        if (!response.ok) throw new Error('Failed to fetch quiz details');
        quiz.value = await response.json();
      } catch (error) {
        console.error("Error fetching quiz details:", error);
        alert("Failed to load quiz details. Please try again.");
      } finally {
        loading.value = false;
      }
    };

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    };

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

    onMounted(() => {
      fetchQuizDetails();
      // Fetch username from session or API if needed
    });

    return {
      quiz,
      loading,
      username,
      formatDuration,
      logout
    };
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");

.view-quiz {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
  min-height: 100vh;
}

/* Header */
.header {
  background-color: #007bff;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
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
  text-align: center;
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
}

.loading-message {
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.quiz-details {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin: 0 auto;
  text-align: left;
}

.quiz-details .detail {
  margin-bottom: 15px;
}

.quiz-details .detail label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.quiz-details .detail .value {
  padding: 8px;
  border: 2px solid #007bff;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.quiz-details .detail .value.green-box {
  border-color: #28a745;
  background-color: #e6ffe6;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.action-buttons button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}

.action-buttons button:hover {
  background-color: #0056b3;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    padding: 15px;
  }

  .quiz-details {
    padding: 15px;
  }

  .main-content h2 {
    font-size: 28px;
  }
}
</style>