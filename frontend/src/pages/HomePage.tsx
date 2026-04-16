import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="max-w-2xl mx-auto text-center px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Performance Test App
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          A full-stack application built with FastAPI and React.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/login"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="px-6 py-3 bg-white text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
          >
            Register
          </Link>
          <Link
            to="/items"
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Browse Items
          </Link>
        </div>
      </div>
    </div>
  );
}