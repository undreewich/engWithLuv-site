// Базовый URL для API
const API_BASE_URL = '/api';

// Функция-обертка для fetch с проверкой 401 ошибки
async function secureFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        // Если получен статус 401, перенаправляем на страницу входа
        if (response.status === 401) {
            console.warn('Сессия истекла или доступ запрещен (401). Перенаправление на страницу входа...');
            window.location.href = '/admin/login';
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Загружаем данные для всех таблиц при загрузке страницы
    loadAllTables();

    // Обработчик для закрытия модальных окон при клике вне них
    window.onclick = function(event) {
        const modals = [
            document.getElementById('editStudentModal'),
            document.getElementById('createInvoiceModal')
        ];

        modals.forEach(modal => {
            if (modal && event.target === modal) {
                modal.style.display = 'none';
            }
        });
    };
});

function logout() {
    // Перенаправление на страницу входа
    window.location.href = '/admin/login';
}

// Получение данных студентов с пагинацией
async function fetchStudents(limit = studentPageLimit, offset = 0) {
    try {
        const response = await secureFetch(`${API_BASE_URL}/admin/students?limit=${limit}&offset=${offset}`);
        if (!response || !response.ok) {
            throw new Error('Ошибка при получении данных студентов');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении данных студентов:', error);
        return [];
    }
}

// Заглушка для получения данных расписания
async function fetchSchedule() {
    try {
        const response = await secureFetch(`${API_BASE_URL}/admin/schedule`);
        if (!response || !response.ok) {
            throw new Error('Ошибка при получении данных расписания');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении данных расписания:', error);
        return [];
    }
}

// Заглушка для получения данных кучи уроков
async function fetchLessonsHeap() {
    try {
        const response = await secureFetch(`${API_BASE_URL}/admin/lessons-heap`);
        if (!response || !response.ok) {
            throw new Error('Ошибка при получении данных кучи уроков');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении данных кучи уроков:', error);
        return [];
    }
}

// Заглушка для получения данных истории уроков
async function fetchLessonsHistory() {
    try {
        const response = await secureFetch(`${API_BASE_URL}/admin/lessons-history`);
        if (!response || !response.ok) {
            throw new Error('Ошибка при получении данных истории уроков');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении данных истории уроков:', error);
        return [];
    }
}

// Получение данных платежей с пагинацией
async function fetchPayments(limit = paymentPageLimit, offset = 0) {
    try {
        const response = await secureFetch(`${API_BASE_URL}/admin/invoices?limit=${limit}&offset=${offset}`);
        if (!response || !response.ok) {
            throw new Error('Ошибка при получении данных платежей');
        }
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении данных платежей:', error);
        return [];
    }
}

// Функция для авторизации администратора
async function loginAdmin(password) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });

        if (response.status === 200) {
            return { success: true };
        } else if (response.status === 401) {
            return { success: false, error: 'Неверный пароль' };
        } else {
            return { success: false, error: 'Ошибка сервера' };
        }
    } catch (error) {
        console.error('Ошибка при авторизации:', error);
        return { success: false, error: 'Ошибка сети' };
    }
}

let studentLoadOffset = 0;
let studentPageLimit = 50;
let hasMoreStudents = true;
let paymentLoadOffset = 0;
let paymentPageLimit = 50;
let hasMorePayments = true;

