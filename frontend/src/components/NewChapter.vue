<template>
<div class="new-subject-container">
  <div class="form-container">
    <h2>New Chapter</h2>
    <form @submit.prevent="submitForm">
      <div class="input-group">
        <label for="chapter-id">Chapter ID:</label>
        <input
          type="number"
          id="chapter-id"
          v-model.number="chapter_id"
          placeholder="Enter Chapter ID"
          required
          min="1"
        />
      </div>

      <div class="input-group">
        <label for="subject-id">Subject ID:</label>
        <input
          type="number"
          id="subject-id"
          v-model.number="subject_id"
          placeholder="Enter Subject ID"
          required
        />
      </div>

      <div class="input-group">
        <label for="chapter-name">Name:</label>
        <input
          type="text"
          id="chapter-name"
          v-model="chapter_name"
          placeholder="Enter chapter name"
          required
        />
      </div>

      <div class="input-group">
        <label for="chapter-description">Description:</label>
        <textarea
          id="chapter-description"
          v-model="chapter_description"
          placeholder="Enter chapter description"
        ></textarea>
      </div>

      <div class="button-group">
        <button type="submit">Save</button>
        <router-link to="/admin-dashboard">
          <button type="button">Cancel</button>
        </router-link>
      </div>
    </form>
  </div>
</div>
</template>

<script>
export default {
  name: "NewChapter",
  data() {
  return {
    chapter_id: "",
    subject_id: "",  // initialized as empty
    chapter_name: "",
    chapter_description: "",
  };
},
created() {
  this.subject_id = this.$route.params.subject_id || "";
  },
  methods: {
    submitForm() {
      const payload = {
        chapter_id: this.chapter_id,
        subject_id: this.subject_id,
        chapter_name: this.chapter_name,
        chapter_description: this.chapter_description,
      };

      fetch(`/api/new-chapter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
        .then((res) => {
          if (res.ok) {
            this.$router.push("/admin-dashboard");
          } else {
            alert("Failed to save chapter.");
          }
        })
        .catch(() => alert("An error occurred while saving."));
    },
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Bangers&display=swap");

body {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
}

.form-container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.form-container h2 {
  font-family: 'Bangers', cursive;
  font-size: 36px;
  color: #ff8c42;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-transform: capitalize;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.input-group input,
.input-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-group input:focus,
.input-group textarea:focus {
  border-color: #007bff;
  outline: none;
}
.input-group textarea {
  resize: vertical;
  height: 100px;
}
.new-subject-container {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
  padding: 20px;
}
.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.button-group button {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.button-group button[type="submit"] {
  background-color: #007bff;
  color: white;
}

.button-group button[type="button"] {
  background-color: white;
  color: #ff0000;
  border: 2px solid #ff0000;
}

.button-group button:hover {
  opacity: 0.9;
}

.note {
  color: red;
  font-size: 12px;
  margin-top: 5px;
  text-align: left;
}
</style>
