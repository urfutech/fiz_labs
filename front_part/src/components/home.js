import React, { useState } from 'react';
import './home.css';

const Home = ({ name, group, teacher }) => {
    const firstLetter = name ? name.trim().charAt(0).toUpperCase() : '';
    return (
        <div>
            <div>
                <span>icon</span>
                <span>{firstLetter}</span>
                <h2>
                    <span>{name}</span>
                    <span>{group}</span>
                </h2>
                <span>icon</span>
            </div>

            <div>
                <h1>Лабораторные работы по физике(1 семестр)</h1>
                <h2>Ваша группа: {group}</h2>
                <h2>Ваш преподаватель: {teacher}</h2>
            </div>

            <div>
                <h2>Cписок доступных к выполнению работ:</h2>
            </div>

        </div>

        
    );
};
export default Home;
