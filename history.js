// Historical Data JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set default year
    const yearSelect = document.getElementById('year');
    if (yearSelect) {
        yearSelect.value = '2023';
    }
    
    // Load locations
    loadLocations();
    
    // Event listeners
    const loadHistoryBtn = document.getElementById('loadHistoryBtn');
    if (loadHistoryBtn) {
        loadHistoryBtn.addEventListener('click', loadHistoricalData);
    }
});

function loadLocations() {
    const locationSelect = document.getElementById('location');
    if (!locationSelect) return;
    
    const locationsData = document.getElementById('locations-data');
    if (!locationsData) return;
    
    try {
        const locations = JSON.parse(locationsData.value);
        
        locationSelect.innerHTML = '<option value="">Choose a district...</option>';
        
        Object.keys(locations).sort().forEach(location => {
            const option = document.createElement('option');
            option.value = location;
            option.textContent = location;
            locationSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

async function loadHistoricalData() {
    const location = document.getElementById('location').value;
    const year = document.getElementById('year').value;
    
    if (!location || !year) {
        showAlert('Please select both location and year', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/get_historical_trends', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ location, year })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateHistoricalStats(data.trends);
            updateHistoricalCharts(data.trends);
            updateHistoricalTable(data.trends);
            showAlert('Historical data loaded successfully!', 'success');
        } else {
            showAlert(data.error || 'Error loading historical data', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error connecting to server', 'error');
    } finally {
        showLoading(false);
    }
}

function updateHistoricalStats(trends) {
    // Calculate statistics from monthly data
    let totalRainfall = 0;
    let totalTemp = 0;
    let totalWind = 0;
    let maxRainfall = 0;
    let count = 0;
    
    Object.values(trends).forEach(month => {
        totalRainfall += month.rainfall || 0;
        totalTemp += month.temperature || 0;
        totalWind += month.wind_speed || 0;
        maxRainfall = Math.max(maxRainfall, month.rainfall || 0);
        count++;
    });
    
    const annualRainfall = document.getElementById('annualRainfall');
    if (annualRainfall) {
        annualRainfall.textContent = `${totalRainfall.toFixed(1)} mm`;
    }
    
    const avgTemp = document.getElementById('avgTempHistorical');
    if (avgTemp) {
        avgTemp.textContent = `${(totalTemp / count).toFixed(1)}°C`;
    }
    
    const avgWind = document.getElementById('avgWindHistorical');
    if (avgWind) {
        avgWind.textContent = `${(totalWind / count).toFixed(1)} km/h`;
    }
    
    const maxRainfallEl = document.getElementById('maxRainfall');
    if (maxRainfallEl) {
        maxRainfallEl.textContent = `${maxRainfall.toFixed(1)} mm`;
    }
}

function updateHistoricalCharts(trends) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const rainfallData = [];
    const tempData = [];
    
    // Populate data for all months
    months.forEach((_, index) => {
        const month = index + 1;
        if (trends[month]) {
            rainfallData.push(trends[month].rainfall || 0);
            tempData.push(trends[month].temperature || 0);
        } else {
            rainfallData.push(0);
            tempData.push(0);
        }
    });
    
    // Monthly Rainfall Chart
    const rainfallCtx = document.getElementById('monthlyRainfallChart');
    if (rainfallCtx) {
        if (window.monthlyRainfallChart) {
            window.monthlyRainfallChart.destroy();
        }
        
        window.monthlyRainfallChart = new Chart(rainfallCtx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [{
                    label: 'Rainfall (mm)',
                    data: rainfallData,
                    backgroundColor: 'rgba(37, 99, 235, 0.5)',
                    borderColor: 'rgb(37, 99, 235)',
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
    
    // Monthly Temperature Chart
    const tempCtx = document.getElementById('monthlyTempChart');
    if (tempCtx) {
        if (window.monthlyTempChart) {
            window.monthlyTempChart.destroy();
        }
        
        window.monthlyTempChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Temperature (°C)',
                    data: tempData,
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderColor: 'rgb(245, 158, 11)',
                    borderWidth: 2,
                    tension: 0.3,
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

function updateHistoricalTable(trends) {
    const tableBody = document.getElementById('historicalTableBody');
    if (!tableBody) return;
    
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    
    let html = '';
    
    months.forEach((month, index) => {
        const monthNum = index + 1;
        const data = trends[monthNum] || {};
        
        html += `
            <tr>
                <td>${month}</td>
                <td>${(data.rainfall || 0).toFixed(1)} mm</td>
                <td>${(data.temperature || 0).toFixed(1)}°C</td>
                <td>${(data.humidity || 0).toFixed(0)}%</td>
                <td>${(data.wind_speed || 0).toFixed(1)} km/h</td>
                <td>${data.wind_direction || '--'}</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

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

function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}