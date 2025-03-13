module.exports = {
  content: ["**/*.{js,jsx,ts,tsx}"]  // Now looks inside src/
  ,  // ✅ Ensures Tailwind scans your React files
  theme: {
    extend: {},  // You can customize this later
  },
  plugins: [],
};
