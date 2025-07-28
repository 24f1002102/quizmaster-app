<template>
  <div class="new-quiz-container">
    <div class="form-container">
      <h2>Create New Quiz</h2>
      <form @submit.prevent="handleSubmit">
        <!-- Quiz Name Field -->
        <div class="input-group">
          <label for="quiz_name">Quiz Name:</label>
          <input
            type="text"
            id="quiz_name"
            v-model="formData.quiz_name"
            placeholder="Enter quiz name"
            required
          />
        </div>

        <!-- Chapter ID Field -->
        <!-- Chapter ID Field (Dropdown) -->
<div class="input-group">
  <label for="chapter_id">Chapter ID:</label>
  <select id="chapter_id" v-model="formData.chapter_id" required>
    <option value="" disabled>Select chapter</option>
    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
      {{ chapter.id }}-{{ chapter.name }}
    </option>
  </select>
</div>


        <!-- Due Date Field -->
        <div class="input-group">
          <label for="date_of_quiz">Due Date:</label>
          <input
            type="date"
            id="date_of_quiz"
            v-model="formData.date_of_quiz"
            required
          />
        </div>

        <!-- Duration Field -->
        <div class="input-group">
          <label for="time_duration">Duration (minutes):</label>
          <input
            type="number"
            id="time_duration"
            v-model="formData.time_duration"
            placeholder="Enter duration in minutes"
            required
            min="1"
          />
        </div>

        <div class="button-group">
          <button type="submit" class="primary-btn">
            Save Quiz
          </button>
          <router-link to="/quiz" class="secondary-btn">
            Cancel
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "NewQuiz",
  data() {
    return {
      formData: {
        quiz_name: "",
        chapter_id: "",
        date_of_quiz: "",
        time_duration: "",
      },
      chapters: [], // ← holds chapter id & name
    };
  },
  methods: {
    async handleSubmit() {
      try {
        const response = await fetch("/api/newquiz", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.formData),
        });

        if (response.ok) {
          this.$router.push("/quiz");
        } else {
          const error = await response.json();
          alert("Failed to create quiz: " + (error.message || "Unknown error"));
        }
      } catch (error) {
        alert("Error: " + error.message);
      }
    },
  },
  mounted() {
    // Fetch chapter list for dropdown
    fetch("/api/chapters")
      .then((res) => res.json())
      .then((data) => {
        this.chapters = data;
      })
      .catch((err) => {
        console.error("Failed to load chapters", err);
      });
  },
};

</script>

<style scoped>
.new-quiz-container {
  font-family: 'Roboto', sans-serif;
  background-color: #f4f4f4;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
  padding: 20px;
}

.form-container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.form-container h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #ff8c42;
  margin-bottom: 30px;
  letter-spacing: 2px;
  text-transform: capitalize;
}

.input-group {
  margin-bottom: 25px;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.input-group input,
.input-group select {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 16px;
  transition: all 0.3s;
}

.input-group input:focus,
.input-group select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
  outline: none;
}

.input-group input[type="date"] {
  appearance: none;
  background-color: white;
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 30px;
}

.primary-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
  flex: 1;
}

.primary-btn:hover {
  background-color: #0069d9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.secondary-btn {
  padding: 8px 16px;
  background-color: white;
  color: #dc3545;
  border: 2px solid #dc3545;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s;
  text-decoration: none;
  text-align: center;
  flex: 1;
}

.secondary-btn:hover {
  background-color: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 480px) {
  .form-container {
    padding: 20px;
  }
  
  .form-container h2 {
    font-size: 28px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .input-group input {
    padding: 10px 12px;
  }
}
</style>