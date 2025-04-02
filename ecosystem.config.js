module.exports = {
    apps: [{
      name: "iyc-scheduler-api-6000",
      script: "venv/bin/python",  // Path to your virtual env Python
      args: "main.py",            // Your FastAPI main script
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production",
        PORT: "6000"              // Matches the port in your main.py
      }
    }]
  };