// use to spawn a local instance of the FastAPI backend
const { spawn } = require('child_process');

const backendProcess = spawn('uvicorn', ['app.main:app', '--host', '0.0.0.0', '--port', '8000']);

backendProcess.stdout.on('data', (data) => {
  console.log(data.toString());
});

backendProcess.stderr.on('data', (data) => {
  console.error(data.toString());
});

