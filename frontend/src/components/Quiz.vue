<template>
  <div>
    <!-- Header (unchanged) -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/admin-dashboard">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/quiz" class="active">Quiz</router-link>
        <span class="separator">|</span>
        <router-link to="/summary">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span id="username">{{ username }}</span>
        </div>
        <div>
          <form @submit.prevent="onSearch">
            <input 
              type="text" 
              class="search-bar" 
              v-model="searchQuery" 
              placeholder="Search quizzes/questions..." 
            />
          </form>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="subject-container">
      <template v-if="quizzes.length > 0">
        <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="subject-box">
          <div class="quiz-header">
            <h3 class="subject-name">{{ quiz.quiz_name }}</h3>
            <button @click="deleteQuiz(quiz.id)" class="delete-btn">Delete Quiz</button>
          </div>
          
          <div class="quiz-meta">
            <span>Chapter {{ quiz.chapter_id }}</span>
            <span>Due: {{ quiz.date_of_quiz }}</span>
            <span>{{ quiz.time_duration }} minutes</span>
          </div>

          <table>
            <thead>
              <tr>
                <th>Question ID</th>
                <th>Question Text</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="question in filteredQuestions(quiz.id)" :key="question.id">
                <td class="chapter-id-cell">{{ question.id }}</td>
                <td>{{ question.title }}</td>
                <td>
                  <router-link :to="`/edit-question/${question.id}`">
                    <button class="edit-btn">Edit</button>
                  </router-link>
                  <button @click="deleteQuestion(question.id)" class="delete-btn">Delete</button>
                </td>
              </tr>
              <tr v-if="filteredQuestions(quiz.id).length === 0">
                <td colspan="3" style="text-align: center;">
                  No questions found
                </td>
              </tr>
            </tbody>
          </table>

          <div class="add-chapter-container">
            <router-link :to="`/newquestion?quiz_id=${quiz.id}`">
              <button class="add-chapter-button">+ Add Question</button>
            </router-link>
          </div>
        </div>
      </template>
      <div v-else class="no-subjects-message-container">
        <div class="no-subjects-message">
          <h2>No quizzes found. Create your first quiz to get started!</h2>
          <router-link to="/newquiz">
            <button class="add-subject-button">+ Create New Quiz</button>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Global Add Button -->
    <router-link to="/newquiz">
      <button class="global-add-button">+</button>
    </router-link>
  </div>
</template>

