import React from 'react'
import './App.css'
import PriceTrend from './components/PriceTrend'

function App() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">不動産検索</h1>
      <div className="grid gap-6">
        <PriceTrend />
      </div>
    </div>
  )
}

export default App
