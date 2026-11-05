import './App.css';
import { useState } from 'react';
import LoginForm from './components/login';
import Home from './components/home';

const App = () => {

  const [user, setUser] = useState(null); 
  const [error, setError] = useState('');

  const Login = (details) => {
    if (!details.fullname || !details.email || !details.password || !details.group || !details.teacher) {
      setError('Заполните все поля');
      return;
    }
    if (details.password !== details.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    setUser(details); 
    setError('');
  };

  const Logout = () => {
    setUser(null);
    setError('');
  };

  return (
    <div>
      {user ? (
        <Home name={user.fullname} group={user.group} teacher={user.teacher} onLogout={Logout} />
      ) : (
        <LoginForm handleLogin={Login} error={error} />
      )}
    </div>
  );
};

export default App;
