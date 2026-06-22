// Global variables
let rainfallChart = null;
let tempChart = null;
let windChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Load locations
    loadLocations();
    
    // Event listeners
    const predictBtn = document.getElementById('predictBtn');
    if (predictBtn) {
        predictBtn.addEventListener('click', getWeatherData);
    }
    
    const batchPredictBtn = document.getElementById('batchPredictBtn');
    if (batchPredictBtn) {
        batchPredictBtn.addEventListener('click', getWeeklyForecast);
    }
});

// Load locations into dropdown
function loadLocations() {
    const locationSelect = document.getElementById('location');
    if (!locationSelect) return;
    
    // Clear existing options
    locationSelect.innerHTML = '<option value="">Select Location</option>';
    
    // Add locations from data attribute
    const locations = JSON.parse(document.getElementById('locations-data').value);
    
    Object.keys(locations).forEach(location => {
        const option = document.createElement('option');
        option.value = location;
        option.textContent = location;
        locationSelect.appendChild(option);
    });
}

// Get weather data for selected location and date
async function getWeatherData() {
    const location = document.getElementById('location').value;
    const date = document.getElementById('date').value;
    
    if (!location || !date) {
        showAlert('Please select location and date', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/get_weather_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location, date })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateWeatherCards(data);
            updateStatistics(data);
            updateCharts(data);
            showAlert('Weather data loaded successfully!', 'success');
        } else {
            showAlert(data.error || 'Error fetching weather data', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error connecting to server', 'error');
    } finally {
        showLoading(false);
    }
}

// Update weather cards with data
function updateWeatherCards(data) {
    // Past weather card
    updateWeatherCard('past', data.past);
    
    // Present weather card
    updateWeatherCard('present', data.present);
    
    // Future weather card
    updateWeatherCard('future', data.future);
}

function updateWeatherCard(period, weatherData) {
    const card = document.querySelector(`.weather-card.${period}`);
    if (!card || !weatherData) return;
    
    // Update rainfall
    const rainfallEl = card.querySelector('.rainfall-value');
    if (rainfallEl) {
        rainfallEl.textContent = `${weatherData.rainfall.toFixed(1)} mm`;
    }
    
    // Update rainfall category
    const categoryEl = card.querySelector('.rainfall-category');
    if (categoryEl) {
        const category = getRainfallCategory(weatherData.rainfall);
        categoryEl.textContent = category;
        categoryEl.className = `rainfall-category category-${category.toLowerCase().replace(' ', '-')}`;
    }
    
    // Update wind information
    const windDirectionEl = card.querySelector('.wind-direction');
    if (windDirectionEl) {
        windDirectionEl.textContent = weatherData.wind_direction;
    }
    
    const windSpeedEl = card.querySelector('.wind-speed');
    if (windSpeedEl) {
        windSpeedEl.textContent = `${weatherData.wind_speed} km/h`;
    }
    
    // Update wind arrow
    const windArrow = card.querySelector('.wind-arrow i');
    if (windArrow) {
        const rotation = getWindDirectionRotation(weatherData.wind_direction);
        windArrow.style.transform = `rotate(${rotation}deg)`;
    }
}

// Get rainfall category based on mm
function getRainfallCategory(rainfall) {
    if (rainfall === 0) return 'No Rain';
    if (rainfall < 2.5) return 'Light';
    if (rainfall < 7.6) return 'Moderate';
    return 'Heavy';
}

// Get wind direction rotation for arrow
function getWindDirectionRotation(direction) {
    const directions = {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    };
    return directions[direction] || 0;
}

// Update statistics cards
function updateStatistics(data) {
    const stats = {
        'avg-temperature': calculateAverage([data.past.temperature, data.present.temperature, data.future.temperature]),
        'avg-humidity': calculateAverage([data.past.humidity, data.present.humidity, data.future.humidity]),
        'avg-pressure': calculateAverage([data.past.pressure, data.present.pressure, data.future.pressure]),
        'total-rainfall': (data.past.rainfall + data.present.rainfall + data.future.rainfall).toFixed(1)
    };
    
    Object.keys(stats).forEach(key => {
        const el = document.getElementById(key);
        if (el) {
            if (key.includes('temperature')) {
                el.textContent = `${stats[key].toFixed(1)}°C`;
            } else if (key.includes('humidity')) {
                el.textContent = `${stats[key].toFixed(0)}%`;
            } else if (key.includes('pressure')) {
                el.textContent = `${stats[key].toFixed(0)} hPa`;
            } else if (key.includes('rainfall')) {
                el.textContent = `${stats[key]} mm`;
            }
        }
    });
}

// Calculate average
function calculateAverage(values) {
    return values.reduce((a, b) => a + b, 0) / values.length;
}

// Update charts
function updateCharts(data) {
    // Rainfall comparison chart
    const rainfallCtx = document.getElementById('rainfallChart');
    if (rainfallCtx) {
        if (rainfallChart) rainfallChart.destroy();
        
        rainfallChart = new Chart(rainfallCtx, {
            type: 'bar',
            data: {
                labels: ['Past', 'Present', 'Future'],
                datasets: [{
                    label: 'Rainfall (mm)',
                    data: [data.past.rainfall, data.present.rainfall, data.future.rainfall],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.5)',
                        'rgba(16, 185, 129, 0.5)',
                        'rgba(245, 158, 11, 0.5)'
                    ],
                    borderColor: [
                        'rgb(59, 130, 246)',
                        'rgb(16, 185, 129)',
                        'rgb(245, 158, 11)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#f8fafc' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // Temperature trends chart
    const tempCtx = document.getElementById('tempChart');
    if (tempCtx) {
        if (tempChart) tempChart.destroy();
        
        tempChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: ['Past', 'Present', 'Future'],
                datasets: [{
                    label: 'Temperature (°C)',
                    data: [data.past.temperature, data.present.temperature, data.future.temperature],
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#f8fafc' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }
}

// Get weekly forecast
async function getWeeklyForecast() {
    const location = document.getElementById('location').value;
    const days = document.getElementById('forecast-days').value;
    
    if (!location) {
        showAlert('Please select a location', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/predict_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location, days })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayWeeklyForecast(data.predictions);
        } else {
            showAlert(data.error || 'Error generating forecast', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error connecting to server', 'error');
    } finally {
        showLoading(false);
    }
}

// Display weekly forecast
function displayWeeklyForecast(predictions) {
    const forecastContainer = document.getElementById('forecast-container');
    if (!forecastContainer) return;
    
    let html = '<h3>Weekly Weather Forecast</h3><div class="forecast-grid">';
    
    predictions.forEach((pred, index) => {
        const date = pred.date ? new Date(`${pred.date}T00:00:00`) : new Date();
        if (!pred.date) {
            date.setDate(date.getDate() + index);
        }
        
        html += `
            <div class="forecast-card">
                <div class="forecast-date">${date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</div>
                <div class="forecast-rainfall">${pred.rainfall.toFixed(1)} mm</div>
                <span class="rainfall-category category-${getRainfallCategory(pred.rainfall).toLowerCase().replace(' ', '-')}">
                    ${getRainfallCategory(pred.rainfall)}
                </span>
                <div class="forecast-wind">
                    <i class="fas fa-location-arrow" style="transform: rotate(${getWindDirectionRotation(pred.wind_direction)}deg)"></i>
                    ${pred.wind_direction} ${pred.wind_speed} km/h
                </div>
                <div class="forecast-temp">${pred.temperature.toFixed(1)}°C</div>
            </div>
        `;
    });
    
    html += '</div>';
    forecastContainer.innerHTML = html;
}

// Show/hide loading spinner
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        ${message}
    `;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
