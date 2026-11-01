import './App.css';
import { useState } from 'react';
import LoginForm from './components/login';

const App = () => {
  const adminUser = {
    email: 'admin@admin.com',
    password: 'admin',
  };

  const [user, setUser] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [error, setError] = useState('');

  const Login = (details) => {
    if (
      details.email === adminUser.email &&
      details.password === adminUser.password
    ) {
      setUser({ ...details });
      setError('');
    } else {
      setError('Invalid email or password');
    }
  };

  const Logout = () => {
    setUser({
      name: '',
      email: '',
      password: '',
    });
  };

  return (
    <div>
      {
        <LoginForm handleLogin={Login} />
      }
    </div>
  );
};

export default App;
