<template>
  <div class="new-subject-container">
    <div class="form-container">
      <h2>New Subject</h2>
      <form @submit.prevent="handleSubmit">
        <!-- Subject Name Field -->
        <div class="input-group">
          <label for="subject-name">Subject Name:</label>
          <input
            type="text"
            id="subject-name"
            v-model="formData.name"
            placeholder="Enter subject name"
            required
            @input="validateName"
          >
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>

        <!-- Description Field -->
        <div class="input-group">
          <label for="subject-description">Description:</label>
          <textarea
            id="subject-description"
            v-model="formData.description"
            placeholder="Enter subject description"
            rows="4"
          ></textarea>
        </div>

        <div class="button-group">
          <button type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Save' }}
          </button>
          <button type="button" @click="handleCancel">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NewSubject',
  data() {
    return {
      formData: {
        name: '',
        description: ''
      },
      errors: {
        name: ''
      },
      isSubmitting: false
    }
  },
  methods: {
    validateName() {
      if (this.formData.name.length < 3) {
        this.errors.name = 'Subject name must be at least 3 characters';
        return false;
      }
      this.errors.name = '';
      return true;
    },
    async handleSubmit() {
      if (!this.validateName()) return;
      
      this.isSubmitting = true;
      
      try {
        await axios.post('/api/subjects', this.formData);
        
        this.$router.push('/admin-dashboard');
        this.$toast.success('Subject created successfully!'); // If using toast notifications
      } catch (error) {
        console.error('Error creating subject:', error);
        this.$toast.error('Failed to create subject. Please try again.');
      } finally {
        this.isSubmitting = false;
      }
    },
    handleCancel() {
      this.$router.push('/admin-dashboard');
    }
  }
  // If using Vuex
  // methods: mapActions(['createSubject'])
}
</script>

<style scoped>
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
  min-height: 100px;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.button-group button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  transition: all 0.3s;
  flex: 1;
}

.button-group button[type="submit"] {
  background-color: #007bff;
  color: white;
}

.button-group button[type="submit"]:hover {
  background-color: #0069d9;
}

.button-group button[type="submit"]:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.button-group button[type="button"] {
  background-color: white;
  color: #dc3545;
  border: 2px solid #dc3545;
}

.button-group button[type="button"]:hover {
  background-color: #f8f9fa;
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
}
</style>