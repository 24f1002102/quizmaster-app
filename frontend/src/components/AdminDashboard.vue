<template>
  <div>
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <router-link to="/admin-dashboard" class="active">Home</router-link>
        <span class="separator">|</span>
        <router-link to="/quiz">Quiz</router-link>
        <span class="separator">|</span>
        <router-link to="/summary">Summary</router-link>
        <span class="separator">|</span>
        <button @click="logout" class="nav-link-button">Logout</button>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span id="username">Admin</span>
        </div>
        <div>
          <form @submit.prevent="searchSubjects">
            <input type="text" class="search-bar" v-model="searchQuery" placeholder="Search subjects/chapters..." />
          </form>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="subject-container">
      <div v-if="filteredSubjects.length === 0" class="no-subjects-message-container">
        <div class="no-subjects-message">
          <h2>No subjects found or chapters. Add a new subject to get started!</h2>
          <button class="add-subject-button" @click="$router.push('/admin/new-subject')">
            + Add New Subject
          </button>
        </div>
      </div>

      <div v-else v-for="subject in filteredSubjects" :key="subject.id" class="subject-box">
        <h3 class="subject-name">{{ subject.name }}</h3>

        <form @submit.prevent="deleteSubject(subject.id)" style="display: inline;">
          <button type="submit" class="delete-btn">Delete Subject</button>
        </form>

        <table>
          <thead>
            <tr>
              <th>Chapter ID</th>
              <th>Chapter Name</th>
              <th>No. of Questions</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="chapter in getChaptersBySubject(subject.id)" :key="chapter.id">
              <td class="chapter-id-cell">{{ chapter.id }}</td>
              <td>{{ chapter.name }}</td>
              <td>{{ chapter.question_count }}</td>
              <td>
                <template v-if="chapter.question_count > 0">
                  <!-- Show only edit and delete for chapters with questions -->
                  <router-link :to="`/edit-chapter/${chapter.id}`">
                    <button class="edit-btn">Edit</button>
                  </router-link>
                  <form @submit.prevent="deleteChapter(chapter.id)" style="display: inline;">
                    <button type="submit" class="delete-btn">Delete</button>
                  </form>
                </template>
                <template v-else-if="chapter.has_quiz">
                  <router-link :to="`/edit-chapter/${chapter.id}`">
                    <button class="edit-btn">Edit</button>
                  </router-link>
                  <form @submit.prevent="deleteChapter(chapter.id)" style="display: inline;">
                    <button type="submit" class="delete-btn">Delete</button>
                  </form>
                </template>
                <template v-else>
                  <span class="no-quiz-message">No quiz found</span>
                  <router-link :to="`/newquiz?chapter_id=${chapter.id}`">
                    <button class="create-quiz-btn">Create Quiz</button>
                  </router-link>
                  <form @submit.prevent="deleteChapter(chapter.id)" style="display: inline;">
                    <button type="submit" class="delete-btn">Delete</button>
                  </form>
                </template>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="add-chapter-container">
          <router-link :to="`/new-chapter/${subject.id}`">
            <button class="add-chapter-button">+ Add Chapter</button>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Global Add Subject Button -->
    <router-link to="/new-subject">
      <button class="global-add-button">+</button>
    </router-link>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: "",
      subjects: [],
      chapters: [],
    };
  },
  computed: {
    filteredChapters() {
      if (!this.searchQuery.trim()) return this.chapters;
      const query = this.searchQuery.toLowerCase();
      return this.chapters.filter(chapter =>
        chapter.name.toLowerCase().includes(query) ||
        (chapter.subject_name && chapter.subject_name.toLowerCase().includes(query))
      );
    },
    filteredSubjects() {
      if (!this.searchQuery.trim()) return this.subjects;
      const query = this.searchQuery.toLowerCase();
      return this.subjects.filter(subject => {
        const matchesSubject = subject.name?.toLowerCase().includes(query);
        const matchesChapter = this.chapters.some(ch =>
          ch.subject_id === subject.id &&
          ch.name?.toLowerCase().includes(query)
        );
        return matchesSubject || matchesChapter;
      });
    }
  },
  methods: {
    deleteSubject(subjectId) {
      if (!confirm('Are you sure you want to delete this subject and all its chapters?')) return;
      fetch(`/api/delete-subject/${subjectId}`, {
        method: 'DELETE'
      })
        .then(res => {
          if (!res.ok) throw new Error('Delete failed');
          this.subjects = this.subjects.filter(sub => sub.id !== subjectId);
        })
        .catch(err => {
          console.error(err);
          alert('Failed to delete subject');
        });
    },
    logout() {
      fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      })
        .then(res => {
          localStorage.removeItem('loggedIn');
          this.$router.push('/login');
        })
        .catch(() => {
          localStorage.removeItem('loggedIn');
          this.$router.push('/login');
        });
    },
    getChaptersBySubject(subjectId) {
      return this.chapters.filter(ch => ch.subject_id === subjectId);
    },
    searchSubjects() {
      // Computed takes care of filtering
    },
    deleteChapter(chapterId) {
      fetch(`/api/delete-chapter/${chapterId}`, { method: 'DELETE' })
        .then(res => {
          if (res.ok) {
            this.chapters = this.chapters.filter(ch => ch.id !== chapterId);
          } else {
            console.error('Failed to delete chapter');
          }
        })
        .catch(err => {
          console.error('Error deleting chapter:', err);
        });
    }
  },
  mounted() {
    // Fetch subjects
    fetch('/api/subjects')
      .then(res => res.json())
      .then(data => this.subjects = data);

    // Fetch chapters with question counts and quiz info
    fetch('/api/chapters-with-questions')
      .then(res => res.json())
      .then(data => this.chapters = data);
  }
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
  text-align: center;
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
  background-color: #28a745;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin-right: 5px;
}
.edit-btn:hover {
  background-color: #218838;
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
  background-color: #28a745;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin-right: 5px;
}
.create-quiz-btn:hover {
  background-color: #218838;
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
</style>