import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Header() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // Logout errors are non-critical
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-primary-600">
          Performance Test App
        </Link>
        <nav className="flex items-center gap-4">
          <Link to="/items" className="text-gray-600 hover:text-gray-900 text-sm">
            Items
          </Link>
          {user ? (
            <>
              <Link to="/profile" className="text-gray-600 hover:text-gray-900 text-sm">
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-600 hover:text-gray-900 text-sm">
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-3 py-1.5 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm transition-colors"
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}