<template>
  <div class="user-dashboard">
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/user-dashboard" class="active">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/scores">Scores</router-link>
        <span class="separator">|</span>
        <router-link to="/summaryuser">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span>{{ username }}</span>
        </div>
        <input
          type="text"
          class="search-bar"
          v-model="searchQuery"
          placeholder="Search quizzes..."
        />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2>Upcoming Quizzes</h2>

      <div v-if="loading" class="no-quizzes">
        <p>Loading quizzes...</p>
      </div>
      <div v-else-if="filteredQuizzes.length === 0" class="no-quizzes">
        <p>No upcoming quizzes found{{ searchQuery ? ' matching your search' : '' }}.</p>
      </div>
      <table v-else class="quiz-table">
        <thead>
          <tr>
            <th>Quiz ID</th>
            <th>Quiz Name</th>
            <th>No of Questions</th>
            <th>Date</th>
            <th>Duration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
            <td>{{ quiz.id }}</td>
            <td>{{ quiz.quiz_name }}</td>
            <td>{{ quiz.num_questions || quiz.total_questions || 0 }}</td>
            <td class="quiz-date">{{ quiz.date_of_quiz }}</td>
            <td class="quiz-duration">
              {{ formatDuration(quiz.time_duration) }}
            </td>
            <td class="action-buttons">
              <router-link :to="`/viewquiz/${quiz.id}`">
                <button class="view-button">View</button>
              </router-link>
              <router-link :to="`/startquiz/${quiz.id}`">
                <button class="start-button">Start</button>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- Reminder Button -->
    <div class="reminder-container">
      <label for="reminder-time">Set Reminder Time:</label>
      <input type="time" id="reminder-time" v-model="reminderTime">
      <button class="reminder-button" @click="updateReminder">Set</button>
    </div>
    <!-- Export Button -->
    <!-- Export Button -->
<div class="export-button-container">
  <button
    class="export-button"
    @click="exportQuizReport"
    :disabled="!userId || !userEmail"
    :title="(!userId || !userEmail) ? 'User info is still loading...' : 'Export your quiz report'"
  >
    Export Quiz Report
  </button>
</div>


  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { DateTime } from 'luxon';

export default {
  name: 'UserDashboard',
  setup() {
    const router = useRouter();
    const quizzes = ref([]);
    const loading = ref(true);
    const searchQuery = ref('');
    const username = ref('User');
    const userId = ref(null);
    const userEmail = ref('');
    const reminderTime = ref("18:00");

    const exportQuizReport = async () => {
      try {
        if (!userId.value || !userEmail.value) {
          alert("User info not loaded yet.");
          return;
        }

        const res = await fetch("/api/export_csv", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            user_id: userId.value,
            email: userEmail.value
          })
        });

        const data = await res.json();
        if (res.ok) {
          alert("Export started. You will receive an email when it's ready.");
        } else {
          alert(data.error || "Failed to start export.");
        }
      } catch (error) {
        console.error("Export failed:", error);
        alert("Error occurred while exporting quiz report.");
      }
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

    const fetchQuizzes = async () => {
      try {
        loading.value = true;
        const response = await fetch('/api/quizzess');
        if (!response.ok) throw new Error('Failed to fetch quizzes');
        quizzes.value = await response.json();
      } catch (error) {
        console.error("Error fetching quizzes:", error);
        alert("Failed to load quizzes. Please try again.");
      } finally {
        loading.value = false;
      }
    };

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    };

    const upcomingQuizzes = computed(() => {
      const currentDate = DateTime.now().toISODate();
      return quizzes.value.filter(quiz => {
        const quizDate = DateTime.fromISO(quiz.date_of_quiz).toISODate();
        return quizDate >= currentDate;
      });
    });

    const filteredQuizzes = computed(() => {
      const query = searchQuery.value.toLowerCase().trim();
      return upcomingQuizzes.value.filter(quiz =>
        quiz.quiz_name.toLowerCase().includes(query)
      );
    });

    const updateReminder = async () => {
      try {
        const [hour, minute] = reminderTime.value.split(":").map(Number);
        const response = await fetch("/api/user/reminder", {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            reminder_hour: hour,
            reminder_minute: minute
          })
        });
        const result = await response.json();
        if (response.ok) {
          alert("Reminder time updated!");
        } else {
          alert(result.error || "Failed to update reminder.");
        }
      } catch (error) {
        console.error("Reminder update failed:", error);
        alert("An error occurred while updating reminder time.");
      }
    };

    onMounted(async () => {
      await fetchQuizzes();
      try {
        // Fetch current user
        const userRes = await fetch('/api/current_user', {
          credentials: 'include'
        });
        const userData = await userRes.json();
        console.log("Fetched user data ✅", userData); // 👈 ADD THIS LINE
        if (userRes.ok) {
          username.value = userData.username;
          userId.value = userData.user_id;
          userEmail.value = userData.email;
        } else {
          console.warn("Failed to load user info.");
        }

        // Fetch reminder time
        const reminderRes = await fetch('/api/user/reminder', {
          credentials: 'include'
        });
        const reminderData = await reminderRes.json();
        if (reminderRes.ok) {
          const hour = String(reminderData.reminder_hour).padStart(2, '0');
          const minute = String(reminderData.reminder_minute ?? 0).padStart(2, '0');
          reminderTime.value = `${hour}:${minute}`;
        } else {
          console.warn("Failed to fetch reminder time, using default.");
        }
      } catch (error) {
        console.error('Error fetching user or reminder info:', error);
      }
    });

    const formattedReminderTime = computed(() => {
      const [hour, minute] = reminderTime.value.split(':').map(Number);
      return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    });

    return {
      quizzes,
      upcomingQuizzes,
      filteredQuizzes,
      loading,
      searchQuery,
      username,
      logout,
      formatDuration,
      reminderTime,
      formattedReminderTime,
      updateReminder,
      exportQuizReport,
      userId,
  userEmail, // 👈 Add these two
    };
  }
};
</script>



<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");
.export-button-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: white;
  border: 2px solid #007bff;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
  z-index: 999;
}

.export-button {
  background-color: #007bff;
  color: white;
  font-weight: bold;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.export-button:hover {
  background-color: #0056b3;
}

.reminder-container {
  position: fixed;
  bottom: 20px;
  left: 20px;
  background-color: white;
  border: 2px solid #dc3545;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  z-index: 999;
}

.reminder-container label {
  font-weight: bold;
  margin-bottom: 5px;
}

.reminder-container input[type="time"] {
  margin-bottom: 10px;
  padding: 5px 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.reminder-button {
  background-color: #dc3545;
  color: white;
  font-weight: bold;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.reminder-button:hover {
  background-color: #c82333;
}

.user-dashboard {
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
  border-radius: 5px;
  width: 200px;
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