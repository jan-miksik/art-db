module.exports = {
  env: {
      browser: true,
      es2021: true,
  }     ,
  extends: [
      "@nuxtjs/eslint-config-typescript",
      "plugin:prettier/recommended"
  ],
  overrides: [],
  parser: "vue-eslint-parser",
  parserOptions: {
      parser: "@typescript-eslint/parser",
      ecmaVersion: "latest",
      sourceType: "module",
  },
  plugins: ["vue", "@typescript-eslint"],
  rules: {
  "vue/multi-word-component-names": 0,
  },
};