import React, { useState } from 'react';

function Dropdown({ title, name, value, options, onChange }) {

    const [isOpen, setIsOpen] = useState(false);
    const [selectedOption, setSelectedOption] = useState('Выберите вариант');

    const groupOptions = ['ПA-01', 'ПA-02', 'ПA-03'];
    const teacherOptions = ['Преподавателев П. П.', 'Проектнов П. П.', 'Физиков Д. Э.'];

    const toggleDropdown = () => setIsOpen(!isOpen);

    const handleOptionClick = (option) => {
        onChange({ target: { name, value: option } });
        setIsOpen(false);
    };

    return (

        <div className="dropdown" style={{ position: 'relative', display: 'inline-block' }}>
            <label htmlFor={name}>{title}</label>
            <input
                className="form-control"
                type="text"
                name={name}
                id={name}
                readOnly
                required
                value={value || ''}
                placeholder="Выберите вариант"
                onClick={toggleDropdown}
                style={{ cursor: 'pointer' }}
            />
            <button class="icon-button" aria-label="Раскрыть" onClick={toggleDropdown}> 
                
            </button>


            {isOpen && (
                <ul style={{
                    position: 'absolute',
                    width: '100%',
                    top: '100%',
                    left: 0,
                    listStyle: 'none',
                    padding: '8px',
                    margin: '4px 0 0',
                    border: '1px solid #ccc',
                    background: '#fff',
                    zIndex: isOpen ? 50 : 1
                }}>
                    {options.map((option, index) => (
                        <li
                            key={index}
                            onClick={() => handleOptionClick(option)}
                            style={{ cursor: 'pointer', padding: '4px 8px' }}
                        >
                            {option}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default Dropdown;