// Функция для заполнения выпадающих списков учеников
function populateStudentSelects(students) {
    const selects = ['paymentLinkStudent', 'addLessonsStudent', 'addPaymentStudent'];
    
    selects.forEach(id => {
        const select = document.getElementById(id);
        select.innerHTML = '<option value="">Выберите ученика</option>';
        
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${student.name} ${student.surname}`;
            select.appendChild(option);
        });
    });
}

// Функция для загрузки всех таблиц
async function loadAllTables() {
    await Promise.all([
        loadStudentsTable(),
        loadScheduleTable(),
        loadLessonsHeapTable(),
        loadLessonsHistoryTable(),
        loadPaymentsTable()
    ]);
    
    // Устанавливаем сегодняшнюю дату для поля даты оплаты
    document.getElementById('addPaymentDate').value = new Date().toISOString().split('T')[0];
}

// Функции для загрузки конкретных таблиц
async function loadStudentsTable() {
    studentLoadOffset = 0;
    hasMoreStudents = true;

    const data = await fetchStudents(studentPageLimit, studentLoadOffset);
    renderTable('studentsTable', data, ['id', 'name', 'surname', 'email', 'prepaidLessonsCount', 'doneLessonsCount', 'prepaidSum', 'usedSum', 'isActive', 'age']);
    populateStudentSelects(data);
    studentLoadOffset = data.length;
    hasMoreStudents = data.length === studentPageLimit;
}

async function loadScheduleTable() {
    const data = await fetchSchedule();
    renderTable('scheduleTable', data, ['id', 'dayname', 'daytimeH', 'daytimeM', 'daytimeHreal', 'daytimeMreal', 'student', 'isActive']);
}

async function loadLessonsHeapTable() {
    const data = await fetchLessonsHeap();
    renderTable('lessonsHeapTable', data, ['id', 'student', 'price']);
}

async function loadLessonsHistoryTable() {
    const data = await fetchLessonsHistory();
    renderTable('lessonsHistoryTable', data, ['id', 'student', 'price', 'lesson_date', 'dayname', 'daytimeHreal', 'daytimeMreal', 'isDone', 'isSkipped']);
}

async function loadPaymentsTable() {
    paymentLoadOffset = 0;
    hasMorePayments = true;
    const data = await fetchPayments(paymentPageLimit, paymentLoadOffset);
    renderTable('paymentsTable', data, ['id', 'student', 'amount', 'isPaid', 'created', 'expiry_date', 'link']);
    paymentLoadOffset = data.length;
    hasMorePayments = data.length === paymentPageLimit;
}

// Универсальная функция для рендеринга таблицы
function renderTable(tableId, data, columns, append = false) {
    const tbody = document.querySelector(`#${tableId} tbody`);

    if (!append) {
        tbody.innerHTML = '';
    }

    if (data.length === 0) {
        const colspan = tableId === 'studentsTable' ? columns.length + 1 : columns.length;
        if (!append || tbody.children.length === 0) {
            tbody.innerHTML = '<tr><td colspan="' + colspan + '" style="text-align: center; padding: 20px;">Нет данных</td></tr>';
        }
        return;
    }

    data.forEach(row => {
        const tr = document.createElement('tr');
        columns.forEach(column => {
            const td = document.createElement('td');
            let value = row[column];

            // Форматирование специальных типов данных
            if (column.includes('Sum') || column.includes('price') || column === 'sum' || column === 'amount') {
                value = parseFloat(value).toFixed(2) + ' €';
            } else if (column === 'isActive' || column === 'isDone' || column === 'isSkipped' || column === 'isPaid') {
                value = value ? 'Да' : 'Нет';
            } else if (column === 'lesson_date' || column === 'created' || column === 'expiry_date') {
                value = value ? new Date(value).toLocaleString('ru-RU') : '';
            }

            if (column === 'link') {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-btn';
                copyBtn.textContent = '📋';
                copyBtn.title = 'Копировать ссылку';
                copyBtn.onclick = () => copyTextToClipboard(row.link || '');
                td.appendChild(copyBtn);
                tr.appendChild(td);
                return;
            }

            td.textContent = value;
            tr.appendChild(td);
        });

        if (tableId === 'studentsTable') {
            const invoiceTd = document.createElement('td');
            const invoiceBtn = document.createElement('button');
            invoiceBtn.className = 'edit-btn';
            invoiceBtn.innerHTML = '💳';
            invoiceBtn.title = 'Выставить счет';
            invoiceBtn.onclick = () => openCreateInvoiceModal(row);
            invoiceTd.appendChild(invoiceBtn);
            tr.appendChild(invoiceTd);

            const actionTd = document.createElement('td');
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.innerHTML = '✏️';
            editBtn.title = 'Редактировать';
            editBtn.onclick = () => openEditModal(row);
            actionTd.appendChild(editBtn);
            tr.appendChild(actionTd);
        }

        tbody.appendChild(tr);
    });
}

// Функции для модального окна редактирования студента
function openEditModal(student) {
    console.log('Открытие модала для студента:', student);
    document.getElementById('editStudentId').value = student.id;
    document.getElementById('editStudentName').value = student.name;
    document.getElementById('editStudentSurname').value = student.surname;
    document.getElementById('editStudentEmail').value = student.email;
    document.getElementById('editStudentPrepaidLessons').value = student.prepaidLessonsCount;
    document.getElementById('editStudentDoneLessons').value = student.doneLessonsCount;
    document.getElementById('editStudentPrepaidSum').value = student.prepaidSum;
    document.getElementById('editStudentUsedSum').value = student.usedSum;
    document.getElementById('editStudentIsActive').value = student.isActive.toString();
    document.getElementById('editStudentAge').value = student.age;
    document.getElementById('editStudentModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('editStudentModal').style.display = 'none';
}

function openCreateInvoiceModal(student) {
    const studentSelect = document.getElementById('paymentLinkStudent');
    if (studentSelect) {
        studentSelect.value = String(student.id);
    }

    const amountInput = document.getElementById('paymentLinkAmount');
    if (amountInput) {
        amountInput.value = '';
    }

    const modal = document.getElementById('createInvoiceModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeInvoiceModal() {
    const modal = document.getElementById('createInvoiceModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function saveStudentChanges() {
    const studentData = {
        id: document.getElementById('editStudentId').value,
        name: document.getElementById('editStudentName').value,
        surname: document.getElementById('editStudentSurname').value,
        email: document.getElementById('editStudentEmail').value,
        prepaidLessonsCount: parseInt(document.getElementById('editStudentPrepaidLessons').value),
        doneLessonsCount: parseInt(document.getElementById('editStudentDoneLessons').value),
        prepaidSum: parseFloat(document.getElementById('editStudentPrepaidSum').value),
        usedSum: parseFloat(document.getElementById('editStudentUsedSum').value),
        isActive: document.getElementById('editStudentIsActive').value === 'true',
        age: parseInt(document.getElementById('editStudentAge').value)
    };
    
    console.log('Отправка изменений студента на сервер:', studentData);
    
    // Имитация отправки на сервер
    secureFetch(`${API_BASE_URL}/admin/students/${studentData.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(studentData)
    }).then(response => {
        if (response && response.ok) {
            alert('Изменения сохранены успешно!');
            closeModal();
            // Перезагрузить таблицу студентов
            loadStudentsTable();
        } else {
            alert('Ошибка при сохранении изменений.');
        }
    }).catch(error => {
        console.error('Ошибка при сохранении:', error);
        alert('Ошибка при сохранении изменений.');
    });
}

// Функция для копирования в буфер обмена
async function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    try {
        await navigator.clipboard.writeText(text);
        alert('Ссылка скопирована в буфер обмена!');
    } catch (err) {
        console.error('Ошибка копирования:', err);
        // Fallback для старых браузеров
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Ссылка скопирована в буфер обмена!');
    }
}

async function copyTextToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        alert('Ссылка скопирована в буфер обмена!');
    } catch (err) {
        console.error('Ошибка копирования:', err);
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Ссылка скопирована в буфер обмена!');
    }
}

// Функции для загрузки дополнительных данных
async function loadMoreStudents() {
    if (!hasMoreStudents) {
        return;
    }

    console.log('Загрузка дополнительных студентов...', { offset: studentLoadOffset, limit: studentPageLimit });

    const data = await fetchStudents(studentPageLimit, studentLoadOffset);
    if (!data.length) {
        hasMoreStudents = false;
        return;
    }

    renderTable('studentsTable', data, ['id', 'name', 'surname', 'email', 'prepaidLessonsCount', 'doneLessonsCount', 'prepaidSum', 'usedSum', 'isActive', 'age'], true);
    studentLoadOffset += data.length;
    hasMoreStudents = data.length === studentPageLimit;
}

function loadMoreSchedule() {
    console.log('Загрузка дополнительного расписания...');
    alert('Заглушка: Загрузка дополнительного расписания (не реализовано)');
}

function loadMoreLessonsHeap() {
    console.log('Загрузка дополнительных оставшихся уроков...');
    alert('Заглушка: Загрузка дополнительных оставшихся уроков (не реализовано)');
}

function loadMoreLessonsHistory() {
    console.log('Загрузка дополнительной истории уроков...');
    alert('Заглушка: Загрузка дополнительной истории уроков (не реализовано)');
}

async function loadMorePayments() {
    if (!hasMorePayments) {
        return;
    }

    console.log('Загрузка дополнительных платежей...', { offset: paymentLoadOffset, limit: paymentPageLimit });

    const data = await fetchPayments(paymentPageLimit, paymentLoadOffset);
    if (!data.length) {
        hasMorePayments = false;
        return;
    }

    renderTable('paymentsTable', data, ['id', 'student', 'amount', 'isPaid', 'created', 'expiry_date', 'link'], true);
    paymentLoadOffset += data.length;
    hasMorePayments = data.length === paymentPageLimit;
}

// Заглушки для новых функций
function createPaymentLink() {
    const studentId = document.getElementById('paymentLinkStudent').value;
    const amount = document.getElementById('paymentLinkAmount').value;
    console.log('Создание ссылки для оплаты:', { studentId, amount });
    

    secureFetch(`${API_BASE_URL}/new-invoice`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"studentId": studentId, "amount": amount})
    }).then(response => {
        if (response && response.ok) {
            return response.json();
        } else {
            console.error('Ошибка при при создании ссылки:', error);
             alert('Ошибка при при создании ссылки.');
        }
    })
    .then(data => {
        console.log("data:", data);
        document.getElementById('paymentLinkUrl').textContent = data["link"];
        document.getElementById('paymentLinkResult').style.display = 'block'; 
    })
    .catch(error => {
        console.error('Ошибка при при создании ссылки:', error);
        alert('Ошибка при при создании ссылки.');
    });
}


function addLessons() {
    const studentId = document.getElementById('addLessonsStudent').value;
    const price = document.getElementById('addLessonsPrice').value;
    const count = document.getElementById('addLessonsCount').value;
    console.log('Добавление уроков:', { studentId, price, count });
    alert('Заглушка: Уроки добавлены (не реализовано)');
}

function addPayment() {
    const studentId = document.getElementById('addPaymentStudent').value;
    const amount = document.getElementById('addPaymentAmount').value;
    const date = document.getElementById('addPaymentDate').value;
    console.log('Добавление оплаты:', { studentId, amount, date });
    alert('Заглушка: Оплата добавлена (не реализовано)');
}

function addStudent() {
    const name = document.getElementById('addStudentName').value.trim();
    const surname = document.getElementById('addStudentSurname').value.trim();
    const email = document.getElementById('addStudentEmail').value.trim();
    const age = parseInt(document.getElementById('addStudentAge').value, 10);

    console.log('Добавление ученика:', { name, surname, email, age });

    if (!name || !surname || !email || Number.isNaN(age)) {
        alert('Заполните имя, фамилию, email и возраст.');
        return;
    }

    secureFetch(`${API_BASE_URL}/admin/students`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, surname, email, age })
    })
    .then(response => {
        if (!response) { return; }
        if (response.ok) {
            alert('Ученик успешно добавлен!');
            document.getElementById('addStudentName').value = '';
            document.getElementById('addStudentSurname').value = '';
            document.getElementById('addStudentEmail').value = '';
            document.getElementById('addStudentAge').value = '';
            return loadStudentsTable();
        }
        return response.json().then(data => {
            throw new Error(data.message || 'Ошибка при добавлении ученика');
        });
    })
    .catch(error => {
        console.error('Ошибка при добавлении ученика:', error);
        alert(error.message || 'Ошибка при добавлении ученика.');
    });
}