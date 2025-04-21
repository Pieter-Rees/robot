import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { createTheme } from '@mui/material/styles'
import Layout from './components/Layout'
import RobotControls from './components/RobotControls'

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={
          <Layout>
            <RobotControls />
          </Layout>
        } />
      </Routes>
    </ThemeProvider>
  )
}

export default App 