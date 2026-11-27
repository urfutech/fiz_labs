import React, { useState, useEffect } from 'react';
import './lab1.css'
import { MathJaxProvider } from 'mathjaxjs-react';


const F = {
    rho: String.raw`$$\langle \rho \rangle = \frac{4m}{\pi \langle d \rangle^{2} \langle h \rangle}$$`,
    massErr: String.raw`$$\Delta_m = \theta_m = 1{,}1 \cdot \sqrt{\theta_{\text{осн}}^{2} + \theta_{\text{отс}}^{2}}$$`,
    dAvg: String.raw`$$\langle d \rangle = \frac{1}{n}\sum_{i=1}^{n} d_i$$`,
    dSumSq: String.raw`$$\sum_{i=1}^{n} \left( d_i - \langle d \rangle \right)^{2} = \dots\ \text{мм}^{2}$$`,
    Sd: String.raw`$$S_{\langle d \rangle} = \sqrt{\frac{\sum_{i=1}^{n} \left( d_i - \langle d \rangle \right)^{2}}{n\,(n-1)}}$$`,
    epsD: String.raw`$$\varepsilon_d = t_{P,n}\, S_{\langle d \rangle}$$`,
    thetaD: String.raw`$$\theta_d = \theta_{\text{осн}}$$`,
    DeltaD: String.raw`$$\Delta_d = \sqrt{\varepsilon_d^{2} + \theta_d^{2}}$$`,
    hAvg: String.raw`$$\langle h \rangle = \frac{1}{n}\sum_{i=1}^{n} h_i$$`,
    Sh: String.raw`$$S_{\langle h \rangle} = \sqrt{\frac{\sum_{i=1}^{n} \left( h_i - \langle h \rangle \right)^{2}}{n\,(n-1)}}$$`,
    epsH: String.raw`$$\varepsilon_h = t_{P,n}\, S_{\langle h \rangle}$$`,
    thetaH: String.raw`$$\theta_h = \theta_{\text{осн}}$$`,
    DeltaH: String.raw`$$\Delta_h = \sqrt{\varepsilon_h^{2} + \theta_h^{2}}$$`,
    rhoCalc: String.raw`$$\langle \rho \rangle = \frac{4\,\langle m \rangle}{\pi \langle d \rangle^{2} \langle h \rangle}$$`,
    gamma: String.raw`$$\gamma = \frac{\Delta_\rho}{\langle \rho \rangle} = \sqrt{\left(\frac{\Delta_m}{m}\right)^{2} + \left(2\,\frac{\Delta_d}{\langle d \rangle}\right)^{2} + \left(\frac{\Delta_h}{\langle h \rangle}\right)^{2}}$$`,
    deltaRho: String.raw`$$\Delta_\rho = \gamma \, \langle \rho \rangle$$`,
};

const Formula = ({ src }) => (
    <div className="formula-block" style={{ textAlign: 'center', margin: '8px 0' }}>
        {src}
    </div>
);

