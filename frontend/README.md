# Robot Frontend

This is the frontend application for controlling the robot. It's built with React, TypeScript, and Material-UI.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Project Structure

- `src/` - Source code
  - `components/` - Reusable React components
  - `pages/` - Page components
  - `hooks/` - Custom React hooks
  - `utils/` - Utility functions
  - `types/` - TypeScript type definitions
- `public/` - Static assets

## Development

The development server runs on port 3000 by default. The application is configured to proxy API requests to the backend server running on port 5000.

## Testing

Run the test suite:
```bash
npm test
```

## Linting

Run the linter:
```bash
npm run lint
``` 