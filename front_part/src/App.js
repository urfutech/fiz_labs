import './App.css';
import { useState } from 'react';
import LoginForm from './components/login';
import Home from './components/home';
import Lab1 from './components/lab_1';
import axios from 'axios';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const API_BASE = "http://localhost:8000";  

const App = () => {


  return (
    <div>
      <BrowserRouter>
        <Routes>
        <Route path="login" element={<LoginForm />} />
        <Route path="home" element={<Home />} />
        <Route path="lab1" element={<Lab1 />}/>
      </Routes>
      </BrowserRouter>
    </div>
  );
};

export default App;
