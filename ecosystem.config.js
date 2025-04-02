module.exports = {
    apps: [{
      name: "iyc-scheduler-api-6000",
      script: "/home/microservices/iyc-scheduler/venv/bin/python",  // Path to virtual env Python
      args: "main.py",
      cwd: "/home/microservices/iyc-scheduler", // working directory
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