<script>
export default {
  name: "Quiz",
  data() {
    return {
      username: "Admin",
      searchQuery: this.$route.query.query || "",
      quizzes: [],
      questions: [],
    };
  },
  computed: {
    filteredQuizzes() {
      if (!this.searchQuery) return this.quizzes;
      
      const q = this.searchQuery.toLowerCase();
      return this.quizzes.filter(quiz => 
        quiz.quiz_name.toLowerCase().includes(q) ||
        this.questions.some(question => 
          question.quiz_id === quiz.id && 
          question.title.toLowerCase().includes(q)
        )
      );
    }
  },
  methods: {
    fetchData() {
      // Fetch quizzes
      fetch(`/api/quizzes${this.searchQuery ? `?query=${encodeURIComponent(this.searchQuery)}` : ''}`)
        .then((res) => res.json())
        .then((data) => {
          this.quizzes = data || [];
        })
        .catch((err) => console.error("Error fetching quizzes:", err));

      // Fetch questions
      fetch("/api/questions")
        .then((res) => res.json())
        .then((data) => {
          this.questions = data || [];
        })
        .catch((err) => console.error("Error fetching questions:", err));
    },
    
    filteredQuestions(quizId) {
      if (!this.searchQuery) {
        return this.questions.filter(q => q.quiz_id === quizId);
      }
      
      const q = this.searchQuery.toLowerCase();
      return this.questions.filter(question => 
        question.quiz_id === quizId && 
        question.title.toLowerCase().includes(q)
      );
    },
    
    onSearch() {
      this.$router.push({ path: "/quiz", query: { query: this.searchQuery } });
    },
    
    deleteQuestion(questionId) {
      if (confirm("Are you sure you want to delete this question?")) {
        fetch(`/api/delete_question/${questionId}`, {
          method: "DELETE",
        })
          .then((res) => {
            if (res.ok) {
              this.questions = this.questions.filter((q) => q.id !== questionId);
            } else {
              alert("Failed to delete question.");
            }
          })
          .catch(() => alert("Error deleting question."));
      }
    },
    async deleteQuiz(quizId) {
      if (!confirm('Are you sure you want to delete this quiz and all its questions?')) {
        return;
      }

      try {
        const response = await fetch(`/api/delete-quiz/${quizId}`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error('Failed to delete quiz');
        }

        // Remove quiz from local state
        this.quizzes = this.quizzes.filter(q => q.id !== quizId);
        // Remove associated questions
        this.questions = this.questions.filter(q => q.quiz_id !== quizId);

      } catch (error) {
        console.error('Error deleting quiz:', error);
        alert('Failed to delete quiz');
      }
    },

    
    logout() {
      // Optional backend logout
      fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      })
        .then(res => {
          // On success or failure, always remove local state and redirect
          localStorage.removeItem('loggedIn');
          this.$router.push('/login');
        })
        .catch(() => {
          localStorage.removeItem('loggedIn');
          this.$router.push('/login');
        });
    },
  },
  watch: {
    "$route.query.query"(newQuery) {
      this.searchQuery = newQuery || "";
      this.fetchData();
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");

body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
  min-height: 100vh;
}
.no-subjects-message-container {
  position: absolute;
  bottom: 20px;
  width: 100%;
  display: flex;
  justify-content: center;
}
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.no-subjects-message {
  text-align: center;
}

.add-subject-button {
  background-color: #28a745;
  color: white;
  padding: 15px 30px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s, transform 0.2s;
}

.add-subject-button:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

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
.header .search-bar {
  padding: 10px;
  border: none;
  border-radius: 10px;
  width: 250px;
}
.header .welcome-message {
  font-weight: bold;
}
.subject-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 15px;
  margin-top: 80px;
}
.subject-box {
  border: 2px solid black;
  padding: 15px;
  border-radius: 10px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
.subject-name {
  text-align: left;
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  padding-bottom: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}
table th,
table td {
  padding: 7px;
  text-align: center;
  border-bottom: 1px solid #ddd;
}
table th {
  text-align: center;
  background-color: #007bff;
  color: white;
}
table tr:hover {
  background-color: #f1f1f1;
}
.action-buttons {
  display: flex;
  gap: 10px;
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
.action-buttons button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.edit-button {
  background-color: #28a745;
  color: white;
}
.delete-button {
  background-color: #dc3545;
  color: white;
}
.edit-button:hover {
  background-color: #218838;
}
.delete-button:hover {
  background-color: #c82333;
}
.add-chapter-button {
  background-color: #ff69b4;
  color: black;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 20px;
}
.add-chapter-button:hover {
  background-color: #ff1493;
}
.global-add-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #ff8c42;
  color: white;
  width: 60px;
  height: 60px;
  border-radius: 70%;
  border: none;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
.global-add-button:hover {
  background-color: #ff7b33;
}
.nav-links a.active {
  text-decoration: underline;
}
.delete-btn {
  background-color: white;
  color: red;
  border: 2px solid red;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
}
.delete-btn:hover {
  background-color: red;
  color: white;
}
.add-chapter-container {
  text-align: center;
  margin-top: 10px;
}
.edit-btn {
  background-color: #17b84d;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin-right: 5px;
}
.edit-btn:hover {
  background-color: darkgreen;
}
.no-subjects-message {
  text-align: center;
  margin-top: 50px;
}
.no-subjects-message h2 {
  font-family: "Bangers", cursive;
  font-size: 24px;
  color: #007bff;
  margin-bottom: 20px;
}
.add-subject-button {
  background-color: #28a745;
  color: white;
  padding: 15px 30px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 18px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s, transform 0.2s;
  display: block;
  margin: 0 auto;
}
.add-subject-button:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}
.add-subject-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.no-quiz-message {
  color: #666;
  font-style: italic;
  margin-right: 10px;
}
.create-quiz-btn {
  background-color: #17b84d;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin-right: 5px;
}
.create-quiz-btn:hover {
  background-color: #138496;
}
.chapter-id-cell {
  font-weight: bold;
  color: #333;
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

/* Quiz meta styles */
.quiz-meta {
  display: flex;
  justify-content: left;
  gap: 10px;
  margin-bottom: 30px;
}

.quiz-meta span {
  color: #000000;
  background-color: #e0e0e0;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
}
</style>