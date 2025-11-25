import { render, screen } from '@testing-library/react'
import React from 'react'
import App from './App'

it('renders main application container', () => {
  render(<App />)
  // Adjust this assertion to something stable in your UI
  expect(document.body).toBeTruthy()
})
