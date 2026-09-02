// Timezone offsets mapping
const timezoneOffsets = {
    'UTC+0': 0,
    'UTC+1': 1,
    'UTC+2': 2,
    'UTC+3': 3,
    'UTC+4': 4,
    'UTC+5': 5,
    'UTC+6': 6,
    'UTC+7': 7,
    'UTC+8': 8,
    'UTC+9': 9,
    'UTC+10': 10,
    'UTC+11': 11,
    'UTC+12': 12,
    'UTC-1': -1,
    'UTC-2': -2,
    'UTC-3': -3,
    'UTC-4': -4,
    'UTC-5': -5,
    'UTC-6': -6,
    'UTC-7': -7,
    'UTC-8': -8,
    'UTC-9': -9,
    'UTC-10': -10,
    'UTC-11': -11,
    'UTC-12': -12,
};

const daysOfWeek = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'];

const workDays = [0, 1, 2, 3, 4, 5]
const baseMinute = 9 * 60; // Start from 9 AM
const endMinute = 21 * 60; // End at 9 PM
const baseTimeZone = 'UTC+1'
const stepMinutes = 60;

// Store selected slots with original times (in UTC+1)
let selectedSlots = [];
let studentTimeZone = 'UTC+1';

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const scheduleTimezoneSelect = document.getElementById('scheduleTimezone');
    // ensure timezone selector resets to default on load (avoid browser autocomplete retention)
    scheduleTimezoneSelect.value = studentTimeZone;
    const submitBtn = document.getElementById('submitBtn');
    
    // Generate initial schedule (value already set above)
    generateSchedule(studentTimeZone);
    
    // Handle timezone change
    scheduleTimezoneSelect.addEventListener('change', function(e) {
        studentTimeZone = e.target.value;
        generateSchedule(studentTimeZone);
        updateSelectedSlotsDisplay();
    });
    
    // Handle submit button
    submitBtn.addEventListener('click', function() {
        const studentInfo = document.getElementById('studentInfo').value;
        const contactTelegram = document.getElementById('contactTelegram').value;
        const contactWhatsapp = document.getElementById('contactWhatsapp').value;
        const contactEmail = document.getElementById('contactEmail').value;
        const successModal = document.getElementById('successModal');
        
        // Validate inputs
        if (selectedSlots.length === 0) {
            alert('Пожалуйста, выберите хотя бы один период времени');
            return;
        }
        
        if (!studentInfo.trim()) {
            alert('Пожалуйста, расскажите о себе');
            return;
        }
        
        // Log to console
        logSubmission(selectedSlots, studentInfo, {
            telegram: contactTelegram,
            whatsapp: contactWhatsapp,
            email: contactEmail
        });
        
        // Clear selection
        clearForm();
        
        // Show success modal
        successModal.classList.remove('hidden');
        
        // Hide modal after 5 seconds
        setTimeout(() => {
            successModal.classList.add('hidden');
        }, 5000);
    });
});

function getTimeInTimeZone(hour, dayIndex, targetTimeZone, baseTimeZone) {
    let day = dayIndex;
    if (typeof hour === "string") {
        hour = Number(hour);
    }
    if (typeof day === "string") {
        day = Number(day);
    }
    if (typeof targetTimeZone === "string") {
        var targetOffset = timezoneOffsets[targetTimeZone];
    } else {
        var targetOffset =  targetTimeZone;
    }
    if (typeof baseTimeZone === "string") {
        var baseOffset = timezoneOffsets[baseTimeZone];
    } else {
        var baseOffset = baseTimeZone;
    }
    
    const offset = targetOffset - baseOffset;
    let newHour = hour + offset;

    if (newHour >= 24) {day++; newHour -= 24;};
    if (newHour < 0) {day--; newHour += 24;};

    if (day > 6) { day = day - 7;};
    if (day < 0) { day = day + 7;};
    
    return {'hour' : newHour, 'dayIndex' : day};
}

function createDayColumn (i) {
        const dayColumn = document.createElement('div');
        dayColumn.className = `day-column ${String(i)}}`;
        
        const dayName = document.createElement('h3');
        dayName.className = 'day-name';
        dayName.textContent = daysOfWeek[i];
        dayColumn.appendChild(dayName);
        
        const timeSlotsContainer = document.createElement('div');
        timeSlotsContainer.className = 'time-slots';

        dayColumn.appendChild(timeSlotsContainer);
        
        return dayColumn;
}

