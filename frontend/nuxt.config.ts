// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      DJANGO_SERVER_URL: process.env.DJANGO_SERVER_URL
    }
  },

  modules: ["@pinia/nuxt", "nuxt-swiper"],

  pinia: {
    storesDirs: ['./J/**', ],
  },

  compatibilityDate: "2024-10-04",
})