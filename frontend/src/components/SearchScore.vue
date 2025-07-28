<template>
  <div>
    <!-- Header -->
    <div class="header">
      <div class="nav-links">
        <RouterLink to="/dashboard">Home</RouterLink>
        <span class="separator">|</span>
        <RouterLink to="/scores">Scores</RouterLink>
        <span class="separator">|</span>
        <RouterLink to="/summary">Summary</RouterLink>
        <span class="separator">|</span>
        <a href="/logout">Logout</a>
      </div>
      <div class="search-container">
        <div class="welcome-message">
          Welcome <span>{{ username }}</span>
        </div>
        <form @submit.prevent="fetchSearchResults">
          <input
            type="text"
            class="search-bar"
            v-model="searchQuery"
            placeholder="Search by date/score..."
          />
        </form>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2>Quiz Search Results</h2>
      <table v-if="searchResults.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>No. of Questions</th>
            <th>Date</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in searchResults" :key="quiz.id">
            <td>{{ quiz.id }}</td>
            <td>{{ quiz.num_questions }}</td>
            <td>{{ quiz.time_stamp }}</td>
            <td>{{ quiz.total_scored }}/{{ quiz.num_questions }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else>
        <p>No results found.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchScore',
  data() {
    return {
      username: '',
      searchQuery: this.$route.query.query || '',
      searchResults: []
    };
  },
  mounted() {
    this.username = localStorage.getItem('username') || 'User';
    this.fetchSearchResults();
  },
  methods: {
    async fetchSearchResults() {
      try {
        const queryParam = this.searchQuery ? `?query=${encodeURIComponent(this.searchQuery)}` : '';
        const res = await fetch(`/api/searchscore${queryParam}`, {
          credentials: 'include'
        });
        const data = await res.json();
        this.searchResults = data.search_results || [];
      } catch (error) {
        console.error('Failed to fetch search results:', error);
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Bangers&display=swap');

body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f4;
}
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
.header .nav-links a:hover,
.header .nav-links a.active {
  text-decoration: underline;
}
.header .nav-links .separator {
  font-weight: bold;
}
.header .search-container {
  display: flex;
  align-items: center;
  gap: 10px;
}
.header .search-bar {
  padding: 8px;
  border: none;
  border-radius: 5px;
  width: 200px;
}
.header .welcome-message {
  font-weight: bold;
}
.main-content {
  padding: 20px;
  text-align: center;
}
.main-content h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #007bff;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}
table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
}
th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
th {
  background-color: #007bff;
  color: white;
}
tr:hover {
  background-color: #f1f1f1;
}
</style>
