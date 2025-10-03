/*
  Скрипт рендерит таблицу из API /payroll/api/summary-data/?year=YYYY
  Ожидаемый формат API (пример одной записи):
  {
    department: "IT",
    employee: "ФИО",
    opening_balance: 0,
    months: {
      "01": {accrued:123, payout:45, balance:78}, "02": {...}, ...
    }
  }
*/

const colDeptW = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--col-dept-w')) || 260;
const colEmpW  = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--col-emp-w')) || 220;
const colInW   = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--col-in-w')) || 140;
const subW     = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--subcol-w')) || 110;

function formatNumber(v){
  if (v === null || v === undefined) return '';
  const n = Number(v);
  if (isNaN(n)) return '';
  // 2 decimals, space as thousands separator
  return n.toLocaleString('ru-RU', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function createYearOptions(selEl, rangeStart=2020, rangeEnd=2030, current=null){
  selEl.innerHTML = '';
  for (let y=rangeStart; y<=rangeEnd; y++){
    const opt = document.createElement('option');
    opt.value = y;
    opt.textContent = y;
    if (current && y===current) opt.selected = true;
    selEl.appendChild(opt);
  }
}

// Понятная группировка: сгруппируем записи по отделу, чтобы отдел выводился 1 раз
function groupByDepartment(data){
  const groups = {};
  data.forEach(item => {
    const dept = item.department || 'Без отдела';
    if (!groups[dept]) groups[dept] = [];
    groups[dept].push(item);
  });
  return groups; // { deptName: [ items ] }
}

async function loadSummary(year){
  const table = document.getElementById('summaryTable');
  table.innerHTML = ''; // очистка

  const resp = await fetch(`/payroll/api/summary-data/?year=${year}`);
  if (!resp.ok) {
    table.innerHTML = `<thead><tr><th style="color:#c00">Ошибка загрузки данных: ${resp.status}</th></tr></thead>`;
    return;
  }
  const data = await resp.json();

  // if API returns objects with keys months as numbers, normalize keys to "01",.. "12"
  data.forEach(it=>{
    if (it.months){
      // ensure keys "01".."12"
      const norm = {};
      for (let m=1;m<=12;m++){
        const k = String(m).padStart(2,'0');
        norm[k] = it.months[k] || (it.months[m] || {accrued:0,payout:0,balance:0});
      }
      it.months = norm;
    } else {
      // defensive
      it.months = {};
      for (let m=1;m<=12;m++){ it.months[String(m).padStart(2,'0')] = {accrued:0,payout:0,balance:0}; }
    }
  });

  // Заголовки: сформируем thead с двумя строками
  const thead = document.createElement('thead');
  const tr1 = document.createElement('tr');
  const tr2 = document.createElement('tr');

  // left fixed headers (dept, employee, incoming)
  const thDept = document.createElement('th');
  thDept.className = 'col-dept';
  thDept.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-dept-w');
  thDept.rowSpan = 2;
  thDept.textContent = 'Отдел / ФИО';
  tr1.appendChild(thDept);

  const thEmp = document.createElement('th');
  thEmp.className = 'col-emp';
  thEmp.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-emp-w');
  thEmp.rowSpan = 2;
  thEmp.textContent = '';
  // (мы уже используем одного столбца для dept/ФИО, но чтобы сохранить структуру — можно оставить пустой)
  // We'll keep two left columns visually merged: we will render department as a group row spanning whole width,
  // but also keep employee column fixed for each employee row.
  tr1.appendChild(thEmp);

  const thIn = document.createElement('th');
  thIn.className = 'col-in';
  thIn.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-in-w');
  thIn.rowSpan = 2;
  thIn.textContent = 'Входящий остаток';
  tr1.appendChild(thIn);

  // months headers (each with colspan=3)
  const months = ["Января","Февраля","Марта","Апреля","Мая","Июня","Июля","Августа","Сентября","Октября","Ноября","Декабря"];
  months.forEach(m=>{
    const th = document.createElement('th');
    th.colSpan = 3;
    th.textContent = m + ' ' + year;
    tr1.appendChild(th);
  });

  // second row subheaders
  for (let i=0;i<12;i++){
    const s1 = document.createElement('th'); s1.className = 'subhead month-sub'; s1.textContent='Начислено'; tr2.appendChild(s1);
    const s2 = document.createElement('th'); s2.className = 'subhead month-sub'; s2.textContent='Выплачено';  tr2.appendChild(s2);
    const s3 = document.createElement('th'); s3.className = 'subhead month-sub'; s3.textContent='Остаток';   tr2.appendChild(s3);
  }

  thead.appendChild(tr1);
  thead.appendChild(tr2);
  table.appendChild(thead);

  // Тело таблицы — сгруппировать по отделам
  const tbody = document.createElement('tbody');
  const grouped = groupByDepartment(data);

  // вычислим colspan для строки отдела
  const totalCols = 3 + 12*3; // left 3 + months*3

  Object.keys(grouped).forEach(deptName=>{
    const group = grouped[deptName]; // массив сотрудников
    // строка-лейбл отдела (один раз)
    const trGroup = document.createElement('tr');
    trGroup.className = 'dept-group';
    const td = document.createElement('td');
    td.colSpan = totalCols;
    td.textContent = deptName;
    td.style.textAlign = 'left';
    td.style.paddingLeft = '10px';
    trGroup.appendChild(td);
    tbody.appendChild(trGroup);

    // затем по каждому сотруднику
    group.forEach(item=>{
      const tr = document.createElement('tr');

      // колонка Отдел (мы показываем пустую, поскольку dept group уже вывели)
      const tdDept = document.createElement('td');
      tdDept.className = 'col-dept';
      tdDept.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-dept-w');
      tdDept.textContent = ''; // пустая, т.к. группа выше содержит название отдела
      tr.appendChild(tdDept);

      // колонка ФИО
      const tdEmp = document.createElement('td');
      tdEmp.className = 'col-emp';
      tdEmp.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-emp-w');
      tdEmp.textContent = item.employee;
      tr.appendChild(tdEmp);

      // колонка входящий остаток (editable)
      const tdIn = document.createElement('td');
      tdIn.className = 'col-in incoming';
      tdIn.style.width = getComputedStyle(document.documentElement).getPropertyValue('--col-in-w');
      tdIn.contentEditable = true;
      tdIn.dataset.empId = item.employee_id || '';
      tdIn.textContent = formatNumber(item.opening_balance || 0);
      // можно добавить обработчик blur для сохранения
      tr.appendChild(tdIn);

      // месяцы
      for (let m=1;m<=12;m++){
        const key = String(m).padStart(2,'0');
        const md = (item.months && item.months[key]) ? item.months[key] : {accrued:0,payout:0,balance:0};

        const tdA = document.createElement('td'); tdA.className='month-sub'; tdA.textContent = formatNumber(md.accrued); tr.appendChild(tdA);
        const tdB = document.createElement('td'); tdB.className='month-sub'; tdB.textContent = formatNumber(md.payout); tr.appendChild(tdB);
        const tdC = document.createElement('td'); tdC.className='month-sub'; tdC.textContent = formatNumber(md.balance);
        if (Number(md.balance) < 0) tdC.classList.add('negative');
        tr.appendChild(tdC);
      }

      tbody.appendChild(tr);
    });

    // опциональная строка "Итого по отделу"
    const totalRow = document.createElement('tr');
    totalRow.className = 'dept-total';
    const tdEmpty1 = document.createElement('td'); tdEmpty1.className='col-dept'; tdEmpty1.textContent=''; totalRow.appendChild(tdEmpty1);
    const tdLabel = document.createElement('td'); tdLabel.className='col-emp'; tdLabel.textContent = 'Итого по отделу'; totalRow.appendChild(tdLabel);
    const tdEmptyIn = document.createElement('td'); tdEmptyIn.className='col-in'; tdEmptyIn.textContent=''; totalRow.appendChild(tdEmptyIn);

    // просуммируем по месяцам для отдела
    for (let m=1;m<=12;m++){
      const key = String(m).padStart(2,'0');
      let sumAcc = 0, sumPay=0;
      group.forEach(it=>{
        const md = it.months && it.months[key] ? it.months[key] : {accrued:0,payout:0,balance:0};
        sumAcc += Number(md.accrued || 0);
        sumPay += Number(md.payout || 0);
      });
      const sumBal = sumAcc - sumPay;
      const tdAcc = document.createElement('td'); tdAcc.textContent = formatNumber(sumAcc); totalRow.appendChild(tdAcc);
      const tdPay = document.createElement('td'); tdPay.textContent = formatNumber(sumPay); totalRow.appendChild(tdPay);
      const tdBal = document.createElement('td'); tdBal.textContent = formatNumber(sumBal); if (sumBal<0) tdBal.classList.add('negative'); totalRow.appendChild(tdBal);
    }
    tbody.appendChild(totalRow);
  });

  table.appendChild(tbody);

  // Добавим повесить обработчик на входящие остатки (сохранение при blur) — пример заглушки
  document.querySelectorAll('.incoming').forEach(el=>{
    el.addEventListener('blur', (e)=>{
      const val = e.target.textContent.replace(/\s/g,'').replace(',','.');
      // здесь можно валидировать и отправлять PATCH/POST на сервер
      // console.log('save incoming for emp', e.target.dataset.empId, val);
      // Для наглядности — форматируем обратно
      e.target.textContent = formatNumber(Number(val || 0));
    });
  });
}

// автозаполнение списка годов и начальная загрузка
(function init(){
  const sel = document.getElementById('yearSelect');
  const now = new Date().getFullYear();
  // от 2020 до now+1
  for (let y = 2020; y <= now+1; y++){
    const o = document.createElement('option');
    o.value = y; o.textContent = y;
    if (y === now) o.selected = true;
    sel.appendChild(o);
  }
  loadSummary(now);
})();