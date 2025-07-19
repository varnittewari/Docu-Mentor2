import Dashboard from './Dashboard';

function App() {
  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <header className="bg-white shadow-sm">
        <nav className="container mx-auto px-6 py-4">
          <h1 className="text-xl font-semibold text-gray-800">Docu-Mentor</h1>
        </nav>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  )
}

export default App
