import { Box, Container, Typography } from '@mui/material'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Robot Control Panel
        </Typography>
        {children}
      </Box>
    </Container>
  )
} 