const Lab1 = ({ name, group, teacher }) => {

    useEffect(() => {
        const prev = document.body.style.backgroundColor;
        document.body.style.backgroundColor = '#fff';
        return () => {
            document.body.style.backgroundColor = prev;
        };
    }, []);

    const [formDetails, setFormDetails] = useState({
        defRho: '', defM: '', defD: '', defH: '',
        sampleNumber: '', mass: '', deltaMass: '',
        avgDiameter: '', sumSqDiameter: '', Sd: '',
        epsD: '', thetaD: '', deltaD: '',
        avgHeight: '', Sh: '', epsH: '', thetaH: '', deltaH: '',
        rho: '', gamma: '', deltaRho: '',
        finalRho: '',
        finalDelta: '',
        conclusion: '',
    });

    const [instruments, setInstruments] = useState(() =>
        Array.from({ length: 3 }, () => ({ name: '', limit: '', division: '', error: '' }))
    );
    const [dRows, setDRows] = useState(() =>
        Array.from({ length: 5 }, () => ({ d: '', dev: '', devSq: '' }))
    );
    const [hRows, setHRows] = useState(() =>
        Array.from({ length: 5 }, () => ({ h: '', dev: '', devSq: '' }))
    );

    const updateRow = (setRows) => (idx, field, value) =>
        setRows(prev => prev.map((row, i) => (i === idx ? { ...row, [field]: value } : row)));

    const updateInstrument = updateRow(setInstruments);
    const updateD = updateRow(setDRows);
    const updateH = updateRow(setHRows);


    const handleChange = (e) => {
        setFormDetails({ ...formDetails, [e.target.name]: e.target.value });
    };


    const handleSubmit = (e) => {
        e.preventDefault();

        //заменить на апи запросы
        console.log("Отправленные данные отчета:", formDetails);

        //просто плейсхолдер
        alert("Отчет успешно отправлен на проверку преподавателю!");
    };

    const numField = (name, label, unit) => (
        <div className="field-row">
            <label htmlFor={name}>{label}</label>
            <input
                className="form-control"
                type="text"
                name={name}
                id={name}
                required
                value={formDetails[name]}
                onChange={handleChange}
            />
            {unit && <span>{unit}</span>}
        </div>
    );

    return (
        <MathJaxProvider>
            <form className="input-form" onSubmit={handleSubmit}>
                <h1>Отчёт по лабораторной работе №1</h1>
                <h2>«Определение плотности твердых тел правильной формы»</h2>
                <p>
                    Студент: {name || '—'} | Группа: {group || '—'} | Преподаватель: {teacher || '—'}
                </p>

                <div className="input-part">1. Расчетная формула</div>
                <Formula src={F.rho} />
                <div className="input-wrapper">
                    <p>
                        где {String.raw`$\langle\rho\rangle$`} —
                        <input className="form-control" name="defRho" onChange={handleChange} />;
                        {String.raw`$m$`} —
                        <input className="form-control" name="defM" onChange={handleChange} />;
                        {String.raw`$\langle d\rangle$`} —
                        <input className="form-control" name="defD" onChange={handleChange} />;
                        {String.raw`$\langle h\rangle$`} —
                        <input className="form-control" name="defH" onChange={handleChange} />.
                    </p>
                </div>

                <div className="input-part">2. Средства измерений и их характеристики</div>
                <div className="input-wrapper">
                    <table className="measure-table">
                        <thead>
                            <tr>
                                <th>Наименование средства измерения</th>
                                <th>Предел измерений / номинальное значение</th>
                                <th>Цена деления шкалы</th>
                                <th>Предел основной погрешности θ<sub>осн</sub></th>
                            </tr>
                        </thead>
                        <tbody>
                            {instruments.map((row, i) => (
                                <tr key={i}>
                                    <td><input className="form-control" value={row.name}
                                        onChange={e => updateInstrument(i, 'name', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.limit}
                                        onChange={e => updateInstrument(i, 'limit', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.division}
                                        onChange={e => updateInstrument(i, 'division', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.error}
                                        onChange={e => updateInstrument(i, 'error', e.target.value)} /></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <label htmlFor="sampleNumber">Образец №</label>
                    <input className="form-control" type="text" name="sampleNumber" id="sampleNumber"
                        value={formDetails.sampleNumber} onChange={handleChange} />
                </div>
                <div className="input-part">3. Результаты измерений</div>

                <div className="input-wrapper">
                    <div className="input-inner-part">3.1. Измерение массы образца</div>
                    <Formula src={F.massErr} />
                    {numField('mass', String.raw`$m=$`, 'г;')}
                    {numField('deltaMass', String.raw`$\Delta_m=\theta_m=$`, 'г.')}
                </div>

                <div className="input-wrapper">
                    <div className="input-inner-part">3.2. Измерение диаметра образца</div>

                    <table className="measure-table">
                        <thead>
                            <tr>
                                <th>d<sub>i</sub>, мм</th>
                                <th>(d<sub>i</sub> − ⟨d⟩), мм</th>
                                <th>(d<sub>i</sub> − ⟨d⟩)², мм²</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dRows.map((row, i) => (
                                <tr key={i}>
                                    <td><input className="form-control" value={row.d}
                                        onChange={e => updateD(i, 'd', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.dev}
                                        onChange={e => updateD(i, 'dev', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.devSq}
                                        onChange={e => updateD(i, 'devSq', e.target.value)} /></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <Formula src={F.dAvg} />
                    {numField('avgDiameter', String.raw`$\langle d\rangle=$`, 'мм.')}

                    <Formula src={F.dSumSq} />
                    {numField('sumSqDiameter', String.raw`$\sum (d_i-\langle d\rangle)^{2}=$`, 'мм².')}

                    <div className="input-inner-part">Среднее квадратичное отклонение</div>
                    <Formula src={F.Sd} />
                    {numField('Sd', String.raw`$S_{\langle d\rangle}=$`, 'мм.')}

                    <div className="input-inner-part">Граница случайной погрешности</div>
                    <Formula src={F.epsD} />
                    {numField('epsD', String.raw`$\varepsilon_d=$`, 'мм.')}
                    <p>
                        где {String.raw`$t_{P,n}$`} — коэффициент Стьюдента для числа измерений
                        {String.raw` $n$`} и доверительной вероятности {String.raw`$P = 0{,}95$`}.
                    </p>

                    <div className="input-inner-part">Граница неисключенной систематической погрешности</div>
                    <Formula src={F.thetaD} />
                    {numField('thetaD', String.raw`$\theta_d=$`, 'мм.')}

                    <div className="input-inner-part">Граница полной погрешности диаметра</div>
                    <Formula src={F.DeltaD} />
                    {numField('deltaD', String.raw`$\Delta_d=$`, 'мм.')}

                    <p>
                        <b>Результат измерения диаметра:</b>{' '}
                        {String.raw`$\langle d\rangle =$`} {formDetails.avgDiameter || '…'} мм,{' '}
                        {String.raw`$\Delta_d =$`} {formDetails.deltaD || '…'} мм,{' '}
                        {String.raw`$P = 0{,}95$`}.
                    </p>
                </div>

                <div className="input-wrapper">
                    <div className="input-inner-part">3.3. Измерение высоты образца</div>

                    <table className="measure-table">
                        <thead>
                            <tr>
                                <th>h<sub>i</sub>, мм</th>
                                <th>(h<sub>i</sub> − ⟨h⟩), мм</th>
                                <th>(h<sub>i</sub> − ⟨h⟩)², мм²</th>
                            </tr>
                        </thead>
                        <tbody>
                            {hRows.map((row, i) => (
                                <tr key={i}>
                                    <td><input className="form-control" value={row.h}
                                        onChange={e => updateH(i, 'h', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.dev}
                                        onChange={e => updateH(i, 'dev', e.target.value)} /></td>
                                    <td><input className="form-control" value={row.devSq}
                                        onChange={e => updateH(i, 'devSq', e.target.value)} /></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <Formula src={F.hAvg} />
                    {numField('avgHeight', String.raw`$\langle h\rangle=$`, 'мм.')}

                    <div className="input-inner-part">Среднее квадратичное отклонение</div>
                    <Formula src={F.Sh} />
                    {numField('Sh', String.raw`$S_{\langle h\rangle}=$`, 'мм.')}

                    <div className="input-inner-part">Граница случайной погрешности</div>
                    <Formula src={F.epsH} />
                    {numField('epsH', String.raw`$\varepsilon_h=$`, 'мм.')}

                    <div className="input-inner-part">Граница неисключенной систематической погрешности</div>
                    <Formula src={F.thetaH} />
                    {numField('thetaH', String.raw`$\theta_h=$`, 'мм.')}

                    <div className="input-inner-part">Граница полной погрешности высоты</div>
                    <Formula src={F.DeltaH} />
                    {numField('deltaH', String.raw`$\Delta_h=$`, 'мм.')}

                    <p>
                        <b>Результат измерения высоты:</b>{' '}
                        {String.raw`$\langle h\rangle =$`} {formDetails.avgHeight || '…'} мм,{' '}
                        {String.raw`$\Delta_h =$`} {formDetails.deltaH || '…'} мм,{' '}
                        {String.raw`$P = 0{,}95$`}.
                    </p>
                </div>

                <div className="input-part">4. Расчет искомой величины в СИ</div>
                <div className="input-wrapper">
                    <Formula src={F.rhoCalc} />
                    {numField('rho', String.raw`$\langle\rho\rangle=$`, 'кг/м³')}
                </div>

                <div className="input-part">5. Оценка границы относительной погрешности</div>
                <div className="input-wrapper">
                    <Formula src={F.gamma} />
                    {numField('gamma', String.raw`$\gamma=$`, '%')}
                </div>

                <div className="input-part">6. Оценка границы абсолютной погрешности</div>
                <div className="input-wrapper">
                    <Formula src={F.deltaRho} />
                    {numField('deltaRho', String.raw`$\Delta_\rho=$`, 'кг/м³, P = 0,95.')}
                </div>

                <div className="input-part">7. Окончательный результат:</div>
                <div className="final-result-row">
                    <span className="math-text">{String.raw`$\rho = (\langle\rho\rangle \pm \Delta_\rho) = ($`}</span>

                    <input
                        className="inline-input"
                        type="text"
                        name="finalRho"
                        value={formDetails.finalRho}
                        onChange={handleChange}
                        placeholder="..."
                    />

                    <span className="math-text">{String.raw`$\pm$`}</span>

                    <input
                        className="inline-input"
                        type="text"
                        name="finalDelta"
                        value={formDetails.finalDelta}
                        onChange={handleChange}
                        placeholder="..."
                    />

                    <span className="math-text">{String.raw`$) \text{ кг/м}^3, \quad P = 0{,}95.$`}</span>
                </div>

                <div className="input-part">8. Выводы.</div>
                <div className="input-wrapper">
                    <textarea
                        className="form-control"
                        name="conclusion"
                        rows={4}
                        placeholder="Развернутый текстовый вывод по работе..."
                        value={formDetails.conclusion}
                        onChange={handleChange}
                        style={{ width: '100%', resize: 'vertical' }}
                    />
                </div>

                <div className="submit-section">
                    <button type="submit" className="submit-btn">
                        Отправить на проверку
                    </button>
                </div>

            </form>
        </MathJaxProvider>
    );
};
export default Lab1;
