// Базовый URL для API
const API_BASE_URL = '/admin';

function showNotice(message, isError = false) {
    let notice = document.getElementById('appNotice');
    if (!notice) {
        notice = document.createElement('div');
        notice.id = 'appNotice';
        notice.setAttribute('role', 'status');
        notice.style.cssText = 'position:fixed;right:20px;bottom:20px;z-index:10000;max-width:min(420px,calc(100vw - 40px));padding:14px 18px;border-radius:10px;background:#eef9f1;color:#277342;box-shadow:0 8px 28px rgba(0,0,0,.18);font:500 14px/1.45 sans-serif;';
        document.body.appendChild(notice);
    }
    notice.setAttribute('role', isError ? 'alert' : 'status');
    notice.style.background = isError ? '#fff0f1' : '#eef9f1';
    notice.style.color = isError ? '#a93245' : '#277342';
    notice.textContent = message;
    notice.hidden = false;
    clearTimeout(notice.dismissTimer);
    notice.dismissTimer = setTimeout(() => { notice.hidden = true; }, 5000);
}

function getErrorMessage(error, fallback = 'Неизвестная ошибка') {
    if (error instanceof Error && error.message) {
        return error.message;
    }
    return typeof error === 'string' && error.trim() ? error : fallback;
}

// Функция-обертка для fetch с проверкой 401 ошибки
async function secureFetch(url, options = {}) {
    try {
        const requestOptions = {
            ...options,
            credentials: 'include',
            headers: { ...options.headers, Accept: 'application/json' }
        };
        let response = await fetch(url, requestOptions);

        if (response.status === 401) {
            const refreshResponse = await fetch('/refresh', {
                method: 'POST',
                credentials: 'include',
                headers: { Accept: 'application/json' }
            });
            if (!refreshResponse.ok) {
                window.location.replace('/admin/login');
                return null;
            }
            response = await fetch(url, requestOptions);
        }

        if (response.status === 401) {
            window.location.replace('/admin/login');
            return null;
        }

        if (response.status === 403) {
            window.location.replace('/');
            return null;
        }
        return response;
    } catch (_error) {
        return null;
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
        return [];
    }
}

// Функция для авторизации администратора
async function loginAdmin(email, password) {
    try {
        const response = await fetch('/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email, password: password })
        });

        const data = await response.json();
        if (response.status === 200) {
            return { success: true };
        } else if (response.status === 401) {
            return { success: false, error: data.message || 'Неверный email или пароль' };
        } else {
            return { success: false, error: data.message || 'Ошибка сервера' };
        }
    } catch (_error) {
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
    
    // Имитация отправки на сервер
    secureFetch(`${API_BASE_URL}/admin/students/${studentData.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(studentData)
    }).then(response => {
        if (response && response.ok) {
            showNotice('Изменения сохранены успешно.');
            closeModal();
            // Перезагрузить таблицу студентов
            loadStudentsTable();
        } else {
            showNotice('Не удалось сохранить изменения. Попробуйте позже.', true);
        }
    }).catch(error => {
        const message = getErrorMessage(error, 'Неизвестная ошибка');
        showNotice('Не удалось сохранить изменения. Попробуйте позже.', true);
    });
}

// Функция для копирования в буфер обмена
async function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    try {
        await navigator.clipboard.writeText(text);
        showNotice('Ссылка скопирована в буфер обмена.');
    } catch (err) {
        try {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            const copied = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (!copied) {
                throw new Error('Браузер не подтвердил копирование.');
            }
            showNotice('Ссылка скопирована в буфер обмена.');
        } catch (fallbackError) {
            showNotice('Не удалось скопировать ссылку. Скопируйте её вручную.', true);
        }
    }
}

async function copyTextToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotice('Ссылка скопирована в буфер обмена.');
    } catch (err) {
        try {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            const copied = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (!copied) {
                throw new Error('Браузер не подтвердил копирование.');
            }
            showNotice('Ссылка скопирована в буфер обмена.');
        } catch (fallbackError) {
            showNotice('Не удалось скопировать ссылку. Скопируйте её вручную.', true);
        }
    }
}

// Функции для загрузки дополнительных данных
async function loadMoreStudents() {
    if (!hasMoreStudents) {
        return;
    }

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
    showNotice('Загрузка расписания пока недоступна.', true);
}

function loadMoreLessonsHeap() {
    showNotice('Загрузка оставшихся уроков пока недоступна.', true);
}

function loadMoreLessonsHistory() {
    showNotice('Загрузка истории уроков пока недоступна.', true);
}

async function loadMorePayments() {
    if (!hasMorePayments) {
        return;
    }

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
    secureFetch(`${API_BASE_URL}/new-invoice`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({"studentId": studentId, "amount": amount})
    }).then(response => {
        if (!response) {
            throw new Error('Сессия истекла. Войдите в систему заново.');
        }
        return response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.message || `Сервер вернул ошибку ${response.status}.`);
            }
            return data;
        });
    })
    .then(data => {
        if (!data || !data.link) {
            throw new Error('Сервер не вернул ссылку на оплату.');
        }
        document.getElementById('paymentLinkUrl').textContent = data.link;
        document.getElementById('paymentLinkResult').style.display = 'block'; 
    })
    .catch(error => {
        const message = getErrorMessage(error, 'Неизвестная ошибка');
        showNotice('Не удалось создать ссылку на оплату. Попробуйте позже.', true);
    });
}


function addLessons() {
    const studentId = document.getElementById('addLessonsStudent').value;
    const price = document.getElementById('addLessonsPrice').value;
    const count = document.getElementById('addLessonsCount').value;
    showNotice('Добавление уроков пока недоступно.', true);
}

function addPayment() {
    const studentId = document.getElementById('addPaymentStudent').value;
    const amount = document.getElementById('addPaymentAmount').value;
    const date = document.getElementById('addPaymentDate').value;
    showNotice('Добавление оплаты пока недоступно.', true);
}

function addStudent() {
    const name = document.getElementById('addStudentName').value.trim();
    const surname = document.getElementById('addStudentSurname').value.trim();
    const email = document.getElementById('addStudentEmail').value.trim();
    const age = parseInt(document.getElementById('addStudentAge').value, 10);

    if (!name || !surname || !email || Number.isNaN(age)) {
        showNotice('Заполните имя, фамилию, email и возраст.', true);
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
            showNotice('Ученик успешно добавлен.');
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
        const message = getErrorMessage(error, 'Неизвестная ошибка');
        showNotice('Не удалось добавить ученика. Проверьте данные и попробуйте снова.', true);
    });
}