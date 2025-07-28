<template>
  <div class="quiz-container" v-if="quiz">
    <!-- Quiz Header -->
    <div class="quiz-header">
      <div>
        <h1 class="quiz-title">{{ quiz.quiz_name }}</h1>
        <p class="quiz-subject">{{ quiz.subject }} - {{ quiz.chapter_name }}</p>
      </div>
      <div class="timer-container">
        <span class="timer-label">Time Left:</span>
        <div class="timer" :class="{ 'time-warning': remainingTime <= 30 }">
          {{ formattedTime }}
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress-container">
      <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
    </div>

    <!-- Question Display -->
    <div class="question-display-area">
      <div class="question-counter">
        Question {{ currentQuestionIndex + 1 }} of {{ quiz.num_questions }}
      </div>
      
      <div class="question-container" v-if="currentQuestion">
        <div class="question-text">{{ currentQuestion.question_statement }}</div>
        
        <div class="options-container">
          <div 
            v-for="(option, index) in currentQuestionOptions" 
            :key="index"
            class="option"
            :class="{ selected: userAnswers[currentQuestion.id] === index + 1 }"
            @click="selectOption(index + 1)"
          >
            <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
            <span class="option-text">{{ option }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="navigation-buttons">
      <button 
        class="btn btn-primary" 
        @click="prevQuestion"
        :disabled="currentQuestionIndex === 0"
      >
        Previous
      </button>
      
      <button 
        class="btn btn-warning" 
        @click="showCancelModal = true"
        v-if="currentQuestionIndex < quiz.num_questions - 1"
      >
        Cancel Quiz
      </button>
      
      <button 
        class="btn btn-primary" 
        @click="nextQuestion"
        v-if="currentQuestionIndex < quiz.num_questions - 1"
      >
        Next
      </button>
      
      <button 
        class="btn btn-danger" 
        @click="submitQuiz"
        v-else
      >
        Submit Quiz
      </button>
    </div>

    <!-- Warning Message -->
    <div class="warning-message">
      <i class="fas fa-exclamation-triangle"></i> Don't refresh or leave this page during the quiz!
    </div>

    <!-- Cancel Confirmation Modal -->
    <div class="modal-overlay" v-if="showCancelModal" @click.self="showCancelModal = false">
      <div class="modal-content">
        <h3 class="modal-title">Confirm Quiz Cancellation</h3>
        <p class="modal-message">
          Are you sure you want to cancel this quiz? All your progress will be lost.
        </p>
        <div class="modal-buttons">
          <button class="btn btn-primary" @click="showCancelModal = false">
            Continue Quiz
          </button>
          <button class="btn btn-danger" @click="cancelQuiz">
            Cancel Quiz
          </button>
        </div>
      </div>
    </div>

    <!-- Loading Spinner -->
    <div class="spinner" v-if="submitting">
      <div class="spinner-content">
        <div class="spinner-icon"></div>
        <h3>Submitting Quiz...</h3>
        <p>Please wait while we process your results</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

const quiz = ref(null);
const questions = ref([]);
const currentQuestionIndex = ref(0);
const remainingTime = ref(0);
const userAnswers = ref({});
const submitting = ref(false);
const showCancelModal = ref(false);
const timerInterval = ref(null);
const loading = ref(true);
const error = ref(null);

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value]);

const currentQuestionOptions = computed(() => {
  if (!currentQuestion.value) return [];
  return [
    currentQuestion.value.option1,
    currentQuestion.value.option2,
    currentQuestion.value.option3,
    currentQuestion.value.option4
  ].filter(opt => opt !== undefined && opt !== null);
});

const formattedTime = computed(() => {
  const minutes = Math.floor(remainingTime.value / 60);
  const seconds = remainingTime.value % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
});

const progressPercent = computed(() => {
  if (!quiz.value) return 0;
  return (remainingTime.value / (quiz.value.time_duration * 60)) * 100;
});

const startTimer = () => {
  timerInterval.value = setInterval(() => {
    if (remainingTime.value <= 0) {
      clearInterval(timerInterval.value);
      submitQuiz();
    } else {
      remainingTime.value--;
    }
  }, 1000);
};

