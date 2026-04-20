/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  env: {
    browser: true,
    node: true,
    es2022: true,
  },
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/consistent-type-imports': 'error',
  },
  ignorePatterns: ['dist', 'node_modules', 'coverage'],
}
