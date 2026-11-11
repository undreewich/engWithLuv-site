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
        const options = {
            method: 'GET',
            credentials: 'include',
            headers: { Accept: 'application/json' }
        };
        let response = await fetch(section.dataset.endpoint, options);

        if (response.status === 401) {
            const refreshResponse = await fetch('/refresh', {
                method: 'POST',
                credentials: 'include',
                headers: { Accept: 'application/json' }
            });
            if (!refreshResponse.ok) {
                window.location.replace('/login');
                return;
            }
            response = await fetch(section.dataset.endpoint, options);
        }

        if (response.status === 401) {
            window.location.replace('/login');
            return;
        }

        if (response.status === 403) {
            window.location.replace('/');
            return;
        }

        if (!response.ok) {
            emptyState.textContent = 'Не удалось загрузить данные. Попробуйте позже.';
            return;
        }

        const items = await response.json();
        if (!Array.isArray(items)) {
            emptyState.textContent = 'Не удалось загрузить данные. Попробуйте позже.';
            return;
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
    } catch (_error) {
        emptyState.textContent = 'Не удалось загрузить данные. Попробуйте обновить страницу.';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-dashboard-section]').forEach(loadDashboardSection);
});