// Generate schedule with time conversion
function generateSchedule(timezone) {
    const scheduleGrid = document.getElementById('scheduleGrid');
    const timezoneInfo = document.getElementById('timezoneInfo');
    const offset = timezoneOffsets[timezone];
    
    timezoneInfo.textContent = `⏰ Время указано по ${timezone}`;
    
    scheduleGrid.innerHTML = '';

    var DayColumns = Array.from({ length: 7 }, (_, i) => createDayColumn(i));
    
    workDays.forEach(dayIndex => {
        for (let currentMinute = baseMinute; currentMinute < endMinute; currentMinute += stepMinutes) {
            const hour =  Math.trunc(currentMinute / 60);
            const minutes = currentMinute - hour * 60;
            const timeInStudentZone = getTimeInTimeZone(hour, dayIndex, timezone, baseTimeZone);
            
            const currentTileTime = `${String(timeInStudentZone.hour)}:${String(minutes).padStart(2, '0')}`;

            const button = document.createElement('button');
            button.className = 'time-slot';
            button.setAttribute('data-day', dayIndex);
            button.setAttribute('data-time-baseTimeZone-hour', hour);
            button.setAttribute('data-time-baseTimeZone-minutes', minutes);
            button.textContent = currentTileTime;

            // Check if this slot is selected``
            if (selectedSlots.includes(`${dayIndex}-${hour}-${minutes}`)) {
                button.classList.add('selected');
            }

            button.addEventListener('click', function(e) {
                // if (button.disabled) return;
                e.preventDefault();
                handleTimeSlotClick(dayIndex, hour, minutes, button);
            });

            DayColumns[timeInStudentZone.dayIndex].querySelector('.time-slots').appendChild(button);
        }
    });

    daysOfWeek.forEach((day,i) => {
        if (DayColumns[i].querySelector('.time-slot') !== null) {
            scheduleGrid.appendChild(DayColumns[i]);
        }
    });
}

function handleTimeSlotClick(dayIndex, hour, minutes, buttonElement) {
    const slotId = `${dayIndex}-${hour}-${minutes}`;
    
    if (buttonElement.classList.contains('selected')) {
        buttonElement.classList.remove('selected');
        selectedSlots = selectedSlots.filter(slot => slot !== slotId);
    } else {
        buttonElement.classList.add('selected');
        selectedSlots.push(slotId);
    }
    
    updateSelectedSlotsDisplay();
}

// Remove slot from selected
function removeSlot(slotId) {
    selectedSlots = selectedSlots.filter(slot => slot !== slotId);
    
    // Unselect the button
    const [dayIndex, hour, minutes] = slotId.split('-');
    const buttons = document.querySelectorAll(`.time-slot[data-day="${dayIndex}"][data-time-baseTimeZone-hour="${hour}"][data-time-baseTimeZone-minutes="${minutes}"]`);
    buttons.forEach(btn => btn.classList.remove('selected'));
    
    updateSelectedSlotsDisplay();
}

// Update selected slots display
function updateSelectedSlotsDisplay() {
    const displayContainer = document.getElementById('selectedSlotsList');
    
    if (selectedSlots.length === 0) {
        displayContainer.innerHTML = '<p class="no-selection">Выберите время выше</p>';
        return;
    }
    
    const slotsHTML = selectedSlots.map(slot => {
        const [dayIndex, hour, minutes] = slot.split('-');
        const timeInStudentZone = getTimeInTimeZone(hour, dayIndex, studentTimeZone, baseTimeZone);
        return `<span class="selected-slot-tag">
                    ${daysOfWeek[timeInStudentZone.dayIndex]} ${String(timeInStudentZone.hour).padStart(2, '0')}:${minutes.padStart(2, '0')}
                    <button class="remove-slot-btn" onclick="removeSlot('${slot}')">×</button>
                </span>`;
    }).join('');
    
    displayContainer.innerHTML = slotsHTML;
}

// Log submission to console
function logSubmission(slots, studentInfo, contacts) {
    const submissionTimezoneOffset = timezoneOffsets[studentTimeZone];
    const nowUTC = new Date();
    const orderTimeUTC = nowUTC.toISOString();

    // build takenTimes array (day, time as shown to student in current schedule timezone)
    const takenTimes = slots.map(slot => {
        const [dayIndex, hour, minutes] = slot.split('-');
        const timeInStudentZone = getTimeInTimeZone(hour, dayIndex, studentTimeZone, baseTimeZone);
        return { "dayIndexBase": dayIndex , "timeHourBase": hour, "timeMinutesBase": minutes, "dayIndexStudent": timeInStudentZone.dayIndex , "timeHourStudent": timeInStudentZone.hour };
    });

    const result = {
        StudentTimeZone: studentTimeZone,
        takenTimes,
        StudentInfo: studentInfo,
        orderTimeUTC: orderTimeUTC,
        contacts: {
            telegram: contacts.telegram,
            whatsapp: contacts.whatsapp,
            email: contacts.email
        }
    };

    console.log(result);
}


// Clear form
function clearForm() {
    // Clear time slot selections
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    
    // Clear text input
    document.getElementById('studentInfo').value = '';
    
    // Clear selected slots array
    selectedSlots = [];
    
    // Update display
    updateSelectedSlotsDisplay();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


// disable if displayed day invalid or mapping back violates schedule
// if (!isValidDay || !isBaseValid) {
//     button.disabled = true;
//     button.classList.add('disabled-slot');
// }