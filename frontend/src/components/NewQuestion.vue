<template>
  <div class="new-question-container">
    <div class="form-container">
      <h2>Add New Question</h2>
      <form @submit.prevent="submitForm">
        <input type="hidden" v-model="form.quiz_id" />
        <input type="hidden" v-model="form.chapter_id" />

        <div class="input-group">
          <label for="question-title">Question Title:</label>
          <input
            type="text"
            id="question-title"
            v-model="form.question_title"
            required
            placeholder="Enter question title"
          />
        </div>

        <div class="input-group">
          <label for="question-statement">Question Statement:</label>
          <textarea
            id="question-statement"
            v-model="form.question_statement"
            required
            placeholder="Enter the full question text"
          ></textarea>
        </div>

        <div class="input-group">
          <label for="option1">Option 1:</label>
          <input
            type="text"
            id="option1"
            v-model="form.option1"
            required
            placeholder="First answer option"
          />
        </div>

        <div class="input-group">
          <label for="option2">Option 2:</label>
          <input
            type="text"
            id="option2"
            v-model="form.option2"
            required
            placeholder="Second answer option"
          />
        </div>

        <div class="input-group">
          <label for="option3">Option 3:</label>
          <input
            type="text"
            id="option3"
            v-model="form.option3"
            required
            placeholder="Third answer option"
          />
        </div>

        <div class="input-group">
          <label for="option4">Option 4:</label>
          <input
            type="text"
            id="option4"
            v-model="form.option4"
            required
            placeholder="Fourth answer option"
          />
        </div>

        <div class="input-group">
          <label for="correct_answer">Correct Answer (1-4):</label>
          <input
            type="number"
            id="correct_answer"
            v-model="form.correct_answer"
            required
            min="1"
            max="4"
          />
        </div>

        <div class="button-group">
          <button type="submit" class="primary-btn">
            Save Question
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
  name: "NewQuestion",
  data() {
    return {
      form: {
        quiz_id: "",
        chapter_id: "",
        question_title: "",
        question_statement: "",
        option1: "",
        option2: "",
        option3: "",
        option4: "",
        correct_answer: "",
      },
    };
  },
  async created() {
  const quizId = this.$route.query.quiz_id;
  this.form.quiz_id = quizId;

  try {
    const response = await fetch(`/api/newquestion/${quizId}`);
    if (!response.ok) throw new Error("Failed to fetch quiz details");

    const data = await response.json();
    this.form.chapter_id = data.chapter_id;
  } catch (error) {
    alert("Failed to fetch quiz details: " + error.message);
  }
},
  methods: {
    async submitForm() {
      try {
        const response = await fetch(`/api/newquestion/${this.form.quiz_id}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.form),
        });

        if (response.ok) {
          this.$router.push("/quiz");
        } else {
          const error = await response.json();
          alert("Failed to add question: " + (error.message || "Unknown error"));
        }
      } catch (error) {
        alert("Error: " + error.message);
      }
    },
  },
};
</script>


<style scoped>
.new-question-container {
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
  max-width: 600px;
  text-align: center;
}

.form-container h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #ff8c42;
  margin-bottom: 8px;
  letter-spacing: 2px;
  text-transform: capitalize;
}

.input-group {
  margin-bottom: 15px;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #000000;
  font-size: 16px;
}

.input-group input,
.input-group select,
.input-group textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 2x;
  box-sizing: border-box;
  font-size: 16px;
  transition: all 0.3s;
  resize: vertical;
  min-height: 1px;
}

.input-group input:focus,
.input-group select:focus,
.input-group textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
  outline: none;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.primary-btn {
  padding: 12px 25px;
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
  padding: 12px 25px;
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

  .input-group input,
  .input-group textarea {
    padding: 10px 12px;
  }
}
</style>
