# Outcome Toolkit Front End development

Outcome Toolkit is a VueJS v3 codebase, written in TypeScript. We use eslint with an expanded rule set; see below for making sure it's set up on your machine.

If you are on Windows, use of WSL is highly recommended. In any case, you'll need `docker` and `docker-compose` installed.

## Required IDE Setup

- [VSCode](https://code.visualstudio.com/)

Required extensions:

- [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) plugin from Volar. Disable any other Vue plugins you had installed (e.g. Vetur) that were for Vue2.
- [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) - Code MUST be formatted with Prettier before being pushed.
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) - Code MUST NOT have any lint errors when pushed to `main`.
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) - Code SHOULD not have misspellings in it.
  * This includes variable names, etc.
  * Use `theURLStyle` names where internal acronyms are all capitalized.
  * Custom words can be added to the project dictionary (many are already there, like "NEMSIS").
- [Todo Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree) - Highly recommended for keeping track of TODOs in the code base. Custom configuration exists in the project VSCode config directory (see below).

Recommended:

- [markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) - For editing files like this one.
- [Playwright Test for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright) - Simplifies test development.
- [Thunder Client](https://marketplace.visualstudio.com/items?itemName=rangav.vscode-thunder-client) - Free alternative to Postman. Helps diagnose API calls.

There is a `frontend/.vscode/` directory with a custom configuration in it, setting up many details of the above plugins.

### Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [TypeScript Vue Plugin (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin) to make the TypeScript language service aware of `.vue` types.

## Project Setup

```zsh
cd frontend/
npm install
```

### Compile and Hot-Reload for Development

Run a hot-reload for quick local development.

```zsh
npm run dev
```

Otherwise, you should be using the `start.sh` script from the parent directory.

### Type-Check, Compile and Minify for Production

Build is also more stringent than `npm run dev`, so use it when making invasive changes.

```sh
npm run build
```

## Testing

All new features should have a matching e2e test that exercises them. We are still catching up on this.

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Playwright](https://playwright.dev)

```sh
# Install browsers for the first run. Only need to do this once.
npx playwright install

# When testing on CI, must build the project first
npm run build

# Runs the end-to-end tests
npm run test:e2e
# Runs the tests only on Chromium
npm run test:e2e -- --project=chromium
# Runs the tests of a specific file
npm run test:e2e -- tests/example.spec.ts
# Runs the tests in debug mode
npm run test:e2e -- --debug
```

### Manual Lint with [ESLint](https://eslint.org/)

Linting should happen automatically as you write and edit code, courtesy of the ESLint plugin in your IDE.

You can also run the lint checks manually via:
`npm run lint`.

It is recommended to make lint checks a pre-push hook, so that you do not accidentally push code with lint failures in it. Create a file in `~/.git/hooks` which runs the above; if it fails, it will prevent pushing, to remind you to fix such errors.
