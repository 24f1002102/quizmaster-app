<template>
  <router-view />
</template>

<script>
export default {
  name: 'App',
  mounted() {
    window.onpageshow = function (event) {
      if (event.persisted) {
        window.location.reload()
      }
    }
  }
}
</script>

<style>
body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  margin: 0;
  background-color: #f4f4f4;
}
</style>
