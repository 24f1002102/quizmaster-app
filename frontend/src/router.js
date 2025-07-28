import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/components/Login.vue'
import Register from '@/components/Register.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import Quiz from '@/components/Quiz.vue'
import Summary from '@/components/Summary.vue' 
import NewSubject from '@/components/NewSubject.vue'
import NewChapter from '@/components/NewChapter.vue'
import EditChapter from './components/EditChapter.vue';
import EditQuestion from './components/EditQuestion.vue';
import NewQuiz from '@/components/NewQuiz.vue';
import NewQuestion from './components/NewQuestion.vue';
// ✅ Make sure this file exists

import UserDashboard from '@/components/UserDashboard.vue';
import ViewQuiz from '@/components/ViewQuiz.vue';
import Scores from '@/components/Scores.vue';
import SummaryUser from '@/components/SummaryUser.vue';
import StartQuiz from './components/StartQuiz.vue';



const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/admin-dashboard', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/quiz', name: 'Quiz', component: Quiz },
  { path: '/summary', name: 'Summary', component: Summary },
  { path: '/new-subject', name: 'NewSubject', component: NewSubject },
  { path: '/new-chapter/:subject_id', name: 'NewChapter', component: NewChapter },
  { path: '/edit-chapter/:chapter_id', name: 'EditChapter', component: EditChapter, props: true },
  { path: '/newquiz', name: 'NewQuiz', component: NewQuiz},
  { path: '/newquestion', name: 'NewQuestion', component: NewQuestion },
  { path: '/edit-question/:question_id', name: 'EditQuestion', component: EditQuestion},
 // ✅ THIS LINE ADDED
  // Add other admin routes here

  { path: '/user-dashboard', name: 'UserDashboard', component: UserDashboard },
  { path: '/viewquiz/:quiz_id', name: 'ViewQuiz', component: ViewQuiz },
  { path: '/scores', name: 'Scores', component: Scores },
  { path: '/summaryuser', name: 'SummaryUser', component: SummaryUser },
  { path: '/startquiz/:id', name: 'StartQuiz', component: StartQuiz },

  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard: check login status on each route
router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  const loggedIn = localStorage.getItem('loggedIn')

  if (authRequired && !loggedIn) {
    return next('/login')
  }

  if ((to.path === '/login' || to.path === '/register') && loggedIn) {
    return next('/admin-dashboard')
  }

  next()
})

export default router
