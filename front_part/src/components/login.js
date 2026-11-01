import React, { useState } from 'react';
import Dropdown from './dropdown';

const LoginForm = ({ handleLogin, error }) => {
  const [formDetails, setFormDetails] = useState({
    fullname: '',
    name: '',
    patronym: '',
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormDetails({ ...formDetails, [e.target.name]: e.target.value });
  };

  const submitHandler = (e) => {
    e.preventDefault();

    handleLogin(formDetails);
  };

  return (
    <div className="container mt-3 card p-3 sm">
      <h2>УрФУ</h2>

      <form onSubmit={submitHandler}>
        <div className="text-center mt-3">
          <span className="text-danger">{error}</span>
        </div>

        <div className="mb-3 mt-3">
          <label htmlFor="fullname">ФИО</label>
          <input
            className="form-control"
            type="text"
            name="fullname"
            id="fullname"
            required
            value={formDetails.fullname}
            onChange={handleChange}
          />
        </div>

        <Dropdown title="Группа" options={['ПA-01', 'ПA-02', 'ПA-03']} />
        <Dropdown title="Преподаватель" options={['Преподавателев П. П.', 'Проектнов П. П.', 'Физиков Д. Э.']} />


        <div className="mb-3 mt-3">
          <label htmlFor="email">Почта</label>
          <input
            className="form-control"
            type="email"
            name="email"
            id="email"
            required
            value={formDetails.email}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3 mt-3">
          <label htmlFor="password">Пароль</label>
          <input
            className="form-control"
            type="password"
            name="password"
            id="password"
            required
            value={formDetails.password}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3 mt-3">
          <label htmlFor="password">Подтвердите пароль</label>
          <input
            className="form-control"
            type="password"
            name="confirmPassword"
            id="confirmPassword"
            required
            onChange={handleChange}
          />
        </div>

        <button type="submit" className="btn btn-primary">
          Зарегистрироваться
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
