<template>
  <div class="container">
    <h1 v-if="chapter.name">{{ chapter.name }}</h1>
    <h1 v-else style="color: red;">Chapter Title Not Found!</h1>

    <p>{{ chapter.description }}</p>

    <router-link :to="`/startquiz/chapter/${chapter.id}`" class="start-quiz-button">
      Start Quiz
    </router-link>
  </div>
</template>

<script>
export default {
  name: "ViewChapter",
  props: {
    chapter: {
      type: Object,
      required: true,
      // Should contain: id, name, description
    },
  },
};
</script>

<style scoped>
/* General Styles */
body {
  font-family: 'Poppins', sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f4f4f9;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* Container Styles */
.container {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
  text-align: center;
}

/* Title */
h1 {
  color: red;
  font-size: 24px;
}

/* Description Styles */
p {
  font-size: 16px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 30px;
}

/* Button Styles */
.start-quiz-button {
  background-color: #007bff;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.start-quiz-button:hover {
  background-color: #0056b3;
}

/* Responsive Design */
@media (max-width: 600px) {
  h1 {
    font-size: 24px;
  }
  p {
    font-size: 14px;
  }
  .start-quiz-button {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
