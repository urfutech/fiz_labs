import './App.css';
import { useState } from 'react';
import LoginForm from './components/login';
import Home from './components/home';
import axios from 'axios';

const API_BASE = "http://localhost:8000";  

const App = () => {

  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  const Login = async (details) => {
    if (!details.fullname || !details.email || !details.password || !details.group || !details.teacher) {
      setError('Заполните все поля');
      return;
    }
    if (details.password !== details.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    const cleanFIO = details.fullname.trim().replace(/\s+/g, ' ');
    const parts = cleanFIO.split(' ');
    const lastName = parts[0]
    const firstName = parts[1]
    const middleName = parts[2]
    const post = {
      lastname,
      firstName,
      middleName,
      group: details.group,
      teacher: details.teacher,
      email: details.email,
      password: details.password
    };
    try {
      const response = await axios.post(`${API_BASE}/items/`, {   //посмотрите пожалуйста куда я это вообще кидаю в какой файл поправьте там, apibase на строчке 7
        post
      });
    } catch (error) {
      console.error("Ошибка добавления:", error);
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
