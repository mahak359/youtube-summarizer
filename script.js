document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for user's preferred theme in localStorage or system preference
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply initial theme
    if (storedTheme === 'dark' || (storedTheme === null && prefersDark)) {
        body.classList.add('dark-mode');
        themeToggle.querySelector('.icon').textContent = '🌙';
    } else {
        body.classList.remove('dark-mode');
        themeToggle.querySelector('.icon').textContent = '💡';
    }

    // Toggle theme on button click
    themeToggle.addEventListener('click', () => {
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            themeToggle.querySelector('.icon').textContent = '💡';
        } else {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            themeToggle.querySelector('.icon').textContent = '🌙';
        }
    });
});