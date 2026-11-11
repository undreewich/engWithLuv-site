function getItemLabel(item) {
    if (typeof item === 'string') {
        return item;
    }

    if (item && typeof item === 'object') {
        return item.title || item.name || item.lesson_date || JSON.stringify(item);
    }

    return String(item);
}

async function loadDashboardSection(section) {
    const emptyState = section.querySelector('[data-empty-state]');
    const itemsList = section.querySelector('[data-items]');

    try {
        const response = await fetch(section.dataset.endpoint, {
            method: 'GET',
            credentials: 'include',
            headers: { Accept: 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const items = await response.json();
        if (!Array.isArray(items)) {
            throw new Error('Ожидался список данных');
        }

        if (items.length === 0) {
            emptyState.textContent = 'Пока нет данных.';
            return;
        }

        itemsList.replaceChildren(...items.map((item) => {
            const listItem = document.createElement('li');
            listItem.textContent = getItemLabel(item);
            return listItem;
        }));
        itemsList.hidden = false;
        emptyState.hidden = true;
    } catch (error) {
        console.error('Не удалось загрузить данные раздела кабинета:', error);
        emptyState.textContent = 'Не удалось загрузить данные. Попробуйте обновить страницу.';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-dashboard-section]').forEach(loadDashboardSection);
});
