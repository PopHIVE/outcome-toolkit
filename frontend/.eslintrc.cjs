module.exports = {
  root: true,
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
    "@vue/eslint-config-typescript",
    "@vue/eslint-config-prettier",
  ],
  parserOptions: {
    ecmaVersion: "latest",
  },
  rules: {
    "vue/attribute-hyphenation": "off",
    "vue/attributes-order": "off",
    // ACF 15 Aug flag use of alert, console.debug, etc. (allow 'warn', 'error')
    "no-alert": "error",
    "no-console": ["warn", { allow: ["warn", "error"] }],
  },
};
