// Simple Playwright MCP (Model Context Protocol) Server
const net = require('net');

const port = process.env.PLAYWRIGHT_SERVER_PORT || 8931;
const host = '0.0.0.0';

console.log(`Playwright MCP Server starting on ${host}:${port}`);

const server = net.createServer((socket) => {
  console.log(`Client connected from ${socket.remoteAddress}:${socket.remotePort}`);

  socket.write('Playwright MCP Server\r\n');

  let buffer = '';

  socket.on('data', async (data) => {
    buffer += data.toString();

    // Process complete lines
    const lines = buffer.split('\r\n');
    buffer = lines.pop(); // Keep last incomplete line in buffer

    for (const line of lines) {
      if (!line.trim()) continue;

      console.log(`Received command: ${line}`);

      try {
        // Parse command - simple protocol
        const parts = line.split(' ');
        const command = parts[0].toLowerCase();

        let response = '';

        switch(command) {
          case 'hello':
            response = 'hello\r\n';
            break;

          case 'ping':
            response = 'pong\r\n';
            break;

          default:
            response = `error unknown_command: ${command}\r\n`;
            break;
        }

        socket.write(response);
      } catch (error) {
        console.error(`Error processing command: ${error.message}`);
        socket.write(`error ${error.message}\r\n`);
      }
    }
  });

  socket.on('error', (err) => {
    console.error(`Socket error: ${err.message}`);
  });

  socket.on('close', () => {
    console.log(`Client disconnected from ${socket.remoteAddress}:${socket.remotePort}`);
  });
});

server.on('error', (err) => {
  console.error(`Server error: ${err.message}`);
});

server.listen(port, host, () => {
  console.log(`Playwright MCP Server listening on ${host}:${port}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down Playwright MCP Server...');
  server.close(() => {
    console.log('Playwright MCP Server shut down.');
    process.exit(0);
  });
});