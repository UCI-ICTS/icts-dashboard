module.exports = {
    transform: {
      "^.+\\.(js|jsx)$": "babel-jest", // ✅ Ensures Jest transforms ES Modules
    },
    transformIgnorePatterns: [
      "/node_modules/(?!axios)/", // ✅ Allows Jest to process Axios
    ],
    setupFilesAfterEnv: ["<rootDir>/src/setupTests.js"],
    testEnvironment: "jsdom",
    moduleNameMapper: {
      "^axios$": require.resolve("axios"), // ✅ Ensures Jest loads Axios correctly
    },
  };
  