const fetchQuiz = async () => {
  const quizId = route.params.id;
  try {
    const response = await axios.get(`/api/startquiz/${quizId}`, { withCredentials: true });

    quiz.value = response.data.quiz;
    questions.value = response.data.questions;

    remainingTime.value = quiz.value.time_duration * 60;
    loading.value = false;
    startTimer();
  } catch (err) {
    error.value = 'Failed to load quiz.';
    console.error(err);
    loading.value = false;
  }
};

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
};

const nextQuestion = () => {
  if (currentQuestionIndex.value < quiz.value.num_questions - 1) {
    currentQuestionIndex.value++;
  }
};

const selectOption = (optionNumber) => {
  userAnswers.value[currentQuestion.value.id] = optionNumber;
};

const calculateScore = () => {
  let score = 0;
  questions.value.forEach(question => {
    if (userAnswers.value[question.id] === question.correct_option) {
      score++;
    }
  });
  return score;
};

const submitQuiz = async () => {
  submitting.value = true;
  clearInterval(timerInterval.value);

  try {
    const score = calculateScore();

    await axios.post('/api/submit-quiz', {
      quiz_id: quiz.value.id,
      score: score,
      answers: userAnswers.value  // optional, for future use
    }, { withCredentials: true });

    setTimeout(() => {
      router.push(`/user-dashboard`);
    }, 1500);
  } catch (error) {
    console.error('Error submitting quiz:', error);
    submitting.value = false;
  }
};

const cancelQuiz = () => {
  router.push('/user-dashboard');
};

onMounted(() => {
  fetchQuiz();
});

onBeforeUnmount(() => {
  if (timerInterval.value) {
    clearInterval(timerInterval.value);
  }
});
</script>




<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.quiz-title {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 5px;
}

.quiz-subject {
  color: #7f8c8d;
  font-size: 14px;
}

.timer-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.timer-label {
  font-size: 14px;
  color: #7f8c8d;
}

.timer {
  font-weight: bold;
  padding: 8px 16px;
  border-radius: 20px;
  background: #f0f8ff;
  color: #3a86ff;
  font-size: 16px;
  min-width: 80px;
  text-align: center;
}

.timer.time-warning {
  background: #ffebee;
  color: #e74c3c;
}

.progress-container {
  height: 8px;
  background-color: #f1f1f1;
  border-radius: 4px;
  margin-bottom: 25px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #3a86ff;
  transition: width 0.3s ease;
}

.question-display-area {
  margin-bottom: 30px;
}

.question-counter {
  text-align: center;
  color: #7f8c8d;
  margin-bottom: 20px;
  font-weight: 500;
}

.question-text {
  font-size: 18px;
  line-height: 1.5;
  margin-bottom: 25px;
  color: #2c3e50;
}

.options-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.option {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f9f9f9;
}

.option:hover {
  background-color: #f1f1f1;
}

.option.selected {
  background-color: #3a86ff;
  color: white;
  border-color: #2980b9;
}

.option-letter {
  font-weight: bold;
  margin-right: 12px;
}

.option.selected .option-letter {
  color: white;
}

.navigation-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}

.btn-primary {
  background-color: #3a86ff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2667cc;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-warning {
  background-color: #f39c12;
  color: white;
}

.btn-warning:hover {
  background-color: #d35400;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.warning-message {
  text-align: center;
  color: #e74c3c;
  margin-top: 25px;
  padding: 12px;
  background-color: #ffebee;
  border-radius: 6px;
  font-size: 14px;
}

.warning-message i {
  margin-right: 8px;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 10px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.modal-title {
  font-size: 20px;
  margin-bottom: 15px;
  color: #2c3e50;
}

.modal-message {
  margin-bottom: 20px;
  color: #7f8c8d;
  line-height: 1.5;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Loading spinner */
.spinner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.spinner-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.spinner-icon {
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3a86ff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive styles */
@media (max-width: 768px) {
  .quiz-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .timer-container {
    align-self: flex-end;
  }
  
  .navigation-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>