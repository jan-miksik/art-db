// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      DJANGO_SERVER_URL: process.env.DJANGO_SERVER_URL
    }
  },
  modules: ["@pinia/nuxt"],
  pinia: {
    storesDirs: ['./J/**', ],
  },
})
