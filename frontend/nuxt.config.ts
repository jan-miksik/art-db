// https://nuxt.com/docs/api/configuration/nuxt-config

// SEO constants
const SEO_TITLE = 'Art-db - Contemporary Artists & Artworks Database'
const SEO_DESCRIPTION = 'Browse contemporary artists and artworks. Explore an interactive database with decentralized image storage, and filtering'

export default defineNuxtConfig({
  devtools: { enabled: true },

  // Keep current directory structure (don't move to app/)
  srcDir: '.',

  runtimeConfig: {
    public: {
      DJANGO_SERVER_URL: process.env.DJANGO_SERVER_URL
    }
  },

  modules: ["@pinia/nuxt", "nuxt-swiper"],

  pinia: {
    storesDirs: ['./J/**'],
  },

  compatibilityDate: "2025-01-15",

  app: {
    head: {
      title: SEO_TITLE,
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { 
          name: 'description', 
          content: SEO_DESCRIPTION
        },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'robots', content: 'index, follow' },
        // Open Graph
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: SEO_TITLE },
        { 
          property: 'og:description', 
          content: SEO_DESCRIPTION
        },
        // Twitter Card
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: SEO_TITLE },
        { 
          name: 'twitter:description', 
          content: SEO_DESCRIPTION
        },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})