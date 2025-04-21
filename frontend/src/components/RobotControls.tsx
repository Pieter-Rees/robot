import { useState, useEffect } from 'react'
import { 
  Box, 
  Button, 
  Grid, 
  Slider, 
  Typography,
  Card,
  CardContent
} from '@mui/material'
import axios from 'axios'

interface ServoInfo {
  position: number
  min: number
  max: number
}

export default function RobotControls() {
  const [servos, setServos] = useState<Record<number, ServoInfo>>({})
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    fetchRobotInfo()
  }, [])

  const fetchRobotInfo = async () => {
    try {
      const response = await axios.get('/api/robot_info')
      if (response.data.status === 'success') {
        setServos(response.data.servos)
        setInitialized(response.data.initialized)
      }
    } catch (error) {
      console.error('Error fetching robot info:', error)
    }
  }

  const handleServoChange = async (servoIndex: number, value: number) => {
    try {
      await axios.post('/api/servo', {
        servo: servoIndex,
        angle: value,
        speed: 0.01
      })
      setServos(prev => ({
        ...prev,
        [servoIndex]: { ...prev[servoIndex], position: value }
      }))
    } catch (error) {
      console.error('Error moving servo:', error)
    }
  }

  const handleAction = async (action: string) => {
    try {
      await axios.post(`/api/${action}`)
      if (action === 'init') {
        setInitialized(true)
      } else if (action === 'shutdown') {
        setInitialized(false)
      }
    } catch (error) {
      console.error(`Error performing ${action}:`, error)
    }
  }

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Robot Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => handleAction('init')}
                  disabled={initialized}
                >
                  Initialize Robot
                </Button>
                <Button 
                  variant="contained" 
                  color="secondary"
                  onClick={() => handleAction('shutdown')}
                  disabled={!initialized}
                >
                  Shutdown Robot
                </Button>
                <Button 
                  variant="contained" 
                  onClick={() => handleAction('stand')}
                  disabled={!initialized}
                >
                  Stand Up
                </Button>
                <Button 
                  variant="contained" 
                  onClick={() => handleAction('walk')}
                  disabled={!initialized}
                >
                  Walk
                </Button>
                <Button 
                  variant="contained" 
                  onClick={() => handleAction('dance')}
                  disabled={!initialized}
                >
                  Dance
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {Object.entries(servos).map(([index, info]) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Servo {index}
                </Typography>
                <Slider
                  value={info.position}
                  min={info.min}
                  max={info.max}
                  onChange={(_, value) => handleServoChange(Number(index), value as number)}
                  disabled={!initialized}
                  valueLabelDisplay="auto"
                />
                <Typography variant="body2" color="text.secondary">
                  Position: {info.position}°
